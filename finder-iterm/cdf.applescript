try
    if not application "iTerm2" is running then error "Open an iTerm tab first."
    tell application "iTerm2"
        if (count of windows) is 0 then error "Open an iTerm tab first."
        tell current session of current window
            set folderPath to variable named "path"
        end tell
    end tell
    if folderPath is missing value or folderPath is "" then error "iTerm could not report this tab's directory. Enable iTerm shell integration and try again."
    if folderPath does not start with "/" then error "The selected iTerm tab did not report an absolute local directory."
    set folderAlias to POSIX file folderPath as alias
    tell application "Finder"
        make new Finder window to folderAlias
        activate
    end tell
on error errorMessage
    display alert "Finder iTerm" message errorMessage as warning
end try
