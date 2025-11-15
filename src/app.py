"""
Flask application for Prometheus weather exporter
"""
import logging
from flask import Flask, Response
from prometheus_client import REGISTRY, generate_latest
from prometheus_client.core import CollectorRegistry

from .scraper import WeatherScraper
from .metrics import WeatherCollector
from .utils import load_config, setup_logging

logger = logging.getLogger(__name__)


def create_app() -> Flask:
    """Create and configure Flask application"""
    # Load configuration
    config = load_config()

    # Setup logging
    setup_logging(level=config.log_level, json_format=config.is_json_logging)

    logger.info(f"Starting Meteo Chamois Exporter with {config}")

    # Create Flask app
    app = Flask(__name__)
    app.config['config'] = config

    # Create scraper
    scraper = WeatherScraper(
        base_url=config.station_url,
        timeout=config.scrape_timeout,
        cache_ttl=config.cache_ttl
    )
    app.config['scraper'] = scraper

    # Create and register Prometheus collector
    collector = WeatherCollector(scraper, station_name=config.station_name)
    REGISTRY.register(collector)

    @app.route('/metrics')
    def metrics():
        """
        Prometheus metrics endpoint
        Returns metrics in Prometheus exposition format
        """
        try:
            output = generate_latest(REGISTRY)
            return Response(output, mimetype='text/plain; version=0.0.4; charset=utf-8')
        except Exception as e:
            logger.error(f"Error generating metrics: {e}", exc_info=True)
            return Response(
                "# Error generating metrics\n",
                status=500,
                mimetype='text/plain'
            )

    @app.route('/health')
    @app.route('/healthz')
    def health():
        """
        Health check endpoint (liveness probe)
        Always returns 200 if application is running
        """
        return {'status': 'healthy', 'service': 'meteo-chamois-exporter'}, 200

    @app.route('/ready')
    @app.route('/readiness')
    def ready():
        """
        Readiness check endpoint
        Returns 200 only if scraper is working
        """
        scraper = app.config['scraper']

        # Check if we can scrape data
        weather = scraper.scrape()

        if weather and weather.is_valid():
            return {
                'status': 'ready',
                'cache_age_seconds': scraper.cache_age_seconds,
                'last_scrape_success': scraper.last_scrape_success
            }, 200
        else:
            return {
                'status': 'not_ready',
                'reason': 'Unable to scrape weather data',
                'last_scrape_success': scraper.last_scrape_success
            }, 503

    @app.route('/')
    def index():
        """
        Root endpoint with service information
        """
        config = app.config['config']
        scraper = app.config['scraper']

        return {
            'service': 'Meteo Chamois Prometheus Exporter',
            'version': '1.0.0',
            'station': config.station_name,
            'endpoints': {
                'metrics': '/metrics',
                'health': '/health',
                'readiness': '/ready'
            },
            'status': {
                'last_scrape_success': scraper.last_scrape_success,
                'cache_age_seconds': round(scraper.cache_age_seconds, 2),
                'last_scrape_duration': round(scraper.last_scrape_duration, 3)
            }
        }, 200

    return app


def main():
    """Main entry point"""
    app = create_app()
    config = app.config['config']

    logger.info(f"Starting server on {config.listen_address}:{config.listen_port}")

    # Run Flask app
    app.run(
        host=config.listen_address,
        port=config.listen_port,
        debug=False
    )


if __name__ == '__main__':
    main()
