# Dashboard Grafana - Météo Roquefort-les-Pins

Ce dossier contient la configuration de provisioning automatique pour Grafana, incluant un dashboard complet et professionnel pour visualiser les données météo.

## 🎨 Fonctionnalités du Dashboard

Le dashboard **"Météo Roquefort-les-Pins"** offre une visualisation complète et élégante des données météorologiques :

### 📊 Sections principales

#### 1. **Vue d'ensemble (Gauges)**
- 🌡️ **Température** : Gauge avec codes couleurs selon la température
- 💧 **Humidité** : Affichage du taux d'humidité relative
- 🔽 **Pression** : Pression atmosphérique avec seuils
- 💨 **Vitesse du Vent** : Vitesse actuelle avec codes couleurs d'alerte

#### 2. **Historiques temporels**
- 📈 **Température 24h** : Évolution avec min/max
- 📊 **Pression atmosphérique** : Tendance et évolution
- 💨 **Vent** : Vitesse actuelle, moyenne et rafales

#### 3. **Détails du vent**
- 🧭 **Direction du vent** : Affichage en degrés avec points cardinaux (N, NE, E, SE, S, SO, O, NO)
- 🌪️ **Rafale maximale** : Stat avec alertes
- 💨 **Vent moyen** : Moyenne de la vitesse

#### 4. **Précipitations**
- 🌧️ **Précipitations cumulées** : Pie chart avec dernière heure, 24h, mois, année
- 💧 **Taux de précipitations** : Graphique temporel du taux actuel et maximum
- 📅 **Pluviométrie** : Bar gauge mensuelle et annuelle

#### 5. **Ensoleillement**
- ☀️ **Rayonnement solaire** : Graphique du rayonnement en W/m²
- 🌞 **Durée d'ensoleillement** : Minutes d'ensoleillement aujourd'hui et ce mois

#### 6. **Indices de confort**
- 💦 **Point de rosée** : Température de condensation
- 🔥 **Indice de chaleur** : Température ressentie avec humidité
- 🌡️ **Indice THSW** : Indice complet (température, humidité, soleil, vent)

#### 7. **Monitoring système**
- ✅ **État du scraping** : Indicateur de santé
- ⏱️ **Durée du scraping** : Performance de la collecte
- 📦 **Age du cache** : Fraîcheur des données
- 🕐 **Dernière mise à jour** : Timestamp relatif

## 🚀 Installation

### Méthode 1 : Docker Compose (Recommandé)

Le dashboard est automatiquement provisionné lors du démarrage de Grafana avec Docker Compose :

```bash
# Démarrer la stack complète
docker compose up -d

# Accéder à Grafana
open http://localhost:3000
```

**Identifiants par défaut :**
- Username: `admin`
- Password: `admin`

Le dashboard sera automatiquement disponible dans la liste des dashboards.

### Méthode 2 : Import manuel

Si vous utilisez une instance Grafana existante :

1. **Accéder à Grafana** : http://votre-grafana:3000
2. **Menu** → **Dashboards** → **Import**
3. **Upload JSON file** : Sélectionnez `meteo-roquefort.json`
4. **Sélectionner la datasource Prometheus**
5. **Import**

## 🎯 Configuration de la Datasource

Le fichier `provisioning/datasources/prometheus.yml` configure automatiquement Prometheus comme source de données.

Si vous devez modifier l'URL de Prometheus :

```yaml
datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090  # Modifier ici si besoin
```

## 📐 Personnalisation

### Modifier les seuils d'alerte

Dans le JSON du dashboard, vous pouvez ajuster les seuils pour chaque métrique. Par exemple, pour la température :

```json
"thresholds": {
  "mode": "absolute",
  "steps": [
    {"color": "blue", "value": null},
    {"color": "green", "value": 10},
    {"color": "yellow", "value": 20},
    {"color": "orange", "value": 30},
    {"color": "red", "value": 35}
  ]
}
```

### Ajouter des panels

1. Mode édition du dashboard : **⚙️ (Settings)** → **Add** → **Visualization**
2. Sélectionner une métrique Prometheus
3. Configurer l'affichage
4. **Save dashboard**

### Exemples de requêtes PromQL utiles

