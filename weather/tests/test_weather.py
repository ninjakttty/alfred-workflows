import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('weather', Path(__file__).parents[1] / 'workflow/weather.alfredui/scripts/weather.py')
weather = importlib.util.module_from_spec(spec)
spec.loader.exec_module(weather)


class WeatherTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        cache = patch.object(weather, 'CACHE', Path(directory.name))
        cache.start()
        self.addCleanup(cache.stop)
        data = patch.object(weather, 'DATA', Path(directory.name) / 'data')
        data.start()
        self.addCleanup(data.stop)

    def test_automatic_failure_uses_saved_city(self):
        with patch.object(weather, 'fetch', side_effect=RuntimeError('offline')), patch.object(weather, 'geocode', return_value={'name': 'Dublin'}) as lookup:
            place, mode = weather.location({'automatic': True, 'city': 'Dublin, Ireland'})
            self.assertEqual(place['name'], 'Dublin')
            lookup.assert_called_once_with('Dublin, Ireland', False)
            self.assertIn('unavailable', mode)

    def test_invalid_coordinates_fall_back(self):
        with patch.object(weather, 'fetch', return_value={'latitude': 999, 'longitude': 0}), patch.object(weather, 'geocode', return_value={'name': 'Saved'}):
            self.assertEqual(weather.location({'automatic': True, 'city': 'Saved'})[0]['name'], 'Saved')

    def test_unknown_city_does_not_change_settings(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(weather, 'DATA', Path(directory)), patch.object(weather, 'SETTINGS', Path(directory) / 'settings.json'):
                weather.save_settings({'automatic': False, 'city': 'Dublin'})
                with patch.object(weather, 'fetch', return_value={'results': []}):
                    with self.assertRaisesRegex(ValueError, 'City not found'):
                        weather.run('city', 'unknown')
                self.assertEqual(weather.settings()['city'], 'Dublin')

    def test_forecast_requests_fahrenheit_and_all_sections(self):
        with patch.object(weather, 'fetch', return_value={}) as fetch:
            weather.forecast({'latitude': 53.3, 'longitude': -6.2})
            url = fetch.call_args.args[0]
            self.assertIn('temperature_unit=fahrenheit', url)
            self.assertIn('current=', url)
            self.assertIn('hourly=', url)
            self.assertIn('daily=', url)
            self.assertIn('timezone=auto', url)
            self.assertIn('forecast_days=3', url)
            self.assertIn('apparent_temperature_max', url)
            self.assertIn('apparent_temperature_min', url)
            self.assertNotIn('temperature_2m', url)

    def test_render_uses_forecast_local_time_and_handles_missing_values(self):
        data = {
            'current': {'time': '2026-11-24T09:15', 'weather_code': 0, 'is_day': 0, 'temperature_2m': 45, 'apparent_temperature': None, 'wind_speed_10m': 3, 'relative_humidity_2m': 80},
            'hourly': {'time': ['2026-11-24T09:00', '2026-11-24T10:00'], 'weather_code': [0, 3], 'is_day': [1, 1], 'temperature_2m': [45, 46], 'apparent_temperature': [39, 40], 'precipitation_probability': [0, None]},
            'daily': {'time': ['2026-11-24'], 'weather_code': [3], 'temperature_2m_max': [50], 'temperature_2m_min': [40], 'apparent_temperature_max': [46], 'apparent_temperature_min': [35], 'precipitation_probability_max': [30]},
            'timezone': 'Europe/Dublin',
        }
        result = weather.render(data)
        self.assertIn('39°F', result['summary']['text'])
        self.assertIn('0% rain', result['details']['text'])
        self.assertEqual(len(result['hourly']['components']), 0)
        self.assertEqual(result['daily']['components'][0]['components'][2]['text'], '46° / 35°')
        self.assertEqual(len(result['daily']['components']), 1)

    def test_fresh_cache_avoids_network_and_expiry_fetches_again(self):
        with patch.object(weather, 'fetch', return_value={'value': 1}) as fetch, patch.object(weather.time, 'time', return_value=1000):
            self.assertEqual(weather.cached_fetch('https://example.test', 600), {'value': 1})
            weather.cached_fetch('https://example.test', 600)
            self.assertEqual(fetch.call_count, 1)
        with patch.object(weather, 'fetch', return_value={'value': 2}) as fetch, patch.object(weather.time, 'time', return_value=1600):
            self.assertEqual(weather.cached_fetch('https://example.test', 600), {'value': 2})
            fetch.assert_called_once()

    def test_force_refresh_bypasses_fresh_cache(self):
        with patch.object(weather, 'fetch', return_value={'value': 1}) as fetch:
            weather.cached_fetch('https://example.test', 600)
            weather.cached_fetch('https://example.test', 600, force=True)
            self.assertEqual(fetch.call_count, 2)

    def test_different_locations_have_separate_forecast_caches(self):
        with patch.object(weather, 'fetch', return_value={'current': {}}) as fetch:
            weather.forecast({'latitude': 1, 'longitude': 2})
            weather.forecast({'latitude': 3, 'longitude': 4})
            weather.forecast({'latitude': 1, 'longitude': 2})
            self.assertEqual(fetch.call_count, 2)

    def test_location_data_never_expires_but_force_updates_it(self):
        with patch.object(weather, 'fetch', return_value={'latitude': 53}) as fetch, patch.object(weather.time, 'time', return_value=1000):
            weather.cached_fetch('https://location.test', None)
            fetch.assert_called_once()
        with patch.object(weather, 'fetch', return_value={'latitude': 54}) as fetch, patch.object(weather.time, 'time', return_value=10**12):
            self.assertEqual(weather.cached_fetch('https://location.test', None), {'latitude': 53})
            fetch.assert_not_called()
            self.assertEqual(weather.cached_fetch('https://location.test', None, force=True), {'latitude': 54})
            fetch.assert_called_once()
        self.assertTrue(list((weather.DATA / 'locations').glob('*.json')))
        self.assertFalse(list(weather.CACHE.glob('*.json')))

    def test_three_four_hour_blocks_show_minimum_temperature_and_maximum_rain(self):
        from datetime import datetime, timedelta
        start = datetime(2026, 11, 24, 22)
        hourly = {
            'time': [(start + timedelta(hours=i)).isoformat(timespec='minutes') for i in range(30)],
            'apparent_temperature': [50, 41, None, 45] + [40] * 26,
            'precipitation_probability': [10, 20, 80, None] + [30] * 26,
            'weather_code': [0, 0, 61, 0] + [3] * 26,
            'is_day': [0] * 30,
        }
        data = {'current': {'time': start.isoformat(), 'weather_code': 0, 'apparent_temperature': 50, 'wind_speed_10m': 1, 'relative_humidity_2m': 80}, 'hourly': hourly, 'daily': {'time': []}, 'timezone': 'Europe/Dublin'}
        result = weather.render(data)
        cards = result['hourly']['components']
        self.assertEqual(len(cards), 3)
        self.assertEqual(result['summary-heading']['text'], '10PM–1AM')
        self.assertEqual(result['summary']['text'], '41°F')
        self.assertEqual(result['summary-icon']['components'][0]['type'], 'imageview')
        self.assertEqual(result['details']['text'], '80% rain')
        self.assertEqual(cards[0]['components'][0]['text'], '2AM–5AM')
        self.assertEqual(cards[-1]['components'][0]['text'], '10AM–1PM')
        hourly['apparent_temperature'] = [None] * 30
        hourly['precipitation_probability'] = [None] * 30
        empty = weather.render(data)['hourly']['components'][0]['components']
        self.assertIn('—', empty[1]['text'])
        self.assertEqual(empty[2]['text'], '—')

    def test_celsius_converts_summary_blocks_and_daily_values(self):
        from datetime import datetime, timedelta
        start = datetime(2026, 11, 24, 10)
        data = {
            'current': {'time': start.isoformat()},
            'hourly': {'time': [(start + timedelta(hours=i)).isoformat() for i in range(16)], 'apparent_temperature': [32] * 16, 'precipitation_probability': [20] * 16, 'weather_code': [3] * 16, 'is_day': [1] * 16},
            'daily': {'time': ['2026-11-24'], 'weather_code': [3], 'apparent_temperature_max': [50], 'apparent_temperature_min': [14], 'precipitation_probability_max': [20]},
            'timezone': 'Europe/Dublin',
        }
        result = weather.render(data, 'celsius')
        self.assertEqual(result['summary']['text'], '0°C')
        self.assertEqual(result['hourly']['components'][0]['components'][1]['text'], '☁️ 0°')
        self.assertEqual(result['daily']['components'][0]['components'][2]['text'], '10° / -10°')
        self.assertEqual(data['hourly']['apparent_temperature'][0], 32)

    def test_unit_change_persists_and_preserves_location(self):
        with patch.object(weather, 'SETTINGS', weather.DATA / 'settings.json'):
            weather.save_settings({'automatic': False, 'city': 'Stillorgan, Ireland'})
            with patch.object(weather, 'location', return_value=({'name': 'Stillorgan'}, 'Saved location')), patch.object(weather, 'forecast', return_value={}), patch.object(weather, 'render', return_value={}):
                result = weather.run('unit', 'celsius')
            self.assertEqual(weather.settings(), {'automatic': False, 'city': 'Stillorgan, Ireland', 'unit': 'celsius'})
            self.assertEqual(result['sheet']['close'], 'weather-settings')
            with self.assertRaises(ValueError):
                weather.run('unit', 'kelvin')
            self.assertEqual(weather.settings()['unit'], 'celsius')

    def test_main_animation_changes_with_conditions_and_falls_back_for_unknown(self):
        data = {
            'current': {'time': '2026-11-24T10:00'},
            'hourly': {'time': ['2026-11-24T10:00'], 'apparent_temperature': [44], 'precipitation_probability': [80], 'weather_code': [61], 'is_day': [1]},
            'daily': {'time': []},
        }
        rainy = weather.render(data)
        self.assertEqual(rainy['summary']['text'], '44°F')
        self.assertEqual(rainy['summary-icon']['components'][0]['image']['src'], 'assets/rain.gif')
        for code, asset in [(0, 'clear-day'), (95, 'thunderstorm'), (71, 'snow')]:
            data['hourly']['weather_code'] = [code]
            result = weather.render(data)
            self.assertEqual(result['summary-icon']['components'][0]['image']['src'], 'assets/' + asset + '.gif')
            self.assertEqual(result['summary']['text'], '44°F')
        data['hourly']['weather_code'] = [999]
        unknown = weather.render(data)
        self.assertEqual(unknown['summary-icon']['components'], [])
        self.assertIn('🌡️', unknown['summary']['text'])

    def test_every_known_condition_has_a_bundled_animation(self):
        groups = {0: 'clear-day', 1: 'partly-cloudy-day', 2: 'partly-cloudy-day', 3: 'overcast', 45: 'fog', 48: 'fog', 51: 'drizzle', 53: 'drizzle', 55: 'drizzle', 56: 'drizzle', 57: 'drizzle', 61: 'rain', 63: 'rain', 65: 'rain', 66: 'rain', 67: 'rain', 80: 'rain', 81: 'rain', 82: 'rain', 71: 'snow', 73: 'snow', 75: 'snow', 77: 'snow', 85: 'snow', 86: 'snow', 95: 'thunderstorm', 96: 'thunderstorm', 99: 'thunderstorm'}
        for code, name in groups.items():
            self.assertEqual(weather.animation_name(code), name)
        self.assertEqual(weather.animation_name(0, False), 'clear-night')
        self.assertEqual(weather.animation_name(2, False), 'partly-cloudy-night')
        self.assertIsNone(weather.animation_name(999))
        for name in weather.ANIMATIONS:
            path = Path(weather.__file__).parents[1] / 'assets' / (name + '.gif')
            self.assertTrue(path.read_bytes().startswith(b'GIF'))

    def test_preview_does_not_fetch_weather_or_change_settings(self):
        with patch.object(weather, 'fetch') as fetch, patch.object(weather, 'save_settings') as save:
            self.assertEqual(weather.run('preview')['sheet']['id'], 'weather-preview')
            for name in weather.ANIMATIONS:
                result = weather.run('preview-icon', name)
                self.assertEqual(result['update']['ids']['preview-icon']['image']['src'], 'assets/' + name + '.gif')
            fetch.assert_not_called()
            save.assert_not_called()

    def test_title_uses_exact_city_name_and_preserves_full_location_tooltip(self):
        response = {'results': [{'name': 'Washington, D.C.', 'admin1': 'District of Columbia', 'country': 'United States', 'latitude': 38.9, 'longitude': -77.0}]}
        with patch.object(weather, 'fetch', return_value=response):
            place = weather.geocode('Washington')
        self.assertEqual(place['city'], 'Washington, D.C.')
        with patch.object(weather, 'settings', return_value={'automatic': False, 'city': 'Washington'}), patch.object(weather, 'location', return_value=(place, 'Saved location')), patch.object(weather, 'forecast', return_value={}), patch.object(weather, 'render', return_value={}):
            title = weather.run('load')['update']['ids']['location']
        self.assertEqual(title['text'], 'Washington, D.C.')
        self.assertIn('United States', title['tooltip'])
