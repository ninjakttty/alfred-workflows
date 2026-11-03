use framework "Foundation"
use scripting additions

on normalizeURL(rawText)
  set nsRawText to current application's NSString's stringWithString:rawText
  set trimmed to nsRawText's stringByTrimmingCharactersInSet:(current application's NSCharacterSet's whitespaceAndNewlineCharacterSet())
  set textValue to trimmed as text

  if textValue is "" then error "No selected text was provided."

  if textValue starts with "http://" or textValue starts with "https://" then return textValue

  return "https://" & textValue
end normalizeURL

on run argv
  if (count of argv) is not 1 then error "Expected selected text as one argument."

  set targetURL to my normalizeURL(item 1 of argv)

  tell application "Google Chrome"
    set targetWindow to make new window with properties {mode:"normal"}
    set URL of active tab of targetWindow to targetURL
    activate
  end tell
end run
