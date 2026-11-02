use framework "Foundation"
use scripting additions

on searchURL(searchQuery)
  if searchQuery is "" then error "Expected a search query"
  set allowedCharacters to current application's NSCharacterSet's characterSetWithCharactersInString:"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~"
  set queryText to current application's NSString's stringWithString:searchQuery
  set encodedQuery to queryText's stringByAddingPercentEncodingWithAllowedCharacters:allowedCharacters
  return "https://www.google.com/search?q=" & (encodedQuery as text)
end searchURL

on run argv
  if (count of argv) is not 1 then error "Expected one search query"
  set targetURL to my searchURL(item 1 of argv)
  tell application "Google Chrome"
    set searchWindow to make new window with properties {mode:"normal"}
    set URL of active tab of searchWindow to targetURL
    activate
  end tell
end run
