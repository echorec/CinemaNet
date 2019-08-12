// swift-tools-version:5.0
// The swift-tools-version declares the minimum version of Swift required to build this package.

import PackageDescription

let package = Package(
    name: "synopsis_auto_labeller",
    platforms: [SupportedPlatform.macOS(SupportedPlatform.MacOSVersion.v10_13)],
    dependencies: [
        // Dependencies declare other packages that this package depends on.
        .package(url: "https://github.com/apple/swift-package-manager.git", from: "0.4.0"),
    ],
    targets: [
        // Targets are the basic building blocks of a package. A target can define a module or a test suite.
        // Targets can depend on other targets in this package, and on products in packages which this package depends on.
        .target(
            name: "synopsis_auto_labeller",
            dependencies: ["SPMUtility"]),
        .testTarget(
            name: "synopsis_auto_labellerTests",
            dependencies: ["synopsis_auto_labeller"]),
    ]
)

