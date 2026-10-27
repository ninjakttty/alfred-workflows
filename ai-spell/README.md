# AI Spell

Native on-device Apple Intelligence spelling suggestions and definitions in Alfred.

## Use

- Type `spell <word or short phrase>` in Alfred. Pause briefly to start checking; no Return is needed to submit.
- Or select text in another app and press **Hyper+S (⌃⌥⇧⌘S)**.
- **Return** pastes the chosen correction into the previous app, replacing selected text when the app supports normal paste.
- **⌘ Return** copies the chosen correction.

Alfred immediately shows a loading row, then updates the same list with up to three distinct suggestions and brief definitions. Editing the input starts a new check. Escape dismisses Alfred; a completed or cancelled model request never opens it again. Older requests cannot replace a newer request's results.

Hyper+S uses Alfred's native **Show Alfred** action with **Selection in macOS** and the `spell ` prefix. No script or model runs before Alfred opens. The Swift Script Filter returns immediately and runs model generation in a separate helper process. It polls for results only while Alfred keeps that filter active. Dismissed or superseded checks are cancelled after a short grace period.

## Requirements and installation

Install `ai-spell.alfredworkflow` in Alfred 5 with Powerpack. Requires an Apple silicon Mac, macOS 26 or later, and Apple Intelligence enabled with its on-device model ready. Alfred needs Accessibility permission for selected-text capture and paste. Apps which block copying or pasting may not support those actions.

This version calls Apple's `SystemLanguageModel` directly through the native Swift Foundation Models framework. No Shortcuts, Siri automation, Python, JavaScript runtime, model API key, or network model service is used at runtime. Your existing `ai-spell` Shortcut is left untouched. Suggestions can still be incorrect; review them before applying.

Input is limited to 2,000 characters. Generation uses a structured Swift schema; empty and duplicate suggestions are removed. Model availability and generation errors appear in Alfred. A check times out after two minutes.

Request files have owner-only permissions in Alfred's workflow cache. Input files are removed after generation or cancellation. Result files expire after fifteen minutes and are cleaned up on subsequent requests. The workflow does not write diagnostic logs.

## Development

On a Mac with Xcode Command Line Tools and a macOS 26+ SDK:

```sh
zsh ai-spell/build-native.zsh
zsh ai-spell/test-native.zsh
```

The build compiles and ad-hoc signs an arm64 Swift executable, then generates the plist and installable export using Node.js. Node.js is needed for packaging only. Source and the MIT license are included in this repository. The icon and original idea come from the user's AI Spell Raycast extension; its private source remains ignored by Git.

Author: Yuri Parsons • https://www.ninjakitty.net
