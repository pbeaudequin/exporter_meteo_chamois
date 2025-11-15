"""
Weather station scraper with retry and caching
"""
import logging
import time
from typing import Optional
from datetime import datetime, timedelta
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .models import WeatherData
from .html_parser import WeatherHTMLParser

logger = logging.getLogger(__name__)


class WeatherScraper:
    """Scrape weather data from station website"""

    def __init__(
        self,
        base_url: str = "https://www.meteo-roquefort-les-pins.com",
        timeout: int = 10,
        cache_ttl: int = 60
    ):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.cache_ttl = cache_ttl
        self.parser = WeatherHTMLParser()

        # Setup session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Cache
        self._cached_data: Optional[WeatherData] = None
        self._cache_timestamp: Optional[datetime] = None
        self._last_scrape_duration: float = 0.0
        self._last_scrape_success: bool = False

    def _fetch_page(self, path: str) -> Optional[str]:
        """Fetch HTML page with error handling"""
        url = f"{self.base_url}/{path.lstrip('/')}"

        try:
            logger.info(f"Fetching {url}")
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.text

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            return None

    def _is_cache_valid(self) -> bool:
        """Check if cached data is still valid"""
        if self._cached_data is None or self._cache_timestamp is None:
            return False

        age = datetime.now() - self._cache_timestamp
        return age < timedelta(seconds=self.cache_ttl)

    def scrape(self, force: bool = False) -> Optional[WeatherData]:
        """
        Scrape weather data from station

        Args:
            force: Force refresh even if cache is valid

        Returns:
            WeatherData object or None if scraping failed
        """
        # Return cached data if valid
        if not force and self._is_cache_valid():
            logger.debug("Returning cached weather data")
            return self._cached_data

        start_time = time.time()
        weather_data: Optional[WeatherData] = None

        try:
            # Fetch both pages
            currant_html = self._fetch_page("meteo/currant.html")
            valeurs_html = self._fetch_page("meteo/vantage/valeurs.htm")

            if currant_html is None and valeurs_html is None:
                logger.error("Failed to fetch any weather pages")
                self._last_scrape_success = False
                # Return stale cache if available
                return self._cached_data

            # Parse pages
            if currant_html:
                weather_data = self.parser.parse_currant_html(currant_html)

            if valeurs_html:
                weather_data = self.parser.parse_valeurs_html(valeurs_html, weather_data)

            # Validate data
            if weather_data and weather_data.is_valid():
                self._cached_data = weather_data
                self._cache_timestamp = datetime.now()
                self._last_scrape_success = True
                logger.info("Successfully scraped weather data")
            else:
                logger.warning("Scraped data is invalid")
                self._last_scrape_success = False
                weather_data = self._cached_data  # Return stale cache

        except Exception as e:
            logger.error(f"Unexpected error during scraping: {e}", exc_info=True)
            self._last_scrape_success = False
            weather_data = self._cached_data  # Return stale cache

        finally:
            self._last_scrape_duration = time.time() - start_time
            logger.info(f"Scrape completed in {self._last_scrape_duration:.2f}s")

        return weather_data

    @property
    def last_scrape_duration(self) -> float:
        """Get duration of last scrape operation"""
        return self._last_scrape_duration

    @property
    def last_scrape_success(self) -> bool:
        """Check if last scrape was successful"""
        return self._last_scrape_success

    @property
    def cache_age_seconds(self) -> float:
        """Get age of cached data in seconds"""
        if self._cache_timestamp is None:
            return float('inf')
        return (datetime.now() - self._cache_timestamp).total_seconds()
