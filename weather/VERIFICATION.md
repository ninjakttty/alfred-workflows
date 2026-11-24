# Weather verification

Verified on 24 November 2026 with Alfred 6.0.3.

## Installed workflow

- Launched Weather from its public Show trigger and from the `weather` keyword's workflow result. Apple's Weather app can also match the keyword.
- Verified automatic IP-based location, saving a fixed city, and switching back to automatic mode. The user approved requests to ipapi and Open-Meteo.
- Verified an invalid city displays an error while retaining the existing forecast and saved settings.
- Verified Refresh completes and reenables controls.
- Visually checked the final layout: location heading; main four-hour block with its time range, lowest feels-like temperature, and maximum rain probability; three following four-hour blocks under “Rest of the day”; three daily feels-like high/low forecasts; and saved-location controls at the bottom.
- Verified section margins and the absence of wind, humidity, and redundant temperature wording in the main block.

The block icon represents the rainiest hour. Midnight-crossing time ranges have full dates in tooltips. “Rest of the day” labels the three following blocks even when they extend into the next date.

## Automated checks and caching

Ten tests pass, covering location fallback, coordinate validation, preserving settings after invalid city searches, Fahrenheit/apparent-temperature API fields, forecast-local times, missing values, four-hour minimum/maximum aggregation across midnight, cache expiry, forced refresh, per-coordinate forecast caching, and indefinite location storage.

Location records persist under Alfred's workflow data directory until explicitly refreshed. Forecast responses expire after 10 minutes in Alfred's cache directory. A live backend benchmark measured 0.385 seconds for a forced refresh with two requests and 0.001 seconds for a cached load with zero requests, excluding Alfred launch/render overhead. Subsequent live backend checks confirmed zero requests on repeated cached loads.

The installable export contains workflow metadata, the native AlfredUI package, executable Python script, and weather icon. No user settings or Python caches are exported. `git diff --check` passes.

## Temperature settings gear — 24 November 2026

Added a small bottom gear opening a native AlfredUI settings sheet with a Celsius/Fahrenheit picker, Apply, and Cancel. Temperature preferences persist with location settings; selecting another city preserves the unit. All temperature displays convert from the canonical cached Fahrenheit forecast locally. Twelve tests pass, including complete Celsius rendering, persistence, and invalid-unit rejection.

Installed the update, opened the gear in Alfred, selected Celsius, and observed the converted main, smaller-block, and daily values. Reopening the settings sheet showed Celsius selected. The computer-use connection then lost the window; restored the original Fahrenheit preference through the backend settings store while preserving the saved location.

## Location controls in settings — 24 November 2026

Moved the location-mode text, city field, Use city, and Current area into the gear settings sheet alongside the unit selector. Refresh and the gear remain on the main forecast. Verified the main view and settings sheet in Alfred, exercised Use city with the saved location, and returned through Apply. Twelve automated tests pass.

## Final settings and footer layout — 24 November 2026

Verified the native settings sheet with location controls, Celsius/Fahrenheit selection, and provider credits. The main forecast no longer displays timestamp, timezone, unit explanation, or credits. Visually verified Refresh aligned left and the gear aligned at the far right in the installed Alfred workflow. The user tested and approved this layout for commit. Twelve tests pass.
