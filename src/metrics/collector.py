"""
Prometheus metrics collector for weather data
"""
import logging
from typing import Optional
from prometheus_client.core import GaugeMetricFamily, InfoMetricFamily
from prometheus_client.registry import Collector

from ..scraper import WeatherScraper, WeatherData

logger = logging.getLogger(__name__)


class WeatherCollector(Collector):
    """
    Prometheus collector for weather station metrics
    """

    def __init__(self, scraper: WeatherScraper, station_name: str = "roquefort_les_pins"):
        self.scraper = scraper
        self.station_name = station_name

    def collect(self):
        """
        Collect metrics from weather station
        Called by prometheus_client when /metrics is scraped
        """
        # Scrape fresh data
        weather = self.scraper.scrape()

        if weather is None:
            logger.warning("No weather data available")
            # Return scrape failure metric
            yield from self._scrape_metrics(success=False)
            return

        # Temperature metrics
        temp = GaugeMetricFamily(
            'weather_temperature_celsius',
            'Temperature in Celsius',
            labels=['station', 'type']
        )
        temp.add_metric([self.station_name, 'current'], weather.temperature.current)
        temp.add_metric([self.station_name, 'min'], weather.temperature.min)
        temp.add_metric([self.station_name, 'max'], weather.temperature.max)
        temp.add_metric([self.station_name, 'average'], weather.temperature.average)
        yield temp

        # Humidity metrics
        humidity = GaugeMetricFamily(
            'weather_humidity_percent',
            'Relative humidity in percent',
            labels=['station', 'type']
        )
        humidity.add_metric([self.station_name, 'current'], weather.humidity.current)
        humidity.add_metric([self.station_name, 'min'], weather.humidity.min)
        humidity.add_metric([self.station_name, 'max'], weather.humidity.max)
        yield humidity

        # Pressure metrics
        pressure = GaugeMetricFamily(
            'weather_pressure_hpa',
            'Atmospheric pressure in hPa',
            labels=['station', 'type']
        )
        pressure.add_metric([self.station_name, 'current'], weather.pressure.current)
        pressure.add_metric([self.station_name, 'min'], weather.pressure.min)
        pressure.add_metric([self.station_name, 'max'], weather.pressure.max)
        yield pressure

        # Pressure trend
        pressure_trend = GaugeMetricFamily(
            'weather_pressure_trend_hpa',
            'Atmospheric pressure trend (6h) in hPa',
            labels=['station']
        )
        pressure_trend.add_metric([self.station_name], weather.pressure.trend)
        yield pressure_trend

        # Wind metrics
        wind_speed = GaugeMetricFamily(
            'weather_wind_speed_kmh',
            'Wind speed in km/h',
            labels=['station', 'type']
        )
        wind_speed.add_metric([self.station_name, 'current'], weather.wind.speed)
        wind_speed.add_metric([self.station_name, 'average'], weather.wind.average)
        wind_speed.add_metric([self.station_name, 'gust_max'], weather.wind.gust_max)
        yield wind_speed

        # Wind direction
        wind_dir = GaugeMetricFamily(
            'weather_wind_direction_degrees',
            'Wind direction in degrees',
            labels=['station']
        )
        wind_dir.add_metric([self.station_name], weather.wind.direction)
        yield wind_dir

        # Rain metrics
        rain = GaugeMetricFamily(
            'weather_rain_mm',
            'Precipitation in mm',
            labels=['station', 'period']
        )
        rain.add_metric([self.station_name, 'last_hour'], weather.rain.last_hour)
        rain.add_metric([self.station_name, 'today'], weather.rain.today)
        rain.add_metric([self.station_name, '24h'], weather.rain.last_24h)
        rain.add_metric([self.station_name, 'month'], weather.rain.month)
        rain.add_metric([self.station_name, 'year'], weather.rain.year)
        yield rain

        # Rain rate
        rain_rate = GaugeMetricFamily(
            'weather_rain_rate_mmh',
            'Rainfall rate in mm/h',
            labels=['station', 'type']
        )
        rain_rate.add_metric([self.station_name, 'current'], weather.rain.rate)
        rain_rate.add_metric([self.station_name, 'max'], weather.rain.rate_max)
        yield rain_rate

        # Solar metrics
        solar = GaugeMetricFamily(
            'weather_solar_radiation_wm2',
            'Solar radiation in W/m²',
            labels=['station', 'type']
        )
        solar.add_metric([self.station_name, 'current'], weather.solar.radiation_current)
        solar.add_metric([self.station_name, 'max'], weather.solar.radiation_max)
        yield solar

        # Sunshine duration
        sunshine = GaugeMetricFamily(
            'weather_sunshine_minutes',
            'Sunshine duration in minutes',
            labels=['station', 'period']
        )
        sunshine.add_metric([self.station_name, 'today'], weather.solar.sunshine_today_minutes)
        sunshine.add_metric([self.station_name, 'month'], weather.solar.sunshine_month_minutes)
        sunshine.add_metric([self.station_name, 'year'], weather.solar.sunshine_year_minutes)
        yield sunshine

        # Dewpoint
        dewpoint = GaugeMetricFamily(
            'weather_dewpoint_celsius',
            'Dew point temperature in Celsius',
            labels=['station']
        )
        dewpoint.add_metric([self.station_name], weather.dewpoint)
        yield dewpoint

        # Heat index
        heat_index = GaugeMetricFamily(
            'weather_heat_index_celsius',
            'Heat index in Celsius',
            labels=['station']
        )
        heat_index.add_metric([self.station_name], weather.heat_index)
        yield heat_index

        # THSW index
        thsw = GaugeMetricFamily(
            'weather_thsw_index_celsius',
            'THSW index in Celsius',
            labels=['station']
        )
        thsw.add_metric([self.station_name], weather.thsw_index)
        yield thsw

        # Station info
        station_info = InfoMetricFamily(
            'weather_station',
            'Weather station information',
            labels=['station']
        )
        station_info.add_metric(
            [self.station_name],
            {
                'name': weather.station_info.name,
                'location': weather.station_info.location,
                'latitude': str(weather.station_info.latitude),
                'longitude': str(weather.station_info.longitude),
                'altitude': str(weather.station_info.altitude),
            }
        )
        yield station_info

        # Last update timestamp
        if weather.timestamp:
            last_update = GaugeMetricFamily(
                'weather_last_update_timestamp',
                'Timestamp of last weather data update',
                labels=['station']
            )
            last_update.add_metric([self.station_name], weather.timestamp.timestamp())
            yield last_update

        # Scrape metrics
        yield from self._scrape_metrics(success=True)

    def _scrape_metrics(self, success: bool):
        """Generate scraper health metrics"""
        scrape_success = GaugeMetricFamily(
            'weather_scrape_success',
            'Whether the last scrape was successful (1=success, 0=failure)',
            labels=['station']
        )
        scrape_success.add_metric([self.station_name], 1 if success else 0)
        yield scrape_success

        scrape_duration = GaugeMetricFamily(
            'weather_scrape_duration_seconds',
            'Duration of last scrape operation in seconds',
            labels=['station']
        )
        scrape_duration.add_metric([self.station_name], self.scraper.last_scrape_duration)
        yield scrape_duration

        cache_age = GaugeMetricFamily(
            'weather_cache_age_seconds',
            'Age of cached weather data in seconds',
            labels=['station']
        )
        cache_age.add_metric([self.station_name], self.scraper.cache_age_seconds)
        yield cache_age
