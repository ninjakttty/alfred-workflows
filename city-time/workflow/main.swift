import Foundation
struct City: Codable { let city: String; let country: String; let zone: String; let aliases: String; let countryCode: String?
 var flag: String {
 guard let code = countryCode?.uppercased(), code.utf8.count == 2,
       code.utf8.allSatisfy({ $0 >= 65 && $0 <= 90 }) else { return "🌐" }
 return String(String.UnicodeScalarView(code.unicodeScalars.compactMap { UnicodeScalar(127397 + $0.value) }))
 }
}
func norm(_ s: String) -> String { s.folding(options: [.diacriticInsensitive, .caseInsensitive], locale: Locale(identifier: "en_US_POSIX")) }
let root = URL(fileURLWithPath: CommandLine.arguments[0]).deletingLastPathComponent()
do {
 let cities = try JSONDecoder().decode([City].self, from: Data(contentsOf: root.appendingPathComponent("cities.json")))
 var q = norm(CommandLine.arguments.dropFirst().joined(separator: " ").trimmingCharacters(in: .whitespacesAndNewlines))
 let conversionQuery = q
 let fromLocal = q.hasSuffix(" @local")
 if fromLocal { q = String(q.dropLast(7)).trimmingCharacters(in: .whitespaces) }
 var conversion: (hour: Int, minute: Int)? = nil
 let pattern = #"^(.*?)\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?$"#
 if let expression = try? NSRegularExpression(pattern: pattern),
    let match = expression.firstMatch(in: q, range: NSRange(q.startIndex..., in: q)) {
 func capture(_ index: Int) -> String { guard let range = Range(match.range(at: index), in: q) else { return "" }; return String(q[range]) }
 let cityQuery = capture(1), hour = Int(capture(2))!, minute = Int(capture(3)) ?? 0, meridiem = capture(4)
 if minute > 59 || (meridiem.isEmpty ? hour > 23 : hour < 1 || hour > 12) {
 let data = try JSONSerialization.data(withJSONObject: ["items": [["title": "Invalid time", "subtitle": "Use 3pm, 3:30pm, or 15:30", "valid": false]]])
 FileHandle.standardOutput.write(data); exit(0)
 }
 conversion = (meridiem.isEmpty ? hour : hour % 12 + (meridiem == "pm" ? 12 : 0), minute)
 q = cityQuery
 }
 let environment = ProcessInfo.processInfo.environment
 let use24Hour = ["1", "true", "yes"].contains(norm(environment["use_24_hour"] ?? "0"))
 let favourites = (environment["favourite_cities"] ?? "San Francisco\nDublin\nBerlin")
     .components(separatedBy: CharacterSet(charactersIn: "\n,;"))
     .map { $0.trimmingCharacters(in: .whitespacesAndNewlines) }.filter { !$0.isEmpty }
 func matchesEntry(_ city: City, _ entry: String) -> Bool {
 let parts = entry.components(separatedBy: "|").map { norm($0.trimmingCharacters(in: .whitespaces)) }
 return norm(city.city) == parts[0] && (parts.count == 1 || (parts.count == 2 && norm(city.zone) == parts[1]))
 }
 func isFavourite(_ city: City) -> Bool { favourites.contains { matchesEntry(city, $0) } }
 var favouriteIssues: [[String: Any]] = []
 var selected: [City]
 if q.isEmpty {
 selected = []
 var seen = Set<String>()
 for entry in favourites {
 let parts = entry.components(separatedBy: "|").map { norm($0.trimmingCharacters(in: .whitespaces)) }
 let matches = cities.filter { norm($0.city) == parts[0] && (parts.count == 1 || (parts.count == 2 && norm($0.zone) == parts[1])) }
 if matches.count == 1 {
 let city = matches[0], key = city.city + ":" + city.zone
 if seen.insert(key).inserted { selected.append(city) }
 } else {
 favouriteIssues.append(["title": matches.isEmpty ? "Unknown favourite: " + entry : "Ambiguous favourite: " + entry,
 "subtitle": "Edit Configure Workflow → Favourites; use City|Area/Zone to disambiguate", "valid": false])
 }
 }
 }
 else {
 let tokens = q.split(separator: " ").map(String.init)
 func score(_ c: City) -> Int { let n = norm(c.city); return n == q ? 0 : n.hasPrefix(q) ? 1 : n.contains(q) ? 2 : 3 }
 selected = cities.filter { c in let hay = norm(c.city + " " + c.country + " " + c.aliases); return tokens.allSatisfy { hay.contains($0) } }.sorted { a,b in let sa = score(a), sb = score(b); return sa == sb ? a.city < b.city : sa < sb }
 }
 let now = Date()
 let localOffset = TimeZone.current.secondsFromGMT(for: now)
 let time = DateFormatter(); time.locale = Locale(identifier: "en_US_POSIX"); time.dateFormat = use24Hour ? "HH:mm" : "h:mm a"
 let day = DateFormatter(); day.locale = Locale(identifier: "en_US_POSIX"); day.dateFormat = "EEE d MMM"
 var items: [[String: Any]] = []
 for c in (q.isEmpty ? selected : Array(selected.prefix(40))) {
 guard let tz = TimeZone(identifier: c.zone) else { continue }
 time.timeZone = tz; day.timeZone = tz
 if let wall = conversion {
 let sourceZone = fromLocal ? TimeZone.current : tz
 let destinationZone = fromLocal ? tz : TimeZone.current
 var calendar = Calendar(identifier: .gregorian); calendar.timeZone = sourceZone
 let start = calendar.startOfDay(for: now)
 let components = DateComponents(hour: wall.hour, minute: wall.minute, second: 0)
 guard let instant = calendar.nextDate(after: start.addingTimeInterval(-1), matching: components, matchingPolicy: .strict, repeatedTimePolicy: .first), calendar.isDate(instant, inSameDayAs: now) else {
 items.append(["title": "That time does not exist today in " + (fromLocal ? "your local time zone" : c.city), "subtitle": "The clocks skip this time during a daylight saving change. Choose another time.", "valid": false]); continue
 }
 let last = calendar.nextDate(after: start.addingTimeInterval(-1), matching: components, matchingPolicy: .strict, repeatedTimePolicy: .last)
 let repeated = last != nil && last != instant
 time.timeZone = sourceZone; let sourceTime = time.string(from: instant)
 time.timeZone = destinationZone; let destinationTime = time.string(from: instant)
 day.timeZone = sourceZone; let sourceDay = day.string(from: instant)
 day.timeZone = destinationZone; let destinationDay = day.string(from: instant)
 let sourceName = fromLocal ? "Local" : c.city
 let destinationName = fromLocal ? c.city : "Local"
 let title = sourceName + " " + sourceTime + " → " + destinationName + " " + destinationTime
 let reverseQuery = fromLocal ? String(conversionQuery.dropLast(7)) : conversionQuery + " @local"
 let subtitle = c.flag + " " + c.country + " · " + sourceDay + " → " + destinationDay + " · " + sourceZone.identifier + " → " + destinationZone.identifier + (repeated ? " · First occurrence of repeated time" : "")
 items.append(["uid": "convert:" + c.city + ":" + c.zone, "title": title, "subtitle": subtitle, "arg": destinationTime, "valid": true,
 "variables": ["clock_action": "copy"], "text": ["copy": destinationTime, "largetype": title],
 "mods": ["cmd": ["arg": title + " · " + subtitle, "subtitle": "Copy full conversion with dates"], "alt": ["arg": reverseQuery, "subtitle": "Switch direction: " + destinationName + " → " + sourceName, "variables": ["clock_action": "convert"], "valid": true]]])
 continue
 }
 let t = time.string(from: now), delta = tz.secondsFromGMT(for: now) - localOffset
 let minutes = abs(delta) / 60, hours = minutes / 60, remainder = minutes % 60
 var duration: [String] = []
 if hours > 0 { duration.append("\(hours) " + (hours == 1 ? "hour" : "hours")) }
 if remainder > 0 { duration.append("\(remainder) min") }
 let difference = delta == 0 ? "Same time as you" : duration.joined(separator: " ") + (delta > 0 ? " ahead of you" : " behind you")
 let saved = isFavourite(c)
 let updatedFavourites = saved ? favourites.filter { !matchesEntry(c, $0) } : favourites + [c.city + "|" + c.zone]
 items.append(["uid": c.city + ":" + c.zone, "title": c.city + "  ·  " + t, "subtitle": c.flag + " " + c.country + " · " + day.string(from: now) + " · " + difference, "arg": t, "valid": true, "variables": ["clock_action": "copy"], "text": ["copy": t, "largetype": t], "mods": ["cmd": ["arg": c.city + ": " + t, "subtitle": "Copy city and time"], "alt": ["variables": ["clock_action": "favourite"], "arg": updatedFavourites.joined(separator: "\n"), "subtitle": (saved ? "Remove " : "Add ") + c.city + (saved ? " from favourites" : " to favourites"), "valid": true]]])
 }
 // Without UIDs, Alfred cannot override the configured order with learned rankings.
 if q.isEmpty {
 items = items.map { item in var ordered = item; ordered.removeValue(forKey: "uid"); return ordered }
 items.append(contentsOf: favouriteIssues)
 }
 if items.isEmpty {
 items = [["title": q.isEmpty ? "No favourite cities" : "No matching cities",
 "subtitle": q.isEmpty ? "Search for a city, then press ⌥Enter to add it to favourites" : "Try a city, country, or time-zone name", "valid": false]]
 }
 let result: [String:Any] = ["items":items,"rerun": 30]
 let out = try JSONSerialization.data(withJSONObject: result, options: [.sortedKeys])
 FileHandle.standardOutput.write(out)
} catch {
 print("{\"items\":[{\"title\":\"Unable to load city index\",\"subtitle\":\"Reinstall Fast City Time\",\"valid\":false}]}")
}
