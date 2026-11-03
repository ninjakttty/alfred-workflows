# Selected Text Chrome Window

Press **Hyper+O** (`⌃⌥⇧⌘O`) while text is selected in macOS to open that text in a **new normal Google Chrome window**.

- Uses an Alfred **Hotkey** trigger (not a keyword trigger).
- Passes the current selected text from macOS directly into the workflow.
- If the selected text has no URL scheme, the workflow prepends `https://`.

## Requirements

- Alfred 5 with Powerpack
- Google Chrome
- macOS permission for Alfred to access selected text and control Chrome (if prompted)

## Notes

- The default hotkey is Hyper+O. Change it in Alfred if you prefer another key.
- Intended for selected URLs/domains (for example `example.com` or `https://example.com/path`).

Author: Yuri Parsons • https://www.ninjakitty.net
