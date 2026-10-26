import AppKit
let size = 512
let image = NSImage(size: NSSize(width:size,height:size))
image.lockFocus()
NSColor.clear.setFill();NSRect(x:0,y:0,width:512,height:512).fill()
let tile = NSBezierPath(roundedRect: NSRect(x:20,y:20,width:472,height:472), xRadius:108,yRadius:108)
NSGradient(starting:NSColor(calibratedRed:0.08,green:0.20,blue:0.38,alpha:1),ending:NSColor(calibratedRed:0.04,green:0.09,blue:0.19,alpha:1))!.draw(in:tile,angle:90)
let ring=NSBezierPath(ovalIn:NSRect(x:101,y:101,width:310,height:310));ring.lineWidth=22
NSColor(calibratedRed:0.95,green:0.98,blue:1,alpha:1).setStroke();ring.stroke()
NSColor(calibratedRed:0.35,green:0.84,blue:0.97,alpha:1).setStroke()
let meridian=NSBezierPath(ovalIn:NSRect(x:176,y:112,width:160,height:288));meridian.lineWidth=7;meridian.stroke()
let equator=NSBezierPath();equator.move(to:NSPoint(x:112,y:256));equator.line(to:NSPoint(x:400,y:256));equator.lineWidth=7;equator.stroke()
// Dark halo keeps the clock hands distinct from the globe grid.
let hands=NSBezierPath();hands.move(to:NSPoint(x:256,y:344));hands.line(to:NSPoint(x:256,y:256));hands.line(to:NSPoint(x:323,y:219));hands.lineCapStyle = .round;hands.lineJoinStyle = .round
NSColor(calibratedRed:0.05,green:0.12,blue:0.24,alpha:1).setStroke();hands.lineWidth=33;hands.stroke()
NSColor.white.setStroke();hands.lineWidth=20;hands.stroke()
NSColor(calibratedRed:0.35,green:0.84,blue:0.97,alpha:1).setFill();NSBezierPath(ovalIn:NSRect(x:244,y:244,width:24,height:24)).fill()
image.unlockFocus()
let rep=NSBitmapImageRep(data:image.tiffRepresentation!)!
try rep.representation(using:.png,properties:[:])!.write(to:URL(fileURLWithPath:CommandLine.arguments[1]))
