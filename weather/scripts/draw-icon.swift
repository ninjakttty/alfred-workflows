import AppKit
let image = NSImage(size: NSSize(width: 512, height: 512))
image.lockFocus()
NSColor(calibratedRed: 0.08, green: 0.19, blue: 0.34, alpha: 1).setFill()
NSBezierPath(roundedRect: NSRect(x: 0, y: 0, width: 512, height: 512), xRadius: 106, yRadius: 106).fill()
NSColor(calibratedRed: 1, green: 0.75, blue: 0.24, alpha: 1).setFill()
NSBezierPath(ovalIn: NSRect(x: 228, y: 240, width: 180, height: 180)).fill()
NSColor.white.setFill()
NSBezierPath(roundedRect: NSRect(x: 88, y: 120, width: 338, height: 130), xRadius: 65, yRadius: 65).fill()
NSBezierPath(ovalIn: NSRect(x: 130, y: 160, width: 180, height: 180)).fill()
NSBezierPath(ovalIn: NSRect(x: 248, y: 145, width: 148, height: 148)).fill()
image.unlockFocus()
let bitmap = NSBitmapImageRep(data: image.tiffRepresentation!)!
try bitmap.representation(using: .png, properties: [:])!.write(to: URL(fileURLWithPath: CommandLine.arguments[1]))
