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
