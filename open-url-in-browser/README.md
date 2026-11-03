# Open URL in Browser

Use Alfred keyword **ou** (type/paste a URL) or press **Hyper+O** (`⌃⌥⇧⌘O`) while text is selected in macOS to open the URL in a **new normal Google Chrome window**.

- Uses both an Alfred **Keyword** trigger and an Alfred **Hotkey** trigger.
- The keyword passes your typed query; the hotkey passes current selected text from macOS.
- If the selected text has no URL scheme, the workflow prepends `https://`.

## Requirements

- Alfred 5 with Powerpack
- Google Chrome
- macOS permission for Alfred to access selected text and control Chrome (if prompted)

## Notes

- The keyword is `ou` and expects a URL/domain (for example `example.com` or `https://example.com/path`).
- The default hotkey is Hyper+O. Change it in Alfred if you prefer another key.

Author: Yuri Parsons • https://www.ninjakitty.net
