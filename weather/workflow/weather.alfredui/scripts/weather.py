#!/usr/bin/env python3
"""Weather data and native AlfredUI rendering, using only the standard library."""
from datetime import datetime
import json
import plistlib
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
CONTROLS = ('refresh', 'settings')
CONFIG_CONTROLS = ('city', 'use-city', 'automatic', 'temperature-unit', 'apply-settings')


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
        raise ValueError('City not found. Try ‘Dublin, Ireland’.')
    place = results[0]
    return {'latitude': place['latitude'], 'longitude': place['longitude'], 'city': place['name'], 'name': ', '.join(dict.fromkeys(filter(None, [place['name'], place.get('admin1'), place.get('country')])))}


def location(config, force=False):
    if config['automatic']:
        try:
            place = cached_fetch('https://ipapi.co/json/', None, force)
            lat, lon = float(place['latitude']), float(place['longitude'])
            if not (-90 <= lat <= 90 and -180 <= lon <= 180):
                raise ValueError('Invalid automatic coordinates')
            return {'latitude': lat, 'longitude': lon, 'city': place.get('city') or 'Current area', 'name': ', '.join(filter(None, [place.get('city'), place.get('country_name')])) or 'Current area'}, 'Approximate location from IP'
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


ANIMATIONS = {
    'clear-day': 'Sunshine', 'clear-night': 'Clear night',
    'partly-cloudy-day': 'Partly cloudy', 'partly-cloudy-night': 'Cloudy night',
    'overcast': 'Overcast', 'fog': 'Fog', 'drizzle': 'Drizzle',
    'rain': 'Rain', 'snow': 'Snow', 'thunderstorm': 'Thunderstorm',
}


def animation_name(code, day=True):
    if code == 0:
        return 'clear-day' if day else 'clear-night'
    if code in (1, 2):
        return 'partly-cloudy-day' if day else 'partly-cloudy-night'
    if code == 3:
        return 'overcast'
    if code in (45, 48):
        return 'fog'
    if code in (51, 53, 55, 56, 57):
        return 'drizzle'
    if code in (61, 63, 65, 66, 67, 80, 81, 82):
        return 'rain'
    if code in (71, 73, 75, 77, 85, 86):
        return 'snow'
    if code in (95, 96, 99):
        return 'thunderstorm'
    return None


def animated_image(name):
    return {'type': 'file', 'src': 'assets/' + name + '.gif'}


def number(value, suffix=''):
    return '—' if value is None else f'{round(value)}{suffix}'


def label(text, size=13, **extra):
    return {'type': 'label', 'text': text, 'font': {'size': size}, **extra}


def forecast_card(components):
    return {'type': 'view', 'layout': 'inline', 'direction': 'vertical',
            'spacing': 7, 'padding': 12, 'cornerradius': 12,
            'background': '#80808018', 'components': components}


