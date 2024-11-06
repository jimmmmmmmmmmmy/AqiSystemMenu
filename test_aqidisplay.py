import unittest
import mock
from datetime import datetime
import tempfile
import os
from app import AQIDisplay

class TestAQIDisplay(unittest.TestCase):
    def setUp(self):
        self.app = AQIDisplay()

    def tearDown(self):
        if hasattr(self, 'app') and self.app.db_connection:
            self.app.db_connection.close()

    def test_parse_api_data(self):
        """Test parsing of API data"""
        test_data = {
            'aqi': 50,
            'iaqi': {
                'pm25': {'v': 20},
                'pm10': {'v': 30},
                't': {'v': 25},
                'h': {'v': 60}
            },
            'city': {'name': 'Test City'},
            'forecast': {'daily': {}}
        }

        result = self.app.parse_api_data(test_data)

        self.assertEqual(result['aqi'], 50)
        self.assertEqual(result['visualization_data']['PM2.5']['current'], 20)
        self.assertEqual(result['visualization_data']['PM10']['current'], 30)
        self.assertEqual(result['visualization_data']['Temp.']['current'], 25)
        self.assertEqual(result['visualization_data']['Humidity']['current'], 60)

    def test_title_formatting(self):
        """Test menu bar title formatting"""
        test_data = {
            'aqi': 50,
            'iaqi': {
                'pm25': {'v': 20},
                't': {'v': 25},
                'h': {'v': 60}
            }
        }
        
        self.app.cached_data = test_data
        
        # Test with only AQI shown
        self.app.format_options = {key: False for key in self.app.format_options}
        self.app.format_options['AQI'] = True
        self.app.update_title()
        self.assertEqual(self.app.title, "AQI: 50")

        # Test with AQI and temperature (°F)
        self.app.format_options['Temperature'] = True
        self.app.temperature_unit = "°F"
        self.app.update_title()
        self.assertEqual(self.app.title, "AQI: 50 | 77.0°F")

        # Test with AQI and temperature (°C)
        self.app.temperature_unit = "°C"
        self.app.update_title()
        self.assertEqual(self.app.title, "AQI: 50 | 25°C")

    @mock.patch('requests.get')
    def test_get_aqi_data(self, mock_get):
        """Test fetching AQI data"""
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'status': 'ok',
            'data': {
                'aqi': 50,
                'city': {'name': 'Greatest City in the WORLD'},
                'iaqi': {
                    'pm25': {'v': 20},
                    't': {'v': 25},
                    'h': {'v': 60}
                }
            }
        }
        mock_get.return_value = mock_response

        result = self.app.get_aqi_data("Greatest City in the WORLD")

        self.assertIsNotNone(result)
        self.assertEqual(result['aqi'], 50)
        self.assertEqual(result['city']['name'], 'Greatest City in the WORLD')

if __name__ == '__main__':
    unittest.main()