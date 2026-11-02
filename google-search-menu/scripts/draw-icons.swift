import AppKit

let root = CommandLine.arguments[1]
for (name, label, color) in [
  ("google", "G", NSColor(calibratedRed: 0.20, green: 0.45, blue: 0.94, alpha: 1)),
  ("reddit", "r", NSColor(calibratedRed: 0.98, green: 0.29, blue: 0.09, alpha: 1)),
  ("ftl", "FTL", NSColor(calibratedRed: 0.49, green: 0.29, blue: 0.87, alpha: 1)),
] {
  let image = NSImage(size: NSSize(width: 512, height: 512))
  image.lockFocus()
  color.setFill()
  NSBezierPath(roundedRect: NSRect(x: 16, y: 16, width: 480, height: 480), xRadius: 108, yRadius: 108).fill()
  let attributes: [NSAttributedString.Key: Any] = [
    .font: NSFont.systemFont(ofSize: label.count > 1 ? 136 : 260, weight: .bold),
    .foregroundColor: NSColor.white,
  ]
  let text = label as NSString
  let size = text.size(withAttributes: attributes)
  text.draw(at: NSPoint(x: (512 - size.width) / 2, y: (512 - size.height) / 2 + 18), withAttributes: attributes)
  NSColor.white.withAlphaComponent(0.75).setStroke()
  let line = NSBezierPath()
  line.lineWidth = 12
  line.lineCapStyle = .round
  line.move(to: NSPoint(x: 185, y: 100))
  line.line(to: NSPoint(x: 327, y: 100))
  line.stroke()
  image.unlockFocus()
  let bitmap = NSBitmapImageRep(data: image.tiffRepresentation!)!
  try bitmap.representation(using: .png, properties: [:])!.write(to: URL(fileURLWithPath: root + "/icons/" + name + ".png"))
  if name == "google" {
    try bitmap.representation(using: .png, properties: [:])!.write(to: URL(fileURLWithPath: root + "/icon.png"))
  }
}
