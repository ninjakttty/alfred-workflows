use framework "Foundation"
use scripting additions

on readCurrentSelectedText()
  set previousClipboard to the clipboard
  try
    tell application "System Events"
      if exists process "Alfred" then set visible of process "Alfred" to false
    end tell
    delay 0.05
    tell application "System Events"
      keystroke "c" using {command down}
    end tell
    delay 0.15
    set selectedText to the clipboard as text
    set the clipboard to previousClipboard
    return selectedText
  on error errMsg number errNum
    set the clipboard to previousClipboard
    error "Could not read selected text from the current app. " & errMsg number errNum
  end try
end readCurrentSelectedText

on normalizeURL(rawText)
  set nsRawText to current application's NSString's stringWithString:rawText
  set trimmed to nsRawText's stringByTrimmingCharactersInSet:(current application's NSCharacterSet's whitespaceAndNewlineCharacterSet())
  set textValue to trimmed as text

  if textValue is "" then error "No selected text was provided."

  if textValue starts with "http://" or textValue starts with "https://" then return textValue

  return "https://" & textValue
end normalizeURL

on run argv
  if (count of argv) is 1 then
    set sourceText to item 1 of argv
  else
    set sourceText to my readCurrentSelectedText()
  end if
  
  if sourceText is "" then set sourceText to my readCurrentSelectedText()
  
  set targetURL to my normalizeURL(sourceText)

  tell application "Google Chrome"
    set targetWindow to make new window with properties {mode:"normal"}
    set URL of active tab of targetWindow to targetURL
    activate
  end tell
end run
