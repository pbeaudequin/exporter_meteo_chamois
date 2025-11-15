# Meteo Chamois Exporter

Prometheus exporter pour la station météo de Roquefort-les-Pins (La Rose des Vents).

Expose les données météorologiques au format Prometheus pour monitoring et visualisation avec Grafana.

## Caractéristiques

- Scraping HTML intelligent avec retry automatique
- Cache TTL (60s par défaut) pour éviter la surcharge du site source
- Métriques Prometheus complètes (température, humidité, pression, vent, pluie, solaire)
- Health checks (liveness & readiness probes)
- Logging structuré (JSON ou texte)
- Image Docker optimisée (~150MB)
- Configuration via variables d'environnement
- Production-ready avec Gunicorn

## Métriques Exposées

### Température
- `weather_temperature_celsius{station, type}` - Température (current/min/max/average)

### Humidité
- `weather_humidity_percent{station, type}` - Humidité relative (current/min/max)

### Pression
- `weather_pressure_hpa{station, type}` - Pression atmosphérique (current/min/max)
- `weather_pressure_trend_hpa{station}` - Tendance pression sur 6h

### Vent
- `weather_wind_speed_kmh{station, type}` - Vitesse du vent (current/average/gust_max)
- `weather_wind_direction_degrees{station}` - Direction du vent en degrés

### Précipitations
- `weather_rain_mm{station, period}` - Précipitations (last_hour/today/24h/month/year)
- `weather_rain_rate_mmh{station, type}` - Taux de pluie (current/max)

### Solaire
- `weather_solar_radiation_wm2{station, type}` - Rayonnement solaire (current/max)
- `weather_sunshine_minutes{station, period}` - Durée d'ensoleillement

### Autres
- `weather_dewpoint_celsius{station}` - Point de rosée
- `weather_heat_index_celsius{station}` - Indice de chaleur
- `weather_thsw_index_celsius{station}` - Indice THSW
- `weather_station_info{...}` - Informations sur la station
- `weather_last_update_timestamp{station}` - Timestamp dernière mise à jour
- `weather_scrape_success{station}` - Succès du scraping (1=ok, 0=erreur)
- `weather_scrape_duration_seconds{station}` - Durée du scraping
- `weather_cache_age_seconds{station}` - Age du cache

## Déploiement avec Coolify

### Méthode 1 : Déploiement direct depuis Git (Recommandé)

1. **Dans Coolify, créer une nouvelle application :**
   - Type : `Dockerfile`
   - Source : Repository Git (URL de votre repo)
   - Branch : `main`

2. **Configuration des variables d'environnement :**
   ```
   LISTEN_ADDRESS=0.0.0.0
   LISTEN_PORT=9100
   STATION_URL=https://www.meteo-roquefort-les-pins.com
   STATION_NAME=roquefort_les_pins
   SCRAPE_TIMEOUT=10
   CACHE_TTL=60
   LOG_LEVEL=INFO
   LOG_FORMAT=json
   ```

3. **Configuration du port :**
   - Port interne : `9100`
   - Port exposé : Au choix (ex: 9100)

4. **Health Checks :**
   - Liveness probe : `http://localhost:9100/health`
   - Readiness probe : `http://localhost:9100/ready`

5. **Déployer !**

### Méthode 2 : Docker Registry

Si vous préférez pousser l'image vers un registry :

```bash
# Build l'image
docker build -t votreregistry.com/meteo-exporter:latest .

# Push vers votre registry
docker push votreregistry.com/meteo-exporter:latest
```

Puis dans Coolify :
- Type : `Docker Image`
- Image : `votreregistry.com/meteo-exporter:latest`

## Configuration Prometheus

Ajoutez ce job dans votre `prometheus.yml` :

```yaml
scrape_configs:
  - job_name: 'weather'
    scrape_interval: 60s
    static_configs:
      - targets: ['meteo-exporter:9100']
        labels:
          station: 'roquefort_les_pins'
```

## Test Local avec Docker Compose

Pour tester en local avec Prometheus + Grafana :

```bash
# Lancer la stack complète
make run

# Vérifier les logs
make logs

# Tester les endpoints
make test

# Voir les métriques
make metrics

# Arrêter
make stop

# Nettoyer
make clean
```

Services disponibles :
- Exporter : http://localhost:9100
- Prometheus : http://localhost:9090
- Grafana : http://localhost:3000 (admin/admin)

## Endpoints

| Endpoint | Description |
|----------|-------------|
| `/` | Informations sur le service |
| `/metrics` | Métriques Prometheus |
| `/health` | Health check (liveness) |
| `/ready` | Readiness check |

## Variables d'Environnement

