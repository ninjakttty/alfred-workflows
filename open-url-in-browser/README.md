# Open URL in Browser

Use Alfred keyword **url** or press **Hyper+O** (`⌃⌥⇧⌘O`) while text is selected in macOS to open the selected text as a URL in a **new normal Google Chrome window**.

- Uses both an Alfred **Keyword** trigger and an Alfred **Hotkey** trigger.
- Both triggers pass current selected text from macOS.
- If the selected text has no URL scheme, the workflow prepends `https://`.

## Requirements

- Alfred 5 with Powerpack
- Google Chrome
- macOS permission for Alfred to access selected text and control Chrome (if prompted)

## Notes

- The keyword is `url` and uses the currently selected URL/domain text (for example `example.com` or `https://example.com/path`).
- The default hotkey is Hyper+O. Change it in Alfred if you prefer another key.

Author: Yuri Parsons • https://www.ninjakitty.net
