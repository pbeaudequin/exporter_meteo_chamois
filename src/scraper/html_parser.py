"""
HTML parser for weather station pages
"""
import re
import logging
from datetime import datetime
from typing import Optional
from bs4 import BeautifulSoup

from .models import (
    WeatherData, Temperature, Humidity, Pressure,
    Wind, Rain, Solar, StationInfo
)

logger = logging.getLogger(__name__)


class WeatherHTMLParser:
    """Parse weather data from HTML pages"""

    @staticmethod
    def _extract_float(text: str) -> float:
        """Extract float value from text (handles both dot and comma as decimal separator)"""
        try:
            # Replace comma with dot for French format, remove non-numeric characters except dots and minus
            cleaned = text.strip().replace(',', '.')
            cleaned = re.sub(r'[^\d.-]', '', cleaned)
            return float(cleaned) if cleaned else 0.0
        except (ValueError, AttributeError):
            return 0.0

    @staticmethod
    def _extract_int(text: str) -> int:
        """Extract integer value from text"""
        try:
            cleaned = re.sub(r'[^\d-]', '', text.strip())
            return int(cleaned) if cleaned else 0
        except (ValueError, AttributeError):
            return 0

    def parse_currant_html(self, html: str) -> WeatherData:
        """
        Parse the currant.html page
        Main source for current weather data
        """
        soup = BeautifulSoup(html, 'html.parser')
        weather = WeatherData()

        try:
            # Find all text content
            text = soup.get_text()
            logger.debug(f"HTML text length: {len(text)} characters")

            # Extract all numeric values with their context for better matching
            # Temperature - be more flexible with patterns
            # Note: French format uses comma as decimal separator (e.g., 18,1 °C)
            patterns = [
                # Temperature - look for "Actuel" followed by temperature
                (r'Actuel[\s\xa0]*(\d+[,.]?\d*)\s*°C', 'temperature.current'),
                # Min/Max with time (e.g., "Min.(08:20)13,8 °C")
                (r'Min\.\([^)]+\)(\d+[,.]?\d*)\s*°C', 'temperature.min'),
                (r'Max\.\([^)]+\)(\d+[,.]?\d*)\s*°C', 'temperature.max'),
                # Average (e.g., "Moyenne15,7 °C")
                (r'Moyenne[\s\xa0]*(\d+[,.]?\d*)\s*°C', 'temperature.average'),
                # Humidity (e.g., "Actuel 98 %")
                (r'Actuel[\s\xa0]*(\d+)\s*%', 'humidity.current'),
                (r'Min\.\([^)]+\)(\d+)\s*%', 'humidity.min'),
                (r'Max\.\([^)]+\)(\d+)\s*%', 'humidity.max'),
                # Pressure
                (r'(?:Pressure|Pression|Press)[\s:]+(\d{3,4}[,.]?\d*)\s*(?:hPa|mb)', 'pressure.current'),
                (r'([+-]\d+[,.]?\d*)\s*hPa', 'pressure.trend'),
                # Wind
                (r'(?:Wind|Vent)[\s:]+(\d+[,.]?\d*)\s*km/?h', 'wind.speed'),
                (r'(?:Gust|Rafale)[\s:]+(\d+[,.]?\d*)\s*km', 'wind.gust_max'),
                # Rain
                (r'(?:Rain|Pluie).*?(?:Today|Aujourd\'hui)[\s:]+(\d+[,.]?\d*)\s*mm', 'rain.today'),
                # Dewpoint
                (r'(?:Dew\s*Point|Point\s*de\s*rosée)[\s:]+(\d+[,.]?\d*)', 'dewpoint'),
            ]

            for pattern, field in patterns:
                match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
                if match:
                    value_str = match.group(1).replace(',', '.')  # Convert French format to float
                    logger.debug(f"Found {field}: {value_str}")

                    try:
                        # Set the value based on the field path
                        parts = field.split('.')
                        if len(parts) == 2:
                            obj = getattr(weather, parts[0])
                            if 'humidity' in field:
                                setattr(obj, parts[1], int(float(value_str)))
                            else:
                                setattr(obj, parts[1], float(value_str))
                        else:
                            setattr(weather, field, float(value_str))
                    except (ValueError, AttributeError) as e:
                        logger.warning(f"Failed to set {field}={value_str}: {e}")

            weather.timestamp = datetime.now()

            # Log what we found
            logger.info(f"Parsed currant.html: temp={weather.temperature.current}°C, "
                       f"humidity={weather.humidity.current}%, pressure={weather.pressure.current}hPa")

        except Exception as e:
            logger.error(f"Error parsing currant.html: {e}", exc_info=True)

        return weather

    def parse_valeurs_html(self, html: str, weather: Optional[WeatherData] = None) -> WeatherData:
        """
        Parse the valeurs.htm page
        Enriches data with additional metrics
        """
        if weather is None:
            weather = WeatherData()

        soup = BeautifulSoup(html, 'html.parser')

        try:
            # Look for table rows with data
            rows = soup.find_all('tr')

            for row in rows:
                cells = row.find_all('td')
                if len(cells) < 2:
                    continue

                label = cells[0].get_text(strip=True).lower()
                value = cells[1].get_text(strip=True)

                # Temperature
                if 'temperature' in label and 'air' not in label:
                    weather.temperature.current = self._extract_float(value)

                # Humidity
                elif 'humidity' in label or 'humidit' in label:
                    weather.humidity.current = self._extract_int(value)

                # Pressure
                elif 'pressure' in label or 'pression' in label:
                    weather.pressure.current = self._extract_float(value)

                # Wind speed
                elif 'wind' in label and '10-min' in label:
                    weather.wind.speed = self._extract_float(value)

                # Rainfall
                elif 'daily' in label and 'rain' in label:
                    weather.rain.today = self._extract_float(value)
                elif 'monthly' in label:
                    weather.rain.month = self._extract_float(value)
                elif 'yearly' in label:
                    weather.rain.year = self._extract_float(value)

                # Rain rate
                elif 'rain rate' in label or 'rainfall rate' in label:
                    weather.rain.rate = self._extract_float(value)

                # Dewpoint
                elif 'dew point' in label:
                    weather.dewpoint = self._extract_float(value)

                # Heat index
                elif 'heat index' in label:
                    weather.heat_index = self._extract_float(value)

                # THSW
                elif 'thsw' in label:
                    weather.thsw_index = self._extract_float(value)

            # Extract min/max values from the page
            text = soup.get_text()

            # Temperature high/low
            temp_high = re.search(r'High\s+(\d+\.?\d*)\s*°C', text, re.IGNORECASE)
            if temp_high:
                weather.temperature.max = float(temp_high.group(1))

            temp_low = re.search(r'Low\s+(\d+\.?\d*)\s*°C', text, re.IGNORECASE)
            if temp_low:
                weather.temperature.min = float(temp_low.group(1))

            # Humidity high/low
            hum_high = re.search(r'High\s+(\d+)\s*%', text)
            if hum_high:
                weather.humidity.max = int(hum_high.group(1))

            hum_low = re.search(r'Low\s+(\d+)\s*%', text)
            if hum_low:
                weather.humidity.min = int(hum_low.group(1))

            # Wind gust
            gust = re.search(r'(\d+\.?\d*)\s*km/hr\s+at', text)
            if gust:
                weather.wind.gust_max = float(gust.group(1))

            # Pressure range
            pressure_high = re.search(r'(\d{4}\.\d+)\s*hPa.*?(\d{4}\.\d+)\s*hPa', text)
            if pressure_high:
                weather.pressure.max = float(pressure_high.group(1))
                weather.pressure.min = float(pressure_high.group(2))

            # Max rainfall rate
            max_rain = re.search(r'(\d+\.?\d*)\s*mm/hr', text)
            if max_rain:
                weather.rain.rate_max = float(max_rain.group(1))

            if weather.timestamp is None:
                weather.timestamp = datetime.now()

        except Exception as e:
            logger.error(f"Error parsing valeurs.htm: {e}")

        return weather
