# Verification — 26 October 2026

Built and installed locally on Apple silicon using Swift 6.4. `swift test` passed all four tests. Release build, ad-hoc signing, both plist validation checks, shell syntax checks, invalid CLI command rejection, and `git diff --check` passed.

Exercised the installed app through Alfred external triggers and native UI:

- Cold `toggle` launched the app with a focused multiline editor.
- Typed and pasted multiline Unicode text, then pressed Escape; the window disappeared and the file contained the saved text.
- `show` restored the note and focused editor.
- The panel remained visible and inactive when Finder had focus.
- Found and fixed a Launch Services reopen event that could undo a toggle. Retested toggle off/on against the installed release.
- Quit and relaunched; the Unicode note was restored. Process inspection showed one Scratchpad instance.
- Tested close-button dismissal and the explicit hide trigger. The UI tool reports a timeout/no available window while the panel is hidden, and can inspect it again after show/toggle.
- Confirmed frame and cursor preferences were written. Cleared verification text through the editor; the saved note is empty.

Automated tests cover persistence and pure command rules. Fullscreen Spaces, monitor removal, interactive disk-full handling, and a manual resize/relaunch comparison were not verified. No commit was made.

## Self-contained workflow update

Rebuilt and reran all four tests successfully. The export includes the signed app under `.scratchpad/Scratchpad.app` and an executable relative-path launcher. Installed that workflow and replaced the optional CLI with a symlink to its launcher. Moved both standalone app copies to Trash and unregistered their old Launch Services paths; note storage was unchanged. Verified the bundled app through the real Alfred toggle trigger, including hide/show and restored editor focus. Visually inspected Alfred search for `scratch`: only the four workflow actions appeared, with neither standalone app entry present.

## Pad workflow rename

Renamed the workflow to Pad (`net.ninjakitty.pad`), with keywords `pad`, `pad-show`, `pad-hide`, and `pad-quit`. Moved the source folder and renamed the installable export to `pad/pad.alfredworkflow`. Preserved the bundled app's internal identifier, launcher, and note path. Validated the plist and installer shell syntax, inspected all four renamed results in Alfred, and exercised the new workflow's show trigger with editor focus confirmed. No application code changed.

## Full flow after clean import

Tested the user's fresh import (`user.workflow.EFFF7E65-6E2C-4A2E-90CF-CBCF447A0DF7`) without replacing it. Confirmed a fresh import omitted the category, despite the export specifying Productivity. Alfred offers a local category choice during import; documented selecting Productivity during import or from the workflow context menu afterwards. The earlier in-place metadata update had not tested this import behavior.

Passed: all four Swift tests; real Alfred search shows only `pad`, `pad-show`, `pad-hide`, with no quit action or standalone app duplicates; cold `pad` keyword launches with focused editor; multiline Unicode edits save before Escape; show restores focus and caret; inserting at the caret confirms its position across hide/show and full quit/relaunch; toggle hides a visible panel from Alfred and shows a hidden panel; close button and explicit hide dismiss it; Command-Q exits; saved note and zoomed window size restore after relaunch. Process exit was checked with pgrep. Restored the original window frame, removed test text, and verified note bytes exactly match the pre-test backup. Left the app stopped.

Found and fixed the optional Terminal CLI's stale UUID symlink after reinstall. It now discovers the installed Pad workflow at each invocation, including Alfred's configured sync folder. Verified show, hide, and quit through the repaired CLI against the fresh UUID. The build/install script installs this dispatcher for future setups. No application binary changed. Fullscreen Spaces and monitor removal remain untested.

## Final reinstall retest and survivor recovery

The user's last reinstall revealed a surviving hidden process from the prior workflow UUID; the new bundle could not receive commands because the old process held the note lock. Fixed the bundled launcher to run a native preflight: identify matching app instances at different bundle paths, request normal termination (including their save handler), wait up to five seconds, and refuse to continue if termination fails. The current-path instance is left running normally.

Rebuilt and installed the fix; all four unit tests passed. Reproduced the failure condition using a real running copy, moved its bundle away from its original path while hidden, then invoked the installed launcher. Verified the old process exited, exactly one process ran from the installed workflow path, the saved multiline Unicode text was preserved, and the editor focus and caret were restored. Restored the moved build bundle afterwards.

Retested real Alfred keyword toggle (visible → hidden), external toggle (hidden → focused), show, hide, Escape save, and close-button dismissal. Search showed exactly three Pad actions with “Floating note”, without quit or standalone app entries. Restored the original note through the editor and compared bytes with the pre-test backup. Final CLI quit completed normally and process inspection confirmed Pad stopped. Updated both installed workflow and installable export. Fullscreen and monitor removal remain untested.
