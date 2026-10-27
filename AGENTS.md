# User preferences

## Alfred workflows

For every Alfred workflow created or updated for this user:
- Use the bundle ID format `net.ninjakitty.{workflow}`, replacing `{workflow}` with the lowercase hyphenated workflow name (for example, `net.ninjakitty.fast-city-time`).
- Set Created By (`createdby`) to `Yuri Parsons`.
- Set the website (`webaddress`) to `https://www.ninjakitty.net`.
- Name standalone workflow GitHub repositories using lowercase `alfred-<workflow-name>`. Inside the shared `alfred-workflows` repository, omit the redundant `alfred-` prefix from workflow folders and exported files (for example, `finder-iterm/` and `finder-iterm.alfredworkflow`).
- Include an appropriate workflow icon in the workflow and its installable export.

Apply these defaults across projects and chats unless the user explicitly requests otherwise.

## Commit organization

When committing work, split changes into multiple commits organized by logical unit. Keep each commit focused, coherent, and independently reviewable. Do not combine unrelated changes into one commit or split tightly coupled changes merely to increase the commit count.

## Verification before commits

Before committing changes, test that the affected functionality actually works. Use appropriate automated checks and verify integration in the real application when applicable. For Alfred workflows, verify that Alfred accepts and loads the workflow and exercise changed user actions; standalone program output or mocked APIs alone are insufficient. Fix failures before committing. If an essential check cannot be performed, explain the limitation and do not claim the feature is verified or commit it without the user's explicit agreement.
