import AppKit
import ScratchpadCore
import Darwin

final class Panel: NSPanel {
    var dismiss: (() -> Void)?
    override var canBecomeKey: Bool { true }
    override func cancelOperation(_ sender: Any?) { dismiss?() }
}
final class Editor: NSTextView {
    var dismiss: (() -> Void)?
    override func keyDown(with event: NSEvent) {
        if event.keyCode == 53 { dismiss?(); return }
        super.keyDown(with: event)
    }
}
final class Delegate: NSObject, NSApplicationDelegate, NSTextViewDelegate, NSWindowDelegate {
    let store = NoteStore(url: FileManager.default.urls(for: .applicationSupportDirectory, in: .userDomainMask)[0].appendingPathComponent("net.ninjakitty.scratchpad/note.txt"))
    let panel = Panel(contentRect: NSRect(x: 240, y: 240, width: 420, height: 320), styleMask: [.titled, .closable, .resizable, .utilityWindow], backing: .buffered, defer: false)
    let editor = Editor()
    var loaded = false
    var pending: [Command] = []
    var lockFD: Int32 = -1
    func applicationWillFinishLaunching(_ notification: Notification) {
        // A process-lifetime lock also guards accidental direct executable launches.
        let dir = store.url.deletingLastPathComponent()
        do { try FileManager.default.createDirectory(at: dir, withIntermediateDirectories: true, attributes: [.posixPermissions: 0o700]) }
        catch { fatalError("Cannot create note directory: \(error)") }
        lockFD = open(dir.appendingPathComponent("instance.lock").path, O_CREAT | O_RDWR, 0o600)
        guard lockFD >= 0, flock(lockFD, LOCK_EX | LOCK_NB) == 0 else { exit(0) }
    }
    func applicationDidFinishLaunching(_ notification: Notification) {
        NSApp.setActivationPolicy(.accessory)
        let menu = NSMenu()
        let item = NSMenuItem(); menu.addItem(item)
        let appMenu = NSMenu(); item.submenu = appMenu
        appMenu.addItem(withTitle: "Quit Scratchpad", action: #selector(NSApplication.terminate(_:)), keyEquivalent: "q")
        let editItem = NSMenuItem(); menu.addItem(editItem)
        let editMenu = NSMenu(title: "Edit"); editItem.submenu = editMenu
        for (title, action, key) in [("Undo", "undo:", "z"), ("Redo", "redo:", "Z"), ("Cut", "cut:", "x"), ("Copy", "copy:", "c"), ("Paste", "paste:", "v"), ("Select All", "selectAll:", "a")] {
            editMenu.addItem(withTitle: title, action: Selector(action), keyEquivalent: key)
        }
        NSApp.mainMenu = menu
        panel.title = "Scratchpad"
        panel.level = .floating
        panel.hidesOnDeactivate = false
        panel.isReleasedWhenClosed = false
        panel.collectionBehavior = [.canJoinAllSpaces, .fullScreenAuxiliary]
        panel.minSize = NSSize(width: 240, height: 160)
        panel.delegate = self
        panel.setFrameAutosaveName("ScratchpadPanel")
        if !NSScreen.screens.contains(where: { $0.visibleFrame.intersects(panel.frame) }) { panel.center() }
        let scroll = NSScrollView(frame: panel.contentView!.bounds)
        scroll.autoresizingMask = [.width, .height]
        scroll.hasVerticalScroller = true
        editor.frame = scroll.bounds
        editor.isRichText = false
        editor.allowsUndo = true
        editor.font = .monospacedSystemFont(ofSize: 14, weight: .regular)
        editor.textContainerInset = NSSize(width: 12, height: 12)
        editor.isVerticallyResizable = true
        editor.isHorizontallyResizable = false
        editor.autoresizingMask = [.width]
        editor.textContainer?.widthTracksTextView = true
        editor.textContainer?.containerSize = NSSize(width: scroll.contentSize.width, height: .greatestFiniteMagnitude)
        scroll.documentView = editor
        panel.contentView?.addSubview(scroll)
        do { editor.string = try store.load() }
        catch { showError(error); return }
        editor.delegate = self
        let selection = min(UserDefaults.standard.integer(forKey: "cursor"), (editor.string as NSString).length)
        editor.setSelectedRange(NSRange(location: max(0, selection), length: 0))
        editor.dismiss = { [weak self] in self?.hide() }
        panel.dismiss = editor.dismiss
        loaded = true
        let commands = pending; pending.removeAll()
        commands.forEach(handle)
        // URL commands are the sole initial presentation trigger: no launch/toggle race.
    }
    func application(_ application: NSApplication, open urls: [URL]) {
        for url in urls { if let command = Command(url: url) { if loaded { handle(command) } else { pending.append(command) } } }
    }
    func handle(_ command: Command) {
        if command == .quit { NSApp.terminate(nil); return }
        if command.visibility(current: panel.isVisible) {
            NSApp.activate(ignoringOtherApps: true)
            panel.makeKeyAndOrderFront(nil)
            panel.makeFirstResponder(editor)
        } else { hide() }
    }
    @discardableResult func flush() -> Bool {
        guard loaded else { return false }
        do {
            try store.save(editor.string)
            UserDefaults.standard.set(editor.selectedRange().location, forKey: "cursor")
            panel.saveFrame(usingName: "ScratchpadPanel")
            return true
        } catch { showError(error); return false }
    }
    func showError(_ error: Error) {
        NSApp.activate(ignoringOtherApps: true)
        let alert = NSAlert(error: error)
        alert.informativeText += "\nThe note remains in memory. Resolve the storage problem and try again."
        alert.runModal()
    }
    func hide() { if flush() { panel.orderOut(nil) } }
    func textDidChange(_ notification: Notification) { flush() }
    func windowShouldClose(_ sender: NSWindow) -> Bool { hide(); return false }
    func applicationShouldTerminate(_ sender: NSApplication) -> NSApplication.TerminateReply { (!loaded || flush()) ? .terminateNow : .terminateCancel }
    func applicationShouldTerminateAfterLastWindowClosed(_ sender: NSApplication) -> Bool { false }
    func applicationShouldHandleReopen(_ sender: NSApplication, hasVisibleWindows flag: Bool) -> Bool { return false }
}
// A workflow reinstall changes its path while an old hidden process may survive.
// Run this short native preflight before Launch Services opens the current bundle.
if CommandLine.arguments.count == 3 && CommandLine.arguments[1] == "--prepare-launch" {
    let desired = URL(fileURLWithPath: CommandLine.arguments[2]).resolvingSymlinksInPath().standardizedFileURL
    let previous = NSRunningApplication.runningApplications(withBundleIdentifier: "net.ninjakitty.scratchpad").filter {
        $0.processIdentifier != getpid() && $0.bundleURL?.resolvingSymlinksInPath().standardizedFileURL != desired
    }
    for application in previous { application.terminate() }
    let deadline = Date().addingTimeInterval(5)
    while previous.contains(where: { !$0.isTerminated }) && Date() < deadline {
        RunLoop.current.run(until: Date().addingTimeInterval(0.05))
    }
    if previous.contains(where: { !$0.isTerminated }) {
        fputs("Pad's previous instance could not quit safely. Resolve any save error, then retry.\n", stderr)
        exit(1)
    }
    exit(0)
}
let app = NSApplication.shared
let delegate = Delegate()
app.delegate = delegate
app.run()
