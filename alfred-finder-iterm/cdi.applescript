try
    tell application "Finder"
        if (count of Finder windows) is 0 then error "Open a Finder folder first."
        set folderPath to POSIX path of (target of front Finder window as alias)
    end tell
    set cdCommand to "cd -- " & quoted form of folderPath
    tell application "iTerm2"
        if (count of windows) is 0 then
            set destinationWindow to create window with default profile
            set destinationSession to current session of destinationWindow
        else
            tell current window
                set destinationTab to create tab with default profile
            end tell
            set destinationSession to current session of destinationTab
        end if
        tell destinationSession to write text cdCommand
        activate
    end tell
on error errorMessage
    display alert "Finder iTerm" message errorMessage as warning
end try
