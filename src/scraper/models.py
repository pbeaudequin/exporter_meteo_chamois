"""
Data models for weather station data
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Temperature:
    """Temperature data in Celsius"""
    current: float = 0.0
    min: float = 0.0
    max: float = 0.0
    average: float = 0.0


@dataclass
class Humidity:
    """Humidity data in percentage"""
    current: int = 0
    min: int = 0
    max: int = 0


@dataclass
class Pressure:
    """Atmospheric pressure in hPa"""
    current: float = 0.0
    trend: float = 0.0
    min: float = 0.0
    max: float = 0.0


@dataclass
class Wind:
    """Wind data in km/h and degrees"""
    speed: float = 0.0
    direction: float = 0.0
    gust_max: float = 0.0
    average: float = 0.0
    direction_text: str = "N"


@dataclass
class Rain:
    """Precipitation data in mm"""
    last_hour: float = 0.0
    today: float = 0.0
    last_24h: float = 0.0
    month: float = 0.0
    year: float = 0.0
    rate: float = 0.0
    rate_max: float = 0.0


@dataclass
class Solar:
    """Solar radiation data"""
    radiation_current: float = 0.0
    radiation_max: float = 0.0
    sunshine_minutes: float = 0.0


@dataclass
class StationInfo:
    """Station metadata"""
    name: str = "La Rose des Vents"
    location: str = "Roquefort les Pins"
    latitude: float = 43.669
    longitude: float = 7.086
    altitude: float = 193.0


@dataclass
class WeatherData:
    """Complete weather station data"""
    temperature: Temperature = field(default_factory=Temperature)
    humidity: Humidity = field(default_factory=Humidity)
    pressure: Pressure = field(default_factory=Pressure)
    wind: Wind = field(default_factory=Wind)
    rain: Rain = field(default_factory=Rain)
    solar: Solar = field(default_factory=Solar)
    dewpoint: float = 0.0
    heat_index: float = 0.0
    thsw_index: float = 0.0
    timestamp: Optional[datetime] = None
    station_info: StationInfo = field(default_factory=StationInfo)

    def is_valid(self) -> bool:
        """Check if weather data has been populated"""
        if self.timestamp is None:
            return False
        # Check if at least some data was parsed (any non-zero value)
        return (
            self.temperature.current != 0.0 or
            self.humidity.current != 0 or
            self.pressure.current != 0.0 or
            self.wind.speed != 0.0 or
            self.rain.today != 0.0
        )
