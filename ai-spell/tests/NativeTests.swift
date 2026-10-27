import Foundation

@main
struct NativeTests {
    static func main() throws {
        let normalized = normalizedSuggestions([
            Suggestion(word: " Hello ", definition: " greeting "),
            Suggestion(word: "ＨＥＬＬＯ", definition: "duplicate"),
            Suggestion(word: "", definition: "invalid"),
            Suggestion(word: "help", definition: "assist"),
            Suggestion(word: "halo", definition: "ring"),
            Suggestion(word: "fourth", definition: "skip")
        ])
        precondition(normalized == [Suggestion(word: "Hello", definition: "greeting"), Suggestion(word: "help", definition: "assist"), Suggestion(word: "halo", definition: "ring")])
        precondition(safeID("../../outside") == nil)
        precondition(safeID(UUID().uuidString) != nil)
        let root = FileManager.default.temporaryDirectory.appendingPathComponent(UUID().uuidString)
        defer { try? FileManager.default.removeItem(at: root) }
        let store = try Store(root: root)
        let id = UUID().uuidString
        try FileManager.default.createDirectory(at: store.directory(id), withIntermediateDirectories: false)
        try store.touch(id)
        precondition(store.fresh(id))
        precondition(!store.fresh(id, now: Date().addingTimeInterval(4)))
        try store.write(Data(id.utf8), to: root.appendingPathComponent("active"))
        precondition(store.active(id))
        precondition(!store.active(UUID().uuidString))
        let state = RequestState(digest: digest("heelo"), status: "ready", suggestions: normalized)
        try store.save(state, id: id)
        let restored = try store.load(id)
        precondition(restored.suggestions == normalized)
        let loading = feedback(RequestState(digest: "", status: "loading"), id: id)
        precondition(loading["rerun"] as? Double == 0.25)
        let ready = feedback(state, id: id)
        precondition(ready["rerun"] == nil)
        precondition((ready["items"] as? [[String: Any]])?.first?["arg"] as? String == "Hello")
        let empty = try filter("", store: store)
        precondition((empty["items"] as? [[String: Any]])?.first?["valid"] as? Bool == false)
        precondition(!store.active(id))
        print("Native normalization, request isolation, leases, and feedback checks passed.")
    }
}
