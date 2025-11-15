.PHONY: help build run stop logs test clean docker-build docker-push

help:
	@echo "Meteo Chamois Exporter - Available commands:"
	@echo ""
	@echo "  make build          - Build Docker image"
	@echo "  make run            - Run exporter with docker-compose"
	@echo "  make stop           - Stop container"
	@echo "  make logs           - Show logs"
	@echo "  make test           - Test the exporter endpoints"
	@echo "  make metrics        - Show metrics endpoint"
	@echo "  make clean          - Clean up container and volumes"
	@echo "  make docker-build   - Build production Docker image"
	@echo "  make docker-push    - Push Docker image to registry"
	@echo ""

build:
	docker-compose build

run:
	docker-compose up -d
	@echo ""
	@echo "Exporter started: http://localhost:9100"
	@echo ""
	@echo "Available endpoints:"
	@echo "  - Info:     http://localhost:9100/"
	@echo "  - Metrics:  http://localhost:9100/metrics"
	@echo "  - Health:   http://localhost:9100/health"
	@echo "  - Ready:    http://localhost:9100/ready"
	@echo ""

stop:
	docker-compose down

logs:
	docker-compose logs -f exporter

test:
	@echo "Testing exporter endpoints..."
	@curl -s http://localhost:9100/ | python -m json.tool
	@echo ""
	@echo "Health check:"
	@curl -s http://localhost:9100/health
	@echo ""
	@echo "Readiness check:"
	@curl -s http://localhost:9100/ready
	@echo ""

metrics:
	@curl -s http://localhost:9100/metrics

clean:
	docker-compose down -v
	rm -rf __pycache__ src/__pycache__ src/*/__pycache__

docker-build:
	docker build -t meteo-exporter:latest .

docker-push:
	@echo "Please tag and push to your registry:"
	@echo "  docker tag meteo-exporter:latest YOUR_REGISTRY/meteo-exporter:latest"
	@echo "  docker push YOUR_REGISTRY/meteo-exporter:latest"
