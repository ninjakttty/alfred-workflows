# User preferences

## Alfred workflows

For every Alfred workflow created or updated for this user:
- Use the bundle ID format `net.ninjakitty.{workflow}`, replacing `{workflow}` with the lowercase hyphenated workflow name (for example, `net.ninjakitty.fast-city-time`).
- Set Created By (`createdby`) to `Yuri Parsons`.
- Set the website (`webaddress`) to `https://www.ninjakitty.net`.
- Name standalone workflow GitHub repositories using lowercase `alfred-<workflow-name>`. Inside the shared `alfred-workflows` repository, omit the redundant `alfred-` prefix from workflow folders and exported files (for example, `finder-iterm/` and `finder-iterm.alfredworkflow`).
- Include an appropriate workflow icon in the workflow and its installable export.
- When a workflow is complete, capture screenshots of the finished workflow in Alfred and add or update its screenshots in the main repository README before pushing. Store images in the workflow's `screenshots/` folder. Include relevant settings or secondary views when applicable, and keep screenshots current when the UI changes. Do not add extra descriptive text unless requested.

Apply these defaults across projects and chats unless the user explicitly requests otherwise.

## Tooling and branch workflow

- Prefer MCP tools whenever possible.
- Create a feature branch whenever starting work.

## Verification before commits

Before committing changes, test that the affected functionality actually works. Use appropriate automated checks and verify integration in the real application when applicable. For Alfred workflows, verify that Alfred accepts and loads the workflow and exercise changed user actions; standalone program output or mocked APIs alone are insufficient. Fix failures before committing. If an essential check cannot be performed, explain the limitation and do not claim the feature is verified or commit it without the user's explicit agreement.
