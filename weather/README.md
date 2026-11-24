# Weather

A native AlfredUI forecast inside Alfred. Requires Alfred 6 with Powerpack, Python 3, and macOS's built-in curl. No API key, compiled app, or third-party Python package is needed.

## Use

Import `weather.alfredworkflow`, type `weather` in Alfred, and choose the Weather workflow result with the cloud-and-sun icon. Apple’s Weather app may also appear; select the workflow result when needed. The large summary shows the current four-hour block, starting with the current forecast hour, with its lowest feels-like temperature and highest hourly rain probability. Three smaller four-hour blocks cover the following 12 hours. A three-day forecast is also shown. All displayed temperatures use feels-like (apparent) values, including hourly temperatures and daily highs/lows. Each hourly block shows its lowest feels-like temperature and highest hourly rain probability; the icon represents the rainiest hour. Missing values display as a dash. Temperatures default to Fahrenheit. Use the gear at the bottom to open Weather settings, choose Celsius or Fahrenheit, and Apply. The choice is saved with your location settings. Conversion uses the cached Fahrenheit forecast locally, so changing units does not invalidate the forecast cache. Times are local to the forecast location; the timezone and observation time are not displayed in the forecast view.

Automatic location uses your public IP through [ipapi](https://ipapi.co/), so it is approximate and can reflect a VPN or network provider rather than your actual city. It does not request GPS or macOS Location Services. If automatic lookup fails, the saved city is used, initially Dublin, Ireland.

Open the bottom gear, enter a city (optionally followed by country or region), and choose **Use city** to save a fixed location. Location buttons apply immediately; the resolved location is displayed above the forecast. The location-mode text, city field, and Current area button live in this settings screen alongside the temperature selector. Refresh remains on the main forecast. Choose **Current area** to return to automatic location, or **Refresh** to reload from the services, bypassing caches. Empty or unsuccessful city searches leave the existing setting unchanged. Escape dismisses the view normally.

Provider credits appear in the gear settings screen. Forecasts and city search use [Open-Meteo](https://open-meteo.com/). Automatic location sends a request to ipapi.co, which sees your public IP; Open-Meteo receives the selected coordinates, and city searches send the entered city to Open-Meteo's geocoding service. Open-Meteo's public API is for noncommercial use. No credentials are needed. Network and service errors appear in the view and stderr. A failed refresh preserves the previous forecast and its timestamp.

## Speed and caching

Automatic location and city coordinates are stored indefinitely under `alfred_workflow_data/locations`, without time-based expiry. Forecasts remain cached for 10 minutes under `alfred_workflow_cache`, keyed by their coordinates. Refresh and Current area explicitly look up location again and replace the stored response; use either after moving or changing networks. Observation times are not displayed. Forecast cache files may safely be deleted. Location records remain until explicitly refreshed or their data files are removed.

## Storage and development

Settings are stored at `alfred_workflow_data/settings.json`, falling back to `~/Library/Application Support/Alfred/Workflow Data/net.ninjakitty.weather/settings.json` for standalone execution. No user settings are included in the exported workflow.

```sh
python3 weather/scripts/build.py
```

The build runs the tests and packages the workflow and icon. Artwork source is in `scripts/draw-icon.swift`; rebuilding the workflow does not require Swift. External trigger `show` is available under `net.ninjakitty.weather`.

Author: Yuri Parsons · https://www.ninjakitty.net
