#!/usr/bin/env python3
"""
Quick test script to verify the scraper works
Run: python test_scraper.py
"""
import sys
import logging
from src.scraper import WeatherScraper

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Test the weather scraper"""
    print("=" * 60)
    print("Testing Meteo Chamois Weather Scraper")
    print("=" * 60)
    print()

    # Create scraper
    scraper = WeatherScraper(
        base_url="https://www.meteo-roquefort-les-pins.com",
        timeout=10,
        cache_ttl=60
    )

    print("Scraping weather data...")
    weather = scraper.scrape(force=True)

    if weather is None:
        print("❌ Failed to scrape weather data")
        return 1

    if not weather.is_valid():
        print("❌ Scraped data is invalid")
        return 1

    print("✅ Successfully scraped weather data!\n")

    # Display results
    print("=" * 60)
    print("WEATHER DATA")
    print("=" * 60)
    print()

    print(f"📍 Station: {weather.station_info.name}")
    print(f"   Location: {weather.station_info.location}")
    print(f"   Coordinates: {weather.station_info.latitude}°N, {weather.station_info.longitude}°E")
    print(f"   Altitude: {weather.station_info.altitude}m")
    print(f"   Timestamp: {weather.timestamp}")
    print()

    print("🌡️  TEMPERATURE")
    print(f"   Current: {weather.temperature.current}°C")
    print(f"   Min: {weather.temperature.min}°C")
    print(f"   Max: {weather.temperature.max}°C")
    if weather.temperature.average:
        print(f"   Average: {weather.temperature.average}°C")
    print()

    print("💧 HUMIDITY")
    print(f"   Current: {weather.humidity.current}%")
    if weather.humidity.min:
        print(f"   Min: {weather.humidity.min}%")
    if weather.humidity.max:
        print(f"   Max: {weather.humidity.max}%")
    print()

    print("🔘 PRESSURE")
    print(f"   Current: {weather.pressure.current} hPa")
    if weather.pressure.trend:
        print(f"   Trend: {weather.pressure.trend:+.1f} hPa/6h")
    if weather.pressure.min:
        print(f"   Min: {weather.pressure.min} hPa")
    if weather.pressure.max:
        print(f"   Max: {weather.pressure.max} hPa")
    print()

    print("💨 WIND")
    print(f"   Speed: {weather.wind.speed} km/h")
    print(f"   Direction: {weather.wind.direction}° ({weather.wind.direction_text})")
    if weather.wind.average:
        print(f"   Average: {weather.wind.average} km/h")
    if weather.wind.gust_max:
        print(f"   Max Gust: {weather.wind.gust_max} km/h")
    print()

    print("🌧️  PRECIPITATION")
    print(f"   Last hour: {weather.rain.last_hour} mm")
    print(f"   Today: {weather.rain.today} mm")
    print(f"   Month: {weather.rain.month} mm")
    print(f"   Year: {weather.rain.year} mm")
    if weather.rain.rate:
        print(f"   Rate: {weather.rain.rate} mm/h")
    if weather.rain.rate_max:
        print(f"   Max Rate: {weather.rain.rate_max} mm/h")
    print()

    if weather.solar.radiation_current or weather.solar.sunshine_minutes:
        print("☀️  SOLAR")
        if weather.solar.radiation_current:
            print(f"   Radiation: {weather.solar.radiation_current} W/m²")
        if weather.solar.radiation_max:
            print(f"   Max Radiation: {weather.solar.radiation_max} W/m²")
        if weather.solar.sunshine_minutes:
            print(f"   Sunshine: {weather.solar.sunshine_minutes} minutes")
        print()

    if weather.dewpoint or weather.heat_index or weather.thsw_index:
        print("📊 INDICES")
        if weather.dewpoint:
            print(f"   Dewpoint: {weather.dewpoint}°C")
        if weather.heat_index:
            print(f"   Heat Index: {weather.heat_index}°C")
        if weather.thsw_index:
            print(f"   THSW Index: {weather.thsw_index}°C")
        print()

    print("=" * 60)
    print("📈 SCRAPER STATS")
    print("=" * 60)
    print(f"   Success: {scraper.last_scrape_success}")
    print(f"   Duration: {scraper.last_scrape_duration:.2f}s")
    print(f"   Cache Age: {scraper.cache_age_seconds:.2f}s")
    print()

    print("✅ Test completed successfully!")
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
        sys.exit(1)
