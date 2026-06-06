import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from luthor.tools.weather_tool import clear_weather_cache, get_weather


class WeatherToolTests(unittest.TestCase):
    def setUp(self):
        clear_weather_cache()

    def tearDown(self):
        clear_weather_cache()

    @patch("luthor.tools.weather_tool.httpx.Client")
    def test_get_weather_parses_open_meteo_response(self, client_cls):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "current": {
                "temperature_2m": 12.5,
                "wind_speed_10m": 8.0,
                "weather_code": 3,
            }
        }
        mock_response.raise_for_status.return_value = None

        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client.get.return_value = mock_response
        client_cls.return_value = mock_client

        data = get_weather(48.85, 2.35)
        self.assertEqual(data["temperature_c"], 12.5)
        self.assertEqual(data["wind_speed_kmh"], 8.0)
        self.assertEqual(data["weather_code"], 3)
        self.assertEqual(data["source"], "open-meteo")

    @patch("luthor.tools.weather_tool.httpx.Client")
    def test_get_weather_uses_cache(self, client_cls):
        mock_response = MagicMock()
        mock_response.json.return_value = {"current": {"temperature_2m": 1.0}}
        mock_response.raise_for_status.return_value = None

        mock_client = MagicMock()
        mock_client.__enter__.return_value = mock_client
        mock_client.get.return_value = mock_response
        client_cls.return_value = mock_client

        get_weather(10.0, 20.0)
        get_weather(10.0, 20.0)
        self.assertEqual(mock_client.get.call_count, 1)


if __name__ == "__main__":
    unittest.main()
