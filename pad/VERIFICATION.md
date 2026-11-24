# Pad AlfredUI verification

Verified locally on 23 November 2026 with Alfred 6.0.3.

- Imported/loaded the updated workflow graph in Alfred Preferences, including the Alfred UI object configured to launch externally.
- Exercised `pad-show` through Alfred search and the public external Show trigger. Observed the native Pad window with the existing note loaded and editor focused.
- Edited the note in the real AlfredUI editor and checked the saved UTF-8 file on disk.
- Exercised Hide through Alfred's external trigger, reopened, and observed the saved edit in the editor.
- Restored the original note and confirmed its content on disk.
- Repeated Show reused the existing AlfredUI process.
- Exercised Toggle on an open session, confirmed the session closed, then exercised cold Toggle and confirmed a new AlfredUI host/session initialized.

The initial computer-use checks were interrupted by intermittent `cgWindowNotFound` errors. Later installed-workflow checks are recorded below. Yuri subsequently tested the workflow and approved merging and pushing on 24 November 2026.

Automated tests cover Unicode/empty/replacement persistence, private file permissions, failure preservation, invalid UTF-8 load rejection, and safe read-only close. Run `./pad/scripts/build-install.sh` to rerun them and rebuild the installable export. The export excludes the old Swift app and Python caches.

Storage correction on 24 November 2026: note storage now uses `alfred_workflow_data`, and transient visibility state uses `alfred_workflow_cache`, with standard bundle-ID-based fallbacks. No legacy migration is included. The installed-workflow checks below verified the updated data location.

## Installed workflow checks — 24 November 2026

Installed the current source into Alfred's existing Pad workflow and launched it through the public Show trigger. Observed the real AlfredUI window without status text or a native title-bar close button.

Temporarily replaced the note destination with an empty directory, preserving any existing file, then typed into the real editor and clicked Close. The window stayed open and retained the text. This exposed a nonzero script exit suppressing UI error JSON; corrected it so UI errors return action JSON successfully while retaining stderr details and CLI failure codes. Repeated the real Close test and observed the error in the still-open window. Restored storage, cleared the temporary test text, and observed the error disappear after a successful save. The current note uses Alfred's standard workflow data directory.

Seven automated tests pass, including a subprocess regression test for displaying save failures. Latest source and export are installed.
