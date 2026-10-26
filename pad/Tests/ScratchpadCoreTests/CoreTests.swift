import XCTest
@testable import ScratchpadCore
final class CoreTests: XCTestCase {
    func testPersistence() throws {
        let dir = FileManager.default.temporaryDirectory.appendingPathComponent(UUID().uuidString)
        defer { try? FileManager.default.removeItem(at: dir) }
        let store = NoteStore(url: dir.appendingPathComponent("nested/note.txt"))
        XCTAssertEqual(try store.load(), "")
        for text in ["hello\n世界 🐱", "replacement", ""] {
            try store.save(text)
            XCTAssertEqual(try NoteStore(url: store.url).load(), text)
        }
    }
    func testUnreadableDataIsNotEmptyNote() throws {
        let url = FileManager.default.temporaryDirectory.appendingPathComponent(UUID().uuidString)
        defer { try? FileManager.default.removeItem(at: url) }
        try Data([0xff]).write(to: url)
        XCTAssertThrowsError(try NoteStore(url: url).load())
    }
    func testCommands() {
        for command in Command.allCases {
            XCTAssertEqual(Command(url: URL(string: "ninjakitty-scratchpad://\(command.rawValue)")!), command)
        }
        for invalid in ["https://toggle", "ninjakitty-scratchpad://unknown", "ninjakitty-scratchpad://show/path", "ninjakitty-scratchpad://show?q=1"] {
            XCTAssertNil(Command(url: URL(string: invalid)!))
        }
        XCTAssertFalse(Command.toggle.visibility(current: true))
        XCTAssertTrue(Command.toggle.visibility(current: false))
        for visible in [true, false] {
            XCTAssertTrue(Command.show.visibility(current: visible))
            XCTAssertFalse(Command.hide.visibility(current: visible))
        }
    }
    func testFailedWritePreservesExistingFile() throws {
        let dir = FileManager.default.temporaryDirectory.appendingPathComponent(UUID().uuidString)
        defer { try? FileManager.default.removeItem(at: dir) }
        try FileManager.default.createDirectory(at: dir, withIntermediateDirectories: true)
        let file = dir.appendingPathComponent("parent")
        try Data("original".utf8).write(to: file)
        XCTAssertThrowsError(try NoteStore(url: file.appendingPathComponent("note.txt")).save("new"))
        XCTAssertEqual(try String(contentsOf: file), "original")
    }
}