```promql
# Température ressentie vs réelle
weather_temperature_celsius{type="current"}
weather_heat_index_celsius

# Confort (humidité entre 40-70%)
weather_humidity_percent{type="current"} > 40 < 70

# Alerte vent fort (>60 km/h)
weather_wind_speed_kmh{type="gust_max"} > 60

# Pression en hausse/baisse
delta(weather_pressure_hpa{type="current"}[6h])

# Probabilité de pluie (humidité + point de rosée)
(weather_humidity_percent{type="current"} +
 (weather_dewpoint_celsius - weather_temperature_celsius{type="current"})) / 2
```

## 🎨 Thèmes et Apparence

Le dashboard utilise le thème par défaut de Grafana. Pour changer :

1. **Settings (⚙️)** → **Preferences**
2. **UI Theme** : Light / Dark / System
3. Les couleurs s'adaptent automatiquement

## 🔄 Rafraîchissement

- **Auto-refresh** : Configuré à 1 minute par défaut
- Modifiable en haut à droite du dashboard : 30s, 1m, 5m, etc.
- **Range temporel** : 24h par défaut, ajustable

## 📱 Responsive

Le dashboard est optimisé pour :
- 🖥️ **Desktop** : Vue complète avec tous les panels
- 📱 **Mobile** : Réorganisation automatique des panels
- 📺 **TV/Écran large** : Mode plein écran disponible

## 🔍 Variables et Filtres

Pour ajouter un filtre par station (si vous avez plusieurs stations) :

1. **Settings** → **Variables** → **Add variable**
2. **Name** : `station`
3. **Type** : Query
4. **Query** : `label_values(weather_temperature_celsius, station)`
5. Utiliser `$station` dans les requêtes

## 📊 Alerting

Pour configurer des alertes :

1. Sélectionner un panel → **Edit**
2. Onglet **Alert** → **Create alert rule**
3. Configurer les conditions (ex: température > 35°C)
4. Ajouter des notifications (email, Slack, etc.)

### Exemples d'alertes recommandées

```promql
# Température extrême
weather_temperature_celsius{type="current"} > 35 OR weather_temperature_celsius{type="current"} < 0

# Vent violent
weather_wind_speed_kmh{type="gust_max"} > 80

# Données obsolètes (>5 min)
time() - weather_last_update_timestamp > 300

# Scraping en échec
weather_scrape_success == 0
```

## 🐛 Dépannage

### Le dashboard ne s'affiche pas

1. Vérifier que Prometheus est accessible :
   ```bash
   curl http://localhost:9090/api/v1/query?query=up
   ```

2. Vérifier les logs Grafana :
   ```bash
   docker logs grafana
   ```

3. Vérifier que la datasource est configurée :
   - Grafana → **Configuration** → **Data sources** → **Prometheus**
   - **Test** doit être vert

### Pas de données dans les panels

1. Vérifier que l'exporter fonctionne :
   ```bash
   curl http://localhost:9100/metrics | grep weather_temperature
   ```

2. Vérifier que Prometheus scrappe l'exporter :
   - http://localhost:9090/targets
   - Le target `weather` doit être **UP**

3. Vérifier les requêtes PromQL :
   - http://localhost:9090/graph
   - Tester manuellement les requêtes

### Panels vides après import

- Éditer le panel → Vérifier que la datasource est bien `Prometheus`
- Changer `${DS_PROMETHEUS}` par `Prometheus` si nécessaire

## 📖 Ressources

- [Documentation Grafana](https://grafana.com/docs/)
- [PromQL Basics](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [Dashboard Best Practices](https://grafana.com/docs/grafana/latest/dashboards/build-dashboards/best-practices/)

## 🎉 Fonctionnalités avancées

### Snapshot et partage

- **Share** → **Snapshot** : Créer un snapshot statique
- **Share** → **Link** : Partager avec URL
- **Export** → **JSON** : Sauvegarder la config

### Playlists

Créer une rotation automatique de dashboards :
1. **Dashboards** → **Playlists** → **New playlist**
2. Ajouter plusieurs dashboards
3. Configurer l'intervalle de rotation
4. Parfait pour des écrans TV !

### Annotations

Ajouter des marqueurs d'événements :
- Orages, canicules, gelées
- Maintenance de la station
- Configuration via l'API Grafana

## 📞 Support

Pour toute question ou suggestion d'amélioration du dashboard, ouvrir une issue sur le repo GitHub du projet.
