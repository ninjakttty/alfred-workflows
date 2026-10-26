# Pad

The Pad Alfred workflow controls a small floating note for macOS. The bundled application and CLI retain the internal name Scratchpad, preserving existing note storage. Requires macOS 13 or later and Xcode or Apple's Swift command line tools to build. No dependencies, Dock icon, menu bar item, network access, or background services.

## Build and install

From this repository:

```sh
./pad/scripts/build-install.sh
"$HOME/.local/bin/scratchpad" show
```

The script runs tests, builds for your Mac's architecture, and bundles the ad-hoc signed app at `workflow/.scratchpad/Scratchpad.app`. It exports the complete `pad.alfredworkflow`, including the executable and launcher. If this workflow is already installed in Alfred's default preferences location, the script updates it and installs a `~/.local/bin/scratchpad` dispatcher that finds the current workflow after reinstalls. Otherwise, open the exported workflow to import it. For synced preferences, pass the existing workflow directory as the script's first argument. Quit Scratchpad before rebuilding. Open `Package.swift` in Xcode to work on the source. No app is installed in `~/Applications`; the hidden workflow folder keeps the app out of normal application search results.

## Use

```sh
"$HOME/.local/bin/scratchpad" toggle
"$HOME/.local/bin/scratchpad" show
"$HOME/.local/bin/scratchpad" hide
"$HOME/.local/bin/scratchpad" quit
```

No argument means `toggle`. Optionally add `~/.local/bin` to your shell's PATH to use `scratchpad` directly. `show` and `toggle` launch the app if necessary and focus the editor. Escape or the close button saves and hides the window. The app remains running. Command-Q while editing, or the CLI `quit`, saves and exits. Resize or drag the title bar normally. The panel floats above ordinary windows and joins Spaces, including as an auxiliary window in fullscreen Spaces; macOS system/security surfaces can cover it.

Launch the note through the CLI or Alfred. Opening the app bundle alone starts it hidden. Reopen events deliberately do not show it: Launch Services may deliver a reopen alongside a URL, and letting both change visibility would break toggle reliability.

## Alfred

Requires Alfred with Powerpack. Open `pad.alfredworkflow` to import the self-contained workflow. No separate app installation is needed. Alfred may import it as Uncategorised: choose Productivity in the import dialog, or right-click Pad → Category → Productivity afterwards. The category is a local Alfred organisational setting. The bundled build targets the architecture of the Mac that built it. Keywords:

- `pad`: toggle
- `pad-show`: show and focus
- `pad-hide`: save and hide

For your own hotkey or keyword workflow, connect it to a Run Script action, language `/bin/zsh`, with this exact command:

```sh
exec ./scratchpad toggle
```

This command runs from inside the Scratchpad workflow directory. For a different workflow, use the optional `~/.local/bin/scratchpad` dispatcher created by the installer instead. Use `show`, `hide`, or `quit` instead as needed. No shell PATH setup is required. The included workflow also exposes external triggers `toggle`, `show`, and `hide` under `net.ninjakitty.pad`.

## Persistence and architecture

One `NSPanel` contains an `NSScrollView` and plain `NSTextView`. Its floating level and `hidesOnDeactivate = false` keep it visible when another app is active. Each edit synchronously writes UTF-8 atomically to:

```text
~/Library/Application Support/net.ninjakitty.scratchpad/note.txt
```

There is no debounce or pending write queue. Escape, close, and normal termination save again before proceeding. A storage failure displays an error and refuses to hide or quit, retaining the in-memory text. An unreadable existing note is never treated as a blank note or overwritten. Quit, repair file access/encoding, then launch again. No application can guarantee persistence through hardware failure, forced termination during an edit, or an unwritable disk; successful edits have no intentionally delayed unsaved interval. Atomic replacement protects the previous file if replacement fails. Do not edit the file externally while Scratchpad runs: external changes are not monitored.

Window frame and cursor offset are stored in the app's UserDefaults; cursor offset is restored on the next launch and selection is retained in memory while hidden. Offscreen windows are centered when no screen intersects them.

The shell CLI validates commands and uses `/usr/bin/open -g -a` with the workflow-private bundle's absolute path and `ninjakitty-scratchpad://toggle` (or the other commands). Launch Services delivers URL events to the existing app or launches it. The app queues early URL events until its note and panel are ready; it never shows unconditionally during launch. Only the app reads `panel.isVisible`, so a visible panel in an inactive app still toggles off. Before opening the bundle, the launcher checks for an instance from a different workflow path, which can survive uninstalling a hidden workflow. It requests a normal save-and-quit and waits up to five seconds before launching the current copy; it aborts if the previous instance cannot quit safely. A process-lifetime advisory lock also prevents a second directly launched binary from editing the same file. Commands are asynchronous: CLI success means Launch Services accepted the request, not a save acknowledgement. `hide` or `quit` on a stopped app may briefly launch it to process the command; neither displays the editor.

## Testing and troubleshooting

```sh
cd pad
swift test
```

Tests exercise Unicode, empty and replacement saves, missing files, invalid UTF-8, write failure preservation, URL validation, and visibility transitions. For integration checks: cold toggle, type text and Escape, reopen and check focus/text/caret, focus Finder and toggle the still-visible panel, resize/move, quit and relaunch, and verify the saved note and geometry. Test Alfred using its keywords or external triggers, not just direct shell commands.

If a command does nothing, run it in Terminal and inspect stderr. Confirm the workflow contains `scratchpad` and `.scratchpad/Scratchpad.app`. Rebuild or reimport the workflow if either is missing. The launcher resolves its own location, including through the optional CLI dispatcher; it does not depend on a fixed workflow UUID. Do not use `open -n`, run the bare executable, or move the app out of its workflow folder. If a second executable immediately exits, the first instance holds the note lock. The lock file can remain after quit; the kernel releases the lock automatically, so deleting it is unnecessary and unsafe while running.

A build is local and ad-hoc signed, not notarized for distribution. Rebuild on each target Mac. To uninstall, quit first, remove the Alfred workflow and optional CLI dispatcher. Keep the Application Support directory to retain your note.

Author: Yuri Parsons · https://www.ninjakitty.net
