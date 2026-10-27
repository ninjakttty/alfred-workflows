#!/bin/zsh
set -eu
cd "${0:A:h}"
mkdir -p "${TMPDIR:-/tmp}/ai-spell-swift-cache"
/usr/bin/xcrun swiftc -O -parse-as-library -target arm64-apple-macos26.0 -module-cache-path "${TMPDIR:-/tmp}/ai-spell-swift-cache" Sources/AISpell.swift -o ai-spell-native
/usr/bin/codesign --force --sign - ai-spell-native
node build.js