def render(data, unit='fahrenheit'):
    unit_symbol = '°C' if unit == 'celsius' else '°F'

    def temperature(value, suffix='°'):
        if value is not None and unit == 'celsius':
            value = (value - 32) * 5 / 9
        return number(value, suffix)

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
        blocks.append({'span': span, 'tooltip': tooltip, 'symbol': symbol, 'code': hourly['weather_code'][representative], 'is_day': hourly['is_day'][representative], 'temperature': min(temperatures) if temperatures else None, 'rain': max(rain) if rain else None})
        hours.append(forecast_card([
            label(span, 12, colour='secondaryLabelColor', tooltip=tooltip),
            label(symbol + ' ' + temperature(min(temperatures) if temperatures else None), 24),
            label(number(max(rain) if rain else None, '% rain'), 12, colour='secondaryLabelColor', tooltip='Highest hourly rain probability'),
        ]))
    first = blocks[0] if blocks else {'span': 'Unavailable', 'tooltip': '', 'symbol': '🌡️', 'code': None, 'temperature': None, 'rain': None}
    animation = animation_name(first['code'], first.get('is_day', True))
    main_icon = [{'type': 'imageview', 'image': animated_image(animation), 'constraints': {'size': {'width': 56, 'height': 56}}, 'accessibility': {'label': ANIMATIONS[animation]}}] if animation else []
    days = []
    for i, date in enumerate(daily['time'][:3]):
        symbol, name = condition(daily['weather_code'][i])
        days.append({'type': 'view', 'layout': 'grid', 'cols': 4, 'rows': 1, 'spacing': 8, 'components': [
            label('Today' if i == 0 else datetime.fromisoformat(date).strftime('%a, %b %-d'), 12, colour='secondaryLabelColor'),
            label(symbol + ' ' + name, 13, colour='secondaryLabelColor'),
            label(temperature(daily['apparent_temperature_max'][i]) + ' / ' + temperature(daily['apparent_temperature_min'][i]), 14, constraints={'position': 'right'}, tooltip='High / Low feels-like temperature'),
            label(number(daily['precipitation_probability_max'][i], '% rain'), 12, colour='secondaryLabelColor', constraints={'position': 'right'}),
        ]})
    return {
        'summary-heading': {'text': first['span'], 'tooltip': first['tooltip']},
        'summary-icon': {'components': main_icon},
        'summary': {'text': temperature(first['temperature'], unit_symbol) if animation else f'{first["symbol"]}  {temperature(first["temperature"], unit_symbol)}'},
        'details': {'text': f'{number(first["rain"], "%")} rain'},
        'hourly': {'components': hours[1:]},
        'daily': {'components': days},
    }


def icon_preview(name='rain'):
    if name not in ANIMATIONS:
        raise ValueError('Unknown icon preview')
    return {'sheet': {'id': 'weather-preview', 'root': {
        'type': 'view', 'layout': 'inline', 'direction': 'vertical',
        'padding': 20, 'spacing': 16, 'components': [
            label('Weather icons', 20),
            label('Preview only · your forecast and location stay unchanged', 12, colour='secondaryLabelColor'),
            {'type': 'picker', 'selected': name,
             'items': [{'text': title, 'value': key} for key, title in ANIMATIONS.items()],
             'events': [{'triggers': 'changed', 'action': {'type': 'script', 'src': 'scripts/weather.py', 'args': ['preview-icon', '{value:self.selected.value}']}}]},
            {'id': 'preview-icon', 'type': 'imageview', 'image': animated_image(name),
             'constraints': {'size': {'width': 112, 'height': 112}, 'position': 'centre'},
             'accessibility': {'label': ANIMATIONS[name]}},
            {'type': 'button', 'text': 'Back to settings', 'constraints': {'position': 'right'},
             'events': [{'triggers': 'actioned', 'action': [
                 {'type': 'json', 'src': {'sheet': {'close': 'weather-preview'}}},
                 {'type': 'script', 'src': 'scripts/weather.py', 'args': ['config']},
             ]}]},
        ],
    }}}


def configuration(config):
    location_controls = json.loads((Path(__file__).resolve().parents[1] / 'components/location-settings.json').read_text())
    location_controls[0].update(font={'size': 12}, colour='secondaryLabelColor')
    location_controls[0]['text'] = 'Approximate location from IP' if config['automatic'] else 'Saved location'
    location_controls[1]['components'][0]['text'] = config['city']
    return {'sheet': {'id': 'weather-settings', 'root': {
        'type': 'view', 'layout': 'inline', 'direction': 'vertical',
        'padding': 20, 'spacing': 12, 'components': [
            label('Weather settings · ' + plistlib.loads((Path(__file__).resolve().parents[2] / 'info.plist').read_bytes())['version'], 20),
            forecast_card([label('Location', 14), *location_controls]),
            {'type': 'view', 'layout': 'border', 'padding': 12, 'cornerradius': 12, 'background': '#80808018', 'components': [
                label('Temperature', 14, constraints={'region': 'left', 'position': 'centre'}),
                {'id': 'temperature-unit', 'type': 'picker', 'selected': config.get('unit', 'fahrenheit'),
                 'constraints': {'region': 'right'},
                 'items': [{'text': 'Celsius (°C)', 'value': 'celsius'}, {'text': 'Fahrenheit (°F)', 'value': 'fahrenheit'}]},
            ]},
            label('Forecast by Open-Meteo · Location by ipapi', 11, colour='secondaryLabelColor'),
            {'id': 'settings-error', 'type': 'view', 'layout': 'inline', 'constraints': {'size': {'height': 36}}, 'components': []},
            {'type': 'view', 'layout': 'inline', 'spacing': 8, 'constraints': {'position': 'right'}, 'components': [
                {'type': 'button', 'text': 'Cancel', 'events': [{'triggers': 'actioned', 'action': {'type': 'json', 'src': {'sheet': {'close': 'weather-settings'}}}}]},
                {'id': 'apply-settings', 'type': 'button', 'text': 'Apply', 'events': [{'triggers': 'actioned', 'action': [
                    {'type': 'json', 'src': {'update': {'ids': {'apply-settings': {'enabled': False}}}}},
                    {'type': 'script', 'src': 'scripts/weather.py', 'args': ['unit', '{value:temperature-unit.selected.value}'], 'async': True},
                ]}]},
            ]},
        ],
    }}}


