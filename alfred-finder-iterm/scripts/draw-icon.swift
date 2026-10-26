import AppKit
let image = NSImage(size: NSSize(width: 512, height: 512))
image.lockFocus()
NSColor(calibratedRed: 0.12, green: 0.24, blue: 0.38, alpha: 1).setFill()
NSBezierPath(roundedRect: NSRect(x: 16,y: 16,width: 480,height: 480), xRadius: 100,yRadius: 100).fill()
NSColor(calibratedRed: 0.30, green: 0.70, blue: 0.98, alpha: 1).setFill()
NSBezierPath(roundedRect: NSRect(x: 65,y: 240,width: 190,height: 125), xRadius: 16,yRadius: 16).fill()
NSBezierPath(roundedRect: NSRect(x: 65,y: 340,width: 90,height: 40), xRadius: 12,yRadius: 12).fill()
NSColor(calibratedWhite: 0.07, alpha: 1).setFill()
NSBezierPath(roundedRect: NSRect(x: 213,y: 120,width: 235,height: 175), xRadius: 20,yRadius: 20).fill()
let text = ">_" as NSString
text.draw(at: NSPoint(x: 245,y: 160), withAttributes: [.font: NSFont.monospacedSystemFont(ofSize: 72, weight: .bold), .foregroundColor: NSColor(calibratedRed: 0.45,green: 0.95,blue: 0.65,alpha: 1)])
image.unlockFocus()
let bitmap = NSBitmapImageRep(data: image.tiffRepresentation!)!
try bitmap.representation(using: .png, properties: [:])!.write(to: URL(fileURLWithPath: CommandLine.arguments[1]))