| Variable | Défaut | Description |
|----------|--------|-------------|
| `LISTEN_ADDRESS` | `0.0.0.0` | Adresse d'écoute |
| `LISTEN_PORT` | `9100` | Port d'écoute |
| `STATION_URL` | `https://www.meteo-roquefort-les-pins.com` | URL du site météo |
| `STATION_NAME` | `roquefort_les_pins` | Nom de la station (label Prometheus) |
| `SCRAPE_TIMEOUT` | `10` | Timeout HTTP en secondes |
| `CACHE_TTL` | `60` | Durée du cache en secondes |
| `LOG_LEVEL` | `INFO` | Niveau de log (DEBUG/INFO/WARNING/ERROR) |
| `LOG_FORMAT` | `json` | Format des logs (json/text) |

## Exemples de Requêtes PromQL

```promql
# Température actuelle
weather_temperature_celsius{type="current"}

# Température moyenne sur 1h
avg_over_time(weather_temperature_celsius{type="current"}[1h])

# Pluie totale aujourd'hui
weather_rain_mm{period="today"}

# Rafale de vent maximale
weather_wind_speed_kmh{type="gust_max"}

# Évolution de la pression (tendance météo)
delta(weather_pressure_hpa{type="current"}[6h])

# Alertes : Vent fort (>80 km/h)
weather_wind_speed_kmh{type="gust_max"} > 80

# Alertes : Données obsolètes (>5 min)
time() - weather_last_update_timestamp > 300
```

## Dashboard Grafana

Panels recommandés :

1. **Température** - Time series graph
   - Query : `weather_temperature_celsius`
   - Legend : `{{type}}`

2. **Vent** - Gauge + Stat
   - Current : `weather_wind_speed_kmh{type="current"}`
   - Gust : `weather_wind_speed_kmh{type="gust_max"}`

3. **Précipitations** - Bar gauge
   - Query : `weather_rain_mm`

4. **Pression** - Time series avec tendance
   - Query : `weather_pressure_hpa{type="current"}`

5. **Humidité** - Gauge
   - Query : `weather_humidity_percent{type="current"}`

## Architecture

```
exporter_meteo_chamois/
├── src/
│   ├── __init__.py
│   ├── app.py                  # Application Flask
│   ├── scraper/
│   │   ├── __init__.py
│   │   ├── models.py           # Data models
│   │   ├── html_parser.py      # HTML parsing
│   │   └── scraper.py          # HTTP scraper
│   ├── metrics/
│   │   ├── __init__.py
│   │   └── collector.py        # Prometheus collector
│   └── utils/
│       ├── __init__.py
│       ├── config.py            # Configuration
│       └── logging.py           # Logging setup
├── config/
│   ├── prometheus.yml          # Config Prometheus
│   └── grafana/                # Config Grafana
├── Dockerfile                   # Production image
├── docker-compose.yml          # Stack complète (dev)
├── requirements.txt
├── Makefile
└── README.md
```

## Développement

### Prérequis
- Python 3.11+
- pip

### Installation locale

```bash
# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'exporter
python -m src.app

# Ou avec gunicorn
gunicorn --bind 0.0.0.0:9100 "src.app:create_app()"
```

## Monitoring de l'Exporter

L'exporter s'auto-monitore avec ces métriques :

- `weather_scrape_success` : Succès/échec du scraping
- `weather_scrape_duration_seconds` : Performance
- `weather_cache_age_seconds` : Fraîcheur des données

Alertes recommandées :

```yaml
# Prometheus alerts
groups:
  - name: weather_exporter
    rules:
      - alert: WeatherScrapeFailed
        expr: weather_scrape_success == 0
        for: 5m
        annotations:
          summary: "Weather scraping failed"

      - alert: WeatherDataStale
        expr: time() - weather_last_update_timestamp > 300
        for: 5m
        annotations:
          summary: "Weather data is stale (>5min)"
```

## Performance

- **Mémoire** : ~50MB
- **CPU** : <1% (scraping toutes les 60s)
- **Réseau** : ~50KB par scrape
- **Temps de réponse** : <500ms pour `/metrics`

## Sécurité

- Image Docker multi-stage (build + runtime séparés)
- Exécution en tant qu'utilisateur non-root
- Pas de secrets/credentials nécessaires
- Rate limiting sur le scraping (cache TTL)
- Validation des données parsées

## Troubleshooting

### L'exporter ne démarre pas
```bash
# Vérifier les logs
docker logs meteo-exporter

# Tester la connectivité
curl https://www.meteo-roquefort-les-pins.com/meteo/currant.html
```

### Pas de données
```bash
# Vérifier le readiness probe
curl http://localhost:9100/ready

# Voir les métriques de debug
curl http://localhost:9100/metrics | grep weather_scrape
```

### Données obsolètes
- Vérifier `weather_cache_age_seconds`
- Ajuster `CACHE_TTL` si nécessaire
- Vérifier que le site source est accessible

## Licence

MIT

## Auteur

Philippe Beaudequin

## Support

Pour toute question ou bug, ouvrir une issue sur GitHub.
