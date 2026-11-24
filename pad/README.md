# Pad

A small floating plain-text note built with the [Alfred UI Toolkit](https://www.alfredapp.com/help/alfredui/). Requires Alfred 6 with Powerpack and Python 3. No compiled app, Swift build, or third-party Python packages are needed. Python is resolved from Alfred's PATH; this Mac uses its existing asdf runtime.

## Install

Open `pad.alfredworkflow` and import it into Alfred. Quit the old Scratchpad app before upgrading so two editors cannot write the same note. The workflow includes its icon and `pad.alfredui` package.

To test and rebuild the export:

```sh
./pad/scripts/build-install.sh
```

Pass an existing Alfred workflow directory as the first argument to update that installation. The installer does not create global commands or install runtimes. An existing optional `~/.local/bin/scratchpad` dispatcher remains compatible.

## Use

- `pad`: toggle the floating note, including while another application has focus.
- `pad-show`: open or focus the note. Repeated Show requests reuse the same window.
- `pad-hide`: close the note without opening it first.
- Escape, Command-W, or Close: save and close the note.

The external window floats above ordinary windows, can be moved and resized, and remembers its frame. AlfredUI controls window lifecycle and Space behavior. Closing releases the editor; reopening reloads the saved text. Cursor position is no longer persisted.

The external triggers `toggle`, `show`, and `hide` retain bundle ID `net.ninjakitty.pad`. The workflow-local launcher accepts `toggle` (default), `show`, `hide`, and `quit`:

```sh
./scratchpad show
```

`quit` behaves like `hide`. Commands are asynchronous. The internal `ui-launch` trigger opens the AlfredUI object; use the public triggers for normal control.

## Storage and errors

The note uses `alfred_workflow_data`, with this standard location as the fallback for standalone launches:

```text
~/Library/Application Support/Alfred/Workflow Data/net.ninjakitty.pad/note.txt
```

Each user edit synchronously writes UTF-8 through a private temporary file and atomic replacement. An unreadable or invalid UTF-8 note leaves the editor read-only and displays the error. Save failures display the error and suspend external hide/toggle polling; text stays in the open editor. Correct the storage problem and edit again or use Close to retry. The native title-bar close button is disabled because it cannot veto closing after a save failure. Use Close, Escape, or Command-W: each saves first and leaves the editor open on failure. Quitting AlfredUI itself cannot be vetoed by the toolkit. Do not externally edit the note while Pad is open.

The backend stores the AlfredUI host PID to distinguish an open note from a closed/crashed instance. External hide/toggle requests are handled by a lightweight pulse every 0.25 seconds. Visibility control files use `alfred_workflow_cache`, falling back to `~/Library/Caches/com.runningwithcrayons.Alfred/Workflow Data/net.ninjakitty.pad`. No network requests are made.

## Verification

```sh
python3 -m unittest discover -s pad/tests -v
```

Tests cover Unicode, empty/replacement saves, private permissions, failed write preservation, and invalid UTF-8. See `VERIFICATION.md` for real Alfred checks. If launch fails, open Alfred's workflow debugger; persistence errors also appear in the note's status bar and stderr.

Author: Yuri Parsons · https://www.ninjakitty.net
