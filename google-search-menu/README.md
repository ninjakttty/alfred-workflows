# Google Search Menu

Type `g hello` in Alfred, then press Return to show three choices:

1. **Google** — searches for `hello` (selected first).
2. **Google + Reddit** — searches for `hello reddit`.
3. **Google + FTL** — searches for `hello ftl`.

Press Return again to open the selected search in a **new normal Google Chrome window**, using Chrome's current normal profile. Use the arrow keys to choose a different option. Each choice has a custom icon. Reddit and FTL are ordinary appended words, not site restrictions.

Requires Alfred 5 with Powerpack and Google Chrome. macOS may request permission for Alfred to control Chrome. Errors remain visible in Alfred's workflow debugger.

Install `google-search-menu.alfredworkflow`. No extra runtimes or dependencies are needed; the menu uses a native List Filter and the Chrome action uses macOS AppleScript. Edit the List Filter items in Alfred to customize the choices.

Rebuild icons with `swift scripts/draw-icons.swift "$PWD"` from this folder. Repackage with `python3 scripts/build.py`; this packages the tracked native List Filter images. The local `icons/` source artwork folder is ignored by Git. To check query encoding, compile `open-chrome.applescript` with `osacompile -o /tmp/google-search-menu-open.scpt open-chrome.applescript`, then run `osascript scripts/test-search.applescript /tmp/google-search-menu-open.scpt`.

Author: Yuri Parsons • https://www.ninjakitty.net
