"""
Configuration management from environment variables
"""
import os
from dataclasses import dataclass


@dataclass
class Config:
    """Application configuration"""

    # Server settings
    listen_address: str = os.getenv('LISTEN_ADDRESS', '0.0.0.0')
    listen_port: int = int(os.getenv('LISTEN_PORT', '9100'))

    # Scraper settings
    station_url: str = os.getenv('STATION_URL', 'https://www.meteo-roquefort-les-pins.com')
    station_name: str = os.getenv('STATION_NAME', 'roquefort_les_pins')
    scrape_timeout: int = int(os.getenv('SCRAPE_TIMEOUT', '10'))
    cache_ttl: int = int(os.getenv('CACHE_TTL', '60'))

    # Logging
    log_level: str = os.getenv('LOG_LEVEL', 'INFO').upper()
    log_format: str = os.getenv('LOG_FORMAT', 'json')  # json or text

    @property
    def is_json_logging(self) -> bool:
        """Check if JSON logging is enabled"""
        return self.log_format.lower() == 'json'

    def __str__(self) -> str:
        """String representation (safe, no secrets)"""
        return (
            f"Config(listen={self.listen_address}:{self.listen_port}, "
            f"station={self.station_name}, cache_ttl={self.cache_ttl}s)"
        )


def load_config() -> Config:
    """Load configuration from environment"""
    return Config()
