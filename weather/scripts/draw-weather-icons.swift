import AppKit
import ImageIO
import UniformTypeIdentifiers

let folder = URL(fileURLWithPath: CommandLine.arguments[1])
try FileManager.default.createDirectory(at: folder, withIntermediateDirectories: true)
let names = ["clear-day", "clear-night", "partly-cloudy-day", "partly-cloudy-night", "overcast", "fog", "drizzle", "rain", "snow", "thunderstorm"]
func emoji(_ text: String, _ x: Double, _ y: Double, _ size: Double, _ alpha: Double = 1) {
    NSGraphicsContext.saveGraphicsState()
    let image = NSImage(size: NSSize(width: 128, height: 128))
    image.lockFocus()
    (text as NSString).draw(at: NSPoint(x: x, y: y), withAttributes: [.font: NSFont.systemFont(ofSize: size), .foregroundColor: NSColor.white])
    image.unlockFocus()
    image.draw(in: NSRect(x: 0, y: 0, width: 128, height: 128), from: .zero, operation: .sourceOver, fraction: alpha)
    NSGraphicsContext.restoreGraphicsState()
}
func line(_ x: Double, _ y: Double, _ dx: Double, _ dy: Double, _ width: Double, _ color: NSColor) {
    color.setStroke()
    let path = NSBezierPath(); path.lineWidth = width; path.lineCapStyle = .round
    path.move(to: NSPoint(x: x, y: y)); path.line(to: NSPoint(x: x + dx, y: y + dy)); path.stroke()
}
for name in names {
    let output = folder.appendingPathComponent(name + ".gif")
    guard let destination = CGImageDestinationCreateWithURL(output as CFURL, UTType.gif.identifier as CFString, 24, nil) else { fatalError("Cannot create \(output)") }
    CGImageDestinationSetProperties(destination, [kCGImagePropertyGIFDictionary: [kCGImagePropertyGIFLoopCount: 0]] as CFDictionary)
    for frame in 0..<24 {
        let phase = Double(frame) / 24
        let wave = sin(phase * .pi * 2)
        let image = NSImage(size: NSSize(width: 128, height: 128)); image.lockFocus()
        NSColor.clear.setFill(); NSRect(x: 0, y: 0, width: 128, height: 128).fill(using: .copy)
        switch name {
        case "clear-day":
            emoji("☀️", 12 - wave, 8 - wave, 100 + wave * 2)
        case "clear-night":
            emoji("🌙", 12, 8, 100)
            emoji("✦", 78, 82 + wave * 2, 20, 0.7 + wave * 0.2)
        case "partly-cloudy-day":
            emoji("☀️", 45, 53, 64)
            emoji("☁️", 6 + wave * 3, 10, 88)
        case "partly-cloudy-night":
            emoji("🌙", 47, 53, 64)
            emoji("☁️", 6 + wave * 3, 10, 88)
        case "overcast":
            emoji("☁️", 10 + wave * 4, 9, 100)
        case "fog":
            emoji("☁️", 12, 34, 88, 0.8)
            for row in 0..<3 {
                let x = 20 + sin(phase * .pi * 2 + Double(row)) * 7
                line(x, 23 + Double(row) * 12, 82, 0, 5, NSColor(calibratedWhite: 0.82, alpha: 0.55))
            }
        case "drizzle", "rain", "snow", "thunderstorm":
            emoji("☁️", 10, 27, 89)
            if name == "thunderstorm" {
                // One slow, soft glow rather than a flashing screen.
                let glow = 0.55 + wave * 0.2
                NSColor(calibratedRed: 1, green: 0.78, blue: 0.28, alpha: glow).setFill()
                let bolt = NSBezierPath(); bolt.move(to: NSPoint(x: 65, y: 51)); bolt.line(to: NSPoint(x: 49, y: 25)); bolt.line(to: NSPoint(x: 62, y: 25)); bolt.line(to: NSPoint(x: 55, y: 5)); bolt.line(to: NSPoint(x: 80, y: 36)); bolt.line(to: NSPoint(x: 66, y: 36)); bolt.close(); bolt.fill()
            } else {
                for (i, x) in [35.0, 59.0, 83.0].enumerated() {
                    let progress = (phase + Double(i) / 3).truncatingRemainder(dividingBy: 1)
                    let alpha = sin(progress * .pi) * 0.9
                    let y = 44 - progress * 34
                    if name == "snow" {
                        let cx = x + sin(progress * .pi * 2) * 3
                        for angle in [0.0, 60, 120] {
                            let dx = cos(angle * .pi / 180) * 3.5, dy = sin(angle * .pi / 180) * 3.5
                            line(cx - dx, y - dy, dx * 2, dy * 2, 1.8, NSColor(calibratedWhite: 0.95, alpha: alpha))
                        }
                    } else {
                        line(x, y, name == "rain" ? -5 : -3, name == "rain" ? -9 : -5, name == "rain" ? 4 : 2.5, NSColor(calibratedRed: 0.32, green: 0.73, blue: 0.98, alpha: alpha))
                    }
                }
            }
        default: break
        }
        image.unlockFocus()
        let bitmap = NSBitmapImageRep(data: image.tiffRepresentation!)!
        CGImageDestinationAddImage(destination, bitmap.cgImage!, [kCGImagePropertyGIFDictionary: [kCGImagePropertyGIFDelayTime: name == "rain" ? 0.05 : 0.125, kCGImagePropertyGIFUnclampedDelayTime: name == "rain" ? 0.05 : 0.125]] as CFDictionary)
    }
    if !CGImageDestinationFinalize(destination) { fatalError("Cannot write \(output)") }
}