def run(command, city=''):
    if command == 'preview':
        return icon_preview()
    if command == 'preview-icon':
        if city not in ANIMATIONS:
            raise ValueError('Unknown icon preview')
        return {'update': {'ids': {'preview-icon': {'image': animated_image(city), 'accessibility': {'label': ANIMATIONS[city]}}}}}
    config = settings()
    if command == 'config':
        return configuration(config)
    if command == 'unit':
        if city not in ('celsius', 'fahrenheit'):
            raise ValueError('Choose Celsius or Fahrenheit')
        config['unit'] = city
        place, mode = location(config)
    elif command == 'city':
        city = city.strip()
        if not city:
            raise ValueError('Enter a city first.')
        # Resolve and fetch before saving so a bad search preserves working settings.
        place = geocode(city)
        mode = 'Saved location'
        config = {**config, 'automatic': False, 'city': city}
    elif command in ('load', 'refresh', 'automatic'):
        if command == 'automatic':
            config['automatic'] = True
        place, mode = location(config, force=command in ('refresh', 'automatic'))
    else:
        raise ValueError('Unknown weather action')
    data = forecast(place, force=command in ('refresh', 'automatic'))
    ids = render(data, config.get('unit', 'fahrenheit'))
    if command in ('city', 'automatic', 'unit'):
        save_settings(config)
    ids.update({name: {'enabled': True} for name in CONTROLS})
    ids.update({'location': {'text': place.get('city', place['name']), 'tooltip': place['name']}, 'status': {'components': []}})
    if command in ('city', 'automatic', 'unit'):
        ids.update({name: {'enabled': True} for name in CONFIG_CONTROLS})
        ids.update({'mode': {'text': mode}, 'city': {'text': config['city'], 'enabled': True}, 'settings-error': {'components': []}})
    result = {'update': {'ids': ids, 'relayout': True}, 'window': {'resize': {'height': 'auto'}}}
    if command == 'unit':
        result['sheet'] = {'close': 'weather-settings'}
    return result


if __name__ == '__main__':
    try:
        result = run(*sys.argv[1:])
    except Exception as error:
        print('Weather: ' + str(error), file=sys.stderr)
        ids = {name: {'enabled': True} for name in CONTROLS}
        ids['status'] = {'components': [label('Could not load weather: ' + str(error), 12, colour='systemRedColor', linebreak='wordwrap')]}
        if sys.argv[1] in ('city', 'automatic', 'unit'):
            ids.update({name: {'enabled': True} for name in CONFIG_CONTROLS})
            ids['settings-error'] = {'components': [label(str(error), 12, colour='systemRedColor', linebreak='wordwrap', tooltip=str(error), constraints={'size': {'height': 36}})]}
        result = {'update': {'ids': ids, 'relayout': True}}
    # Alfred UI needs a successful script exit to process error-display JSON too.
    print(json.dumps(result, ensure_ascii=False))
