#!/usr/bin/env python3
"""Weather data and native AlfredUI rendering, using only the standard library."""
from datetime import datetime
import json
import hashlib
import time
import os
from pathlib import Path
import sys
import subprocess
import tempfile
from urllib.parse import urlencode

DATA = Path(os.environ.get('alfred_workflow_data') or Path.home() / 'Library/Application Support/Alfred/Workflow Data/net.ninjakitty.weather')
SETTINGS = DATA / 'settings.json'
CACHE = Path(os.environ.get('alfred_workflow_cache') or Path.home() / 'Library/Caches/com.runningwithcrayons.Alfred/Workflow Data/net.ninjakitty.weather')
CONTROLS = ('city', 'use-city', 'automatic', 'refresh')


def fetch(url):
    response = subprocess.run(
        ['/usr/bin/curl', '--fail-with-body', '--silent', '--show-error',
         '--connect-timeout', '5', '--max-time', '12',
         '--user-agent', 'NinjaKittyWeather/1.0', url],
        capture_output=True, text=True,
    )
    if response.returncode:
        raise RuntimeError(response.stderr.strip() or f'HTTP request failed ({response.returncode})')
    data = json.loads(response.stdout)
    if data.get('error'):
        raise ValueError(data.get('reason') or data.get('message') or 'Service returned an error')
    return data


def cached_fetch(url, max_age, force=False):
    directory = DATA / 'locations' if max_age is None else CACHE
    path = directory / (hashlib.sha256(url.encode()).hexdigest() + '.json')
    if not force:
        try:
            cached = json.loads(path.read_text())
            age = time.time() - cached['saved_at']
            if max_age is None or 0 <= age < max_age:
                return cached['data']
        except FileNotFoundError:
            pass
        except (OSError, ValueError, KeyError, TypeError) as error:
            print('Weather cache read failed: ' + str(error), file=sys.stderr)
    data = fetch(url)
    temporary = None
    try:
        directory.mkdir(parents=True, exist_ok=True)
        fd, temporary = tempfile.mkstemp(dir=directory)
        with os.fdopen(fd, 'w') as stream:
            json.dump({'saved_at': time.time(), 'data': data}, stream)
        os.replace(temporary, path)
    except OSError as error:
        # A cache is optional; successful live data is still useful.
        print('Weather cache write failed: ' + str(error), file=sys.stderr)
    finally:
        if temporary and os.path.exists(temporary):
            os.unlink(temporary)
    return data


def settings():
    try:
        return json.loads(SETTINGS.read_text())
    except FileNotFoundError:
        return {'automatic': True, 'city': 'Dublin, Ireland'}


def save_settings(value):
    DATA.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(dir=DATA)
    try:
        with os.fdopen(fd, 'w') as stream:
            json.dump(value, stream)
        os.replace(temporary, SETTINGS)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def geocode(city, force=False):
    results = cached_fetch('https://geocoding-api.open-meteo.com/v1/search?' + urlencode({'name': city, 'count': 1, 'language': 'en'}), None, force).get('results', [])
    if not results:
        raise ValueError('Location not found. Try a city followed by its country.')
    place = results[0]
    return {'latitude': place['latitude'], 'longitude': place['longitude'], 'name': ', '.join(dict.fromkeys(filter(None, [place['name'], place.get('admin1'), place.get('country')])))}


def location(config, force=False):
    if config['automatic']:
        try:
            place = cached_fetch('https://ipapi.co/json/', None, force)
            lat, lon = float(place['latitude']), float(place['longitude'])
            if not (-90 <= lat <= 90 and -180 <= lon <= 180):
                raise ValueError('Invalid automatic coordinates')
            return {'latitude': lat, 'longitude': lon, 'name': ', '.join(filter(None, [place.get('city'), place.get('country_name')])) or 'Current area'}, 'Approximate location from IP'
        except Exception as error:
            print('Automatic location failed: ' + str(error), file=sys.stderr)
            return geocode(config['city'], force), 'Automatic location unavailable; using saved city'
    return geocode(config['city'], force), 'Saved location'


def forecast(place, force=False):
    params = {
        'latitude': place['latitude'], 'longitude': place['longitude'],
        'current': 'weather_code,is_day',
        'hourly': 'apparent_temperature,precipitation_probability,weather_code,is_day',
        'daily': 'weather_code,apparent_temperature_max,apparent_temperature_min,precipitation_probability_max',
        'temperature_unit': 'fahrenheit', 'wind_speed_unit': 'mph',
        'timezone': 'auto', 'forecast_days': 3,
    }
    return cached_fetch('https://api.open-meteo.com/v1/forecast?' + urlencode(params), 600, force)


def condition(code, day=True):
    if code == 0:
        return ('☀️' if day else '🌙', 'Clear')
    if code in (1, 2):
        return ('🌤️' if day else '☁️', 'Partly cloudy')
    if code == 3:
        return '☁️', 'Overcast'
    if code in (45, 48):
        return '🌫️', 'Fog'
    if code in (51, 53, 55, 56, 57):
        return '🌦️', 'Drizzle'
    if code in (61, 63, 65, 66, 67, 80, 81, 82):
        return '🌧️', 'Rain'
    if code in (71, 73, 75, 77, 85, 86):
        return '🌨️', 'Snow'
    if code in (95, 96, 99):
        return '⛈️', 'Thunderstorms'
    return '🌡️', 'Unknown conditions'


