# Finder iTerm

![Workflow icon](icon.png)

- `cdf` (cd in Finder): open the selected session in the current iTerm window in a new Finder window.
- `cdi` (cd in iTerm): open the front Finder window's folder in a new iTerm tab. If no iTerm window exists, create one.

No arguments are needed. With split panes, `cdf` uses the active pane. `cdi` uses the Finder window's folder, not a selected item. Virtual Finder locations such as Recents are not ordinary folders.

Requires Alfred 5 with Powerpack and iTerm2. macOS may ask permission for Alfred to control Finder and iTerm. `cdf` uses the directory iTerm reports; enable iTerm shell integration if it is unavailable or stale. These commands are intended for local directories, not remote SSH directories.

Source files and the installable export live in this folder. `info.plist` defines both keywords and external triggers for integration testing.

Author: Yuri Parsons • https://www.ninjakitty.net
