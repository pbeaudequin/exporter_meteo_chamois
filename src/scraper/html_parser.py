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

    @staticmethod
    def _extract_duration_minutes(text: str) -> float:
        """
        Extract duration and convert to minutes
        Handles formats like: "2:27 h", "7:54 heures", "156:36 h", "2176:45 h"
        """
        try:
            # Look for pattern like "123:45" (hours:minutes)
            match = re.search(r'(\d+):(\d+)', text)
            if match:
                hours = int(match.group(1))
                minutes = int(match.group(2))
                return hours * 60 + minutes
            return 0.0
        except (ValueError, AttributeError):
            return 0.0

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

            # Extract sunshine and solar radiation data
            # Look for the solar radiation table with "Ensoleillement" text
            solar_section = soup.find_all(string=re.compile(r'Ensoleillement', re.IGNORECASE))

            if solar_section:
                # Get the parent table containing all solar data
                for elem in solar_section:
                    table = elem.find_parent('table')
                    if table:
                        table_text = table.get_text()

                        # Extract sunshine durations for different periods
                        # Format: "EnsoleillementAujourd'hui2:27 h (durée du jour: 09:16)"
                        # Note: The HTML has no spaces between "Ensoleillement" and the period name
                        sunshine_today = re.search(r"Aujourd[\u2019']hui\s*(\d+:\d+)\s*h", table_text, re.IGNORECASE)
                        if sunshine_today:
                            weather.solar.sunshine_today_minutes = self._extract_duration_minutes(sunshine_today.group(1))
                            logger.debug(f"Sunshine today: {weather.solar.sunshine_today_minutes} minutes")

                        sunshine_month = re.search(r"Mois\s*(\d+:\d+)\s*h", table_text, re.IGNORECASE)
                        if sunshine_month:
                            weather.solar.sunshine_month_minutes = self._extract_duration_minutes(sunshine_month.group(1))
                            logger.debug(f"Sunshine month: {weather.solar.sunshine_month_minutes} minutes")

                        sunshine_year = re.search(r"Ann[ée]e\s*(\d+:\d+)\s*h", table_text, re.IGNORECASE)
                        if sunshine_year:
                            weather.solar.sunshine_year_minutes = self._extract_duration_minutes(sunshine_year.group(1))
                            logger.debug(f"Sunshine year: {weather.solar.sunshine_year_minutes} minutes")

                        # Extract solar radiation max (24h)
                        # Format: "Energie max 24h</font><br><font size="4">557 W/m²"
                        solar_max = re.search(r"Energie max 24h.*?(\d+)\s*W/m", table_text, re.IGNORECASE)
                        if solar_max:
                            weather.solar.radiation_max = float(solar_max.group(1))
                            logger.debug(f"Solar radiation max: {weather.solar.radiation_max} W/m²")

                        # Extract current/average solar radiation
                        # Format: "Moyenne aujourd'hui</font><br><font size="4">167 W/m²"
                        solar_current = re.search(r"Moyenne aujourd'hui.*?(\d+)\s*W/m", table_text, re.IGNORECASE)
                        if solar_current:
                            weather.solar.radiation_current = float(solar_current.group(1))
                            logger.debug(f"Solar radiation current: {weather.solar.radiation_current} W/m²")

                        break  # We found the table, no need to continue

            weather.timestamp = datetime.now()

            # Log what we found
            logger.info(f"Parsed currant.html: temp={weather.temperature.current}°C, "
                       f"humidity={weather.humidity.current}%, pressure={weather.pressure.current}hPa, "
                       f"sunshine_today={weather.solar.sunshine_today_minutes}min")

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
