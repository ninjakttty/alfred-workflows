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


## UI redesign — 24 November 2026

Redesigned on `feat/weather-ui-redesign`: compact location heading, a grouped main forecast card, consistent rounded cards for the three following blocks and daily forecasts, quieter section headings, and Refresh/settings at opposite ends of the footer. Removed the hidden status label's reserved space; loading and errors now appear only when needed in the footer. Settings groups location and temperature into separate cards and aligns its actions right.

Installed and visually checked both views in Alfred. Exercised an invalid location search and verified the error while retaining the existing forecast and saved settings; cancelled settings and refreshed successfully, observing the temporary loading state and restored controls. Temperature preference and location settings were preserved. Twelve tests pass, including updated Celsius and minimum/maximum aggregation checks against the new daily cards. Changes remain uncommitted.

## Compact daily list — 24 November 2026

Replaced the daily forecast cards with three compact, aligned rows in one rounded panel. Each row retains day/date, conditions, feels-like high/low, and rain probability. The main and hourly cards are unchanged. Rebuilt and installed; visually verified the compact list in Alfred. All twelve tests pass.

## README screenshots — 24 November 2026

Captured the real installed Alfred forecast and settings views and added both screenshots to the README. All twelve tests and the whitespace check passed before merging. Keyboard shortcuts remain deferred.

## Heading alignment — 24 November 2026

Made Rest of the day and 3-day forecast bold and inset them 12 points to align with the box contents. Inset Refresh to the same visible text alignment. Installed and visually verified in Alfred, then refreshed both README screenshots. All twelve tests pass.


## Main rain animation prototype — 24 November 2026

Added a small bundled GIF for the main rain/drizzle icon, generated locally with AppKit and ImageIO. Other main conditions, including thunderstorms and snow, and all smaller icons remain static. There is no WebKit view, polling script, or extra network request for animation. Native playback was verified in the real Alfred view: consecutive screenshots visibly show raindrops at different positions. Updated the forecast screenshot. Thirteen tests pass, including resetting the image when conditions change. The prototype is installed and remains uncommitted on `feat/weather-rain-animation`.


## All main condition animations and preview — 24 November 2026

Extended the main icon to ten bundled native GIFs: sunshine, clear night, day/night partly cloudy, overcast, fog, drizzle, rain, snow, and thunderstorms. Unknown conditions retain a static fallback. Smaller hourly and daily icons remain static. Assets are generated with AppKit/ImageIO from `scripts/draw-weather-icons.swift`; no additional runtime dependencies, WebKit views, repeating scripts, or network requests are needed for playback.

Added Settings → Preview weather icons, a local-only picker that can display every animation without changing the live forecast or saved settings. Verified preview navigation and sunshine, clear night, cloudy night, fog, snow, thunderstorm, and rain rendering in Alfred. Decoded every asset with ImageIO: each has 24 valid frames with multiple distinct images. Thunderstorm uses a slow soft bolt glow instead of rapid flashing. Updated main/settings screenshots and added a preview screenshot to both READMEs. Fifteen tests pass, covering condition mapping, fallback, and preview isolation. The workflow is installed; changes remain uncommitted.

## Installed version and preview removal — 25 November 2026

Audited Alfred's active Weather folder after its UUID changed on reimport. The scripts and ten animation assets matched the working tree. Rebuilt as version 1.1.0, added the version to the keyword subtitle and settings heading, and installed into the active folder located by bundle ID. Tested the actual weather keyword through launch, settings, and the animation preview.

At the user's request, removed the preview button from settings and its README screenshot links; animated main icons remain enabled. Rebuilt and reinstalled, verified Settings shows 1.1.0 without the preview button, and refreshed its screenshot. Fifteen tests pass.

## City error clipping — 25 November 2026

The settings sheet initially allocated no height for errors; later text could be clipped. Reserved a two-line error area, gave the error label the same height with word wrapping/full-text tooltip, and shortened the city-search guidance to “City not found. Try ‘Dublin, Ireland’.” Tested an invalid city in the installed Alfred settings and visually confirmed the complete message. Cleared the test error while preserving the saved location and unit. Fifteen tests pass.

## City-only title — 25 November 2026

Forecast titles now use the provider's city field rather than the joined city/region/country name. The full resolved name remains in the tooltip. A regression test preserves city names containing commas. Rebuilt and installed; observed “Stillorgan” as the title in Alfred and refreshed the forecast screenshot. Sixteen tests pass.
