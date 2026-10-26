on run argv
try
    tell application "Finder"
        if (count of Finder windows) is 0 then error "Open a Finder folder first."
        set folderPath to POSIX path of (target of front Finder window as alias)
    end tell
    if (count of argv) > 0 then
        if item 1 of argv is "shell-escaped" then set folderPath to quoted form of folderPath
    end if
    set the clipboard to folderPath
on error errorMessage
    display alert "Copy Directory Path" message errorMessage as warning
end try
end run
