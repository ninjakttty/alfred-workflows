# User preferences

## Alfred workflows

For every Alfred workflow created or updated for this user:
- Use the bundle ID format `net.ninjakitty.{workflow}`, replacing `{workflow}` with the lowercase hyphenated workflow name (for example, `net.ninjakitty.fast-city-time`).
- Set Created By (`createdby`) to `Yuri Parsons`.
- Set the website (`webaddress`) to `https://www.ninjakitty.net`.
- Name GitHub repositories, workflow folders, and exported workflow files using lowercase `alfred-<workflow-name>` (for example, `alfred-finder-iterm` and `alfred-finder-iterm.alfredworkflow`).
- Include an appropriate workflow icon in the workflow and its installable export.

Apply these defaults across projects and chats unless the user explicitly requests otherwise.

## Verification before commits

Before committing changes, test that the affected functionality actually works. Use appropriate automated checks and verify integration in the real application when applicable. For Alfred workflows, verify that Alfred accepts and loads the workflow and exercise changed user actions; standalone program output or mocked APIs alone are insufficient. Fix failures before committing. If an essential check cannot be performed, explain the limitation and do not claim the feature is verified or commit it without the user's explicit agreement.
