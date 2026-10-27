#!/bin/zsh
set -eu
cd "${0:A:h}"
/usr/bin/xcrun swiftc -D TESTING -parse-as-library -module-cache-path "${TMPDIR:-/tmp}/ai-spell-swift-cache" Sources/AISpell.swift tests/NativeTests.swift -o "${TMPDIR:-/tmp}/ai-spell-native-tests"
"${TMPDIR:-/tmp}/ai-spell-native-tests"
node --test tests/native-integration.test.cjs
