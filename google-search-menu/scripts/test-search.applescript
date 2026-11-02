on run argv
  set workflowScript to load script (POSIX file (item 1 of argv))
  set actual to workflowScript's searchURL("C++ & café #1? 你好 🚀")
  set expected to "https://www.google.com/search?q=C%2B%2B%20%26%20caf%C3%A9%20%231%3F%20%E4%BD%A0%E5%A5%BD%20%F0%9F%9A%80"
  if actual is not expected then error "URL encoding failed: " & actual
  return "Query encoding passed"
end run
