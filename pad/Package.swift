// swift-tools-version: 5.9
import PackageDescription
let package = Package(name: "Scratchpad", platforms: [.macOS(.v13)], products: [.executable(name: "Scratchpad", targets: ["Scratchpad"])], targets: [.target(name: "ScratchpadCore"), .executableTarget(name: "Scratchpad", dependencies: ["ScratchpadCore"]), .testTarget(name: "ScratchpadCoreTests", dependencies: ["ScratchpadCore"])])
