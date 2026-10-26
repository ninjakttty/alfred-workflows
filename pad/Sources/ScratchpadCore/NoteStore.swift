import Foundation

public enum Command: String, CaseIterable {
    case toggle, show, hide, quit
    public init?(url: URL) {
        guard url.scheme == "ninjakitty-scratchpad", url.path.isEmpty,
              url.query == nil, url.fragment == nil, let host = url.host else { return nil }
        self.init(rawValue: host)
    }
    public func visibility(current: Bool) -> Bool {
        switch self { case .toggle: return !current; case .show: return true; case .hide, .quit: return false }
    }
}

public final class NoteStore {
    public let url: URL
    public init(url: URL) { self.url = url }
    public func load() throws -> String {
        do { return try String(contentsOf: url, encoding: .utf8) }
        catch let error as NSError where error.domain == NSCocoaErrorDomain && error.code == NSFileReadNoSuchFileError { return "" }
    }
    public func save(_ text: String) throws {
        try FileManager.default.createDirectory(at: url.deletingLastPathComponent(), withIntermediateDirectories: true, attributes: [.posixPermissions: 0o700])
        try Data(text.utf8).write(to: url, options: [.atomic])
        try FileManager.default.setAttributes([.posixPermissions: 0o600], ofItemAtPath: url.path)
    }
}
