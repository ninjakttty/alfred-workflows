import AppKit
let image = NSImage(size: NSSize(width: 512, height: 512))
image.lockFocus()
NSColor(calibratedRed: 0.16, green: 0.23, blue: 0.32, alpha: 1).setFill()
NSBezierPath(roundedRect: NSRect(x: 16, y: 16, width: 480, height: 480), xRadius: 96, yRadius: 96).fill()
NSColor(calibratedRed: 1, green: 0.89, blue: 0.52, alpha: 1).setFill()
NSBezierPath(roundedRect: NSRect(x: 112, y: 80, width: 288, height: 352), xRadius: 18, yRadius: 18).fill()
NSColor(calibratedRed: 0.48, green: 0.36, blue: 0.16, alpha: 1).setStroke()
for y in stride(from: 160, through: 352, by: 64) {
 let line = NSBezierPath(); line.lineWidth = 12; line.move(to: NSPoint(x: 156, y: y)); line.line(to: NSPoint(x: 356, y: y)); line.stroke()
}
image.unlockFocus()
let bitmap = NSBitmapImageRep(data: image.tiffRepresentation!)!
try bitmap.representation(using: .png, properties: [:])!.write(to: URL(fileURLWithPath: CommandLine.arguments[1]))
