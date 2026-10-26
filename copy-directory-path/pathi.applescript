on run argv
try
    if not application "iTerm2" is running then error "Open an iTerm2 session first."
    tell application "iTerm2"
        if (count of windows) is 0 then error "Open an iTerm2 session first."
        tell current session of current window
            set folderPath to variable named "path"
        end tell
    end tell
    if folderPath is missing value or folderPath is "" then error "iTerm2 could not report this session's directory. Enable iTerm2 shell integration and try again."
    if folderPath does not start with "/" then error "iTerm2 did not report an absolute directory path."
    if (count of argv) > 0 then
        if item 1 of argv is "shell-escaped" then set folderPath to quoted form of folderPath
    end if
    set the clipboard to folderPath
on error errorMessage
    display alert "Copy Directory Path" message errorMessage as warning
end try
end run