def number(value, suffix=''):
    return '—' if value is None else f'{round(value)}{suffix}'


def label(text, size=13, **extra):
    return {'type': 'label', 'text': text, 'font': {'size': size}, **extra}


def render(data):
    current, hourly, daily = data['current'], data['hourly'], data['daily']
    now = datetime.fromisoformat(current['time'])
    # API times are local to the forecast, independent of the Mac's timezone.
    current_hour = now.replace(minute=0, second=0, microsecond=0)
    indices = [i for i, value in enumerate(hourly['time']) if datetime.fromisoformat(value) >= current_hour][:16]
    hours = []
    blocks = []
    for offset in range(0, len(indices), 4):
        block = indices[offset:offset + 4]
        start = datetime.fromisoformat(hourly['time'][block[0]])
        end = datetime.fromisoformat(hourly['time'][block[-1]])
        temperatures = [hourly['apparent_temperature'][i] for i in block if hourly['apparent_temperature'][i] is not None]
        rain = [hourly['precipitation_probability'][i] for i in block if hourly['precipitation_probability'][i] is not None]
        # Use conditions from the rainiest hour to match the block's rain value.
        representative = max(block, key=lambda i: hourly['precipitation_probability'][i] if hourly['precipitation_probability'][i] is not None else -1)
        symbol, name = condition(hourly['weather_code'][representative], hourly['is_day'][representative])
        span = start.strftime('%-I%p') if len(block) == 1 else start.strftime('%-I%p') + '–' + end.strftime('%-I%p')
        tooltip = start.strftime('%a %-d %b, %-I %p') + ' to ' + end.strftime('%a %-d %b, %-I %p') + ' · ' + name
        blocks.append({'span': span, 'tooltip': tooltip, 'symbol': symbol, 'temperature': min(temperatures) if temperatures else None, 'rain': max(rain) if rain else None})
        hours.append({'type': 'view', 'layout': 'inline', 'direction': 'vertical', 'spacing': 5, 'padding': 8, 'components': [label(span, 11, tooltip=tooltip), label(symbol + ' ' + number(min(temperatures) if temperatures else None, '°'), 17, tooltip='Lowest feels-like temperature · ' + tooltip), label(number(max(rain) if rain else None, '% rain'), tooltip='Highest hourly rain probability')]})
    first = blocks[0] if blocks else {'span': 'Unavailable', 'tooltip': '', 'symbol': '🌡️', 'temperature': None, 'rain': None}
    days = [label('Day'), label('Conditions'), label('High / Low'), label('Rain')]
    for i, date in enumerate(daily['time'][:3]):
        symbol, name = condition(daily['weather_code'][i])
        days.extend([label('Today' if i == 0 else datetime.fromisoformat(date).strftime('%a, %b %-d')), label(symbol + ' ' + name), label(number(daily['apparent_temperature_max'][i], '°') + ' / ' + number(daily['apparent_temperature_min'][i], '°')), label(number(daily['precipitation_probability_max'][i], '%'))])
    return {
        'summary-heading': {'text': first['span'], 'tooltip': first['tooltip']},
        'summary': {'text': f'{first["symbol"]}  {number(first["temperature"], "°F")}'},
        'details': {'text': f'Max rain {number(first["rain"], "%")}'},
        'hourly': {'components': hours[1:]},
        'daily': {'components': days},
        'updated': {'text': f'As of {now.strftime("%-I:%M %p")} · {data["timezone"]} · All temperatures feel like °F'},
    }


def run(command, city=''):
    config = settings()
    if command == 'city':
        city = city.strip()
        if not city:
            raise ValueError('Enter a city first.')
        # Resolve and fetch before saving so a bad search preserves working settings.
        place = geocode(city)
        mode = 'Saved location'
        config = {'automatic': False, 'city': city}
    elif command in ('load', 'refresh', 'automatic'):
        if command == 'automatic':
            config['automatic'] = True
        place, mode = location(config, force=command in ('refresh', 'automatic'))
    else:
        raise ValueError('Unknown weather action')
    data = forecast(place, force=command in ('refresh', 'automatic'))
    ids = render(data)
    if command in ('city', 'automatic'):
        save_settings(config)
    ids.update({name: {'enabled': True} for name in CONTROLS})
    ids.update({'location': {'text': place['name']}, 'mode': {'text': mode}, 'city': {'text': config['city'], 'enabled': True}, 'status': {'text': '', 'hidden': True}})
    return {'update': {'ids': ids, 'relayout': True}, 'window': {'resize': {'height': 'auto'}}}


if __name__ == '__main__':
    try:
        result = run(*sys.argv[1:])
    except Exception as error:
        print('Weather: ' + str(error), file=sys.stderr)
        ids = {name: {'enabled': True} for name in CONTROLS}
        ids['status'] = {'text': 'Could not load weather: ' + str(error), 'hidden': False, 'colour': 'systemRedColor'}
        result = {'update': {'ids': ids, 'relayout': True}}
    # Alfred UI needs a successful script exit to process error-display JSON too.
    print(json.dumps(result, ensure_ascii=False))
