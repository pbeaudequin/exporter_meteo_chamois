# 🎨 Installation du Dashboard Grafana

## 📦 Fichiers créés

Voici ce qui a été ajouté à votre projet :

```
config/grafana/
├── provisioning/
│   ├── datasources/
│   │   └── prometheus.yml          # Configuration Prometheus (existant)
│   └── dashboards/
│       ├── dashboard.yml            # Configuration provisioning dashboards
│       └── meteo-roquefort.json     # Dashboard complet (24 panels)
├── README.md                        # Documentation complète
└── DASHBOARD_OVERVIEW.md            # Aperçu visuel du dashboard
```

## 🚀 Démarrage rapide

### Option 1 : Stack complète avec Docker Compose

Le dashboard est **automatiquement provisionné** avec docker-compose !

```bash
# Démarrer tous les services
docker compose up -d

# Vérifier que tout fonctionne
docker compose ps

# Accéder aux services
open http://localhost:3000  # Grafana (admin/admin)
open http://localhost:9090  # Prometheus
open http://localhost:9100  # Exporter metrics
```

Le dashboard sera **immédiatement disponible** dans Grafana !

### Option 2 : Import manuel

Si vous avez déjà une instance Grafana :

1. **Télécharger le dashboard** :
   ```bash
   # Le fichier est ici :
   config/grafana/provisioning/dashboards/meteo-roquefort.json
   ```

2. **Dans Grafana** :
   - Menu (☰) → **Dashboards** → **Import**
   - Cliquer sur **Upload JSON file**
   - Sélectionner `meteo-roquefort.json`
   - Choisir la datasource **Prometheus**
   - Cliquer sur **Import**

3. **C'est prêt !** 🎉

## 📊 Contenu du Dashboard

Le dashboard "**Météo Roquefort-les-Pins**" contient **24 panels** :

### Vue d'ensemble (4 gauges)
1. 🌡️ Température actuelle
2. 💧 Humidité relative
3. 🔽 Pression atmosphérique
4. 💨 Vitesse du vent

### Graphiques temporels (3 timeseries)
5. 📈 Température - Historique 24h (actuelle/min/max)
6. 📊 Pression atmosphérique - Évolution
7. 💨 Vent - Vitesse et rafales

### Vent détaillé (3 panels)
8. 🧭 Direction du vent (gauge avec points cardinaux)
9. 🌪️ Rafale maximale (stat)
10. 💨 Vent moyen (stat)

### Précipitations (3 panels)
11. 🌧️ Précipitations cumulées (pie chart)
12. 💧 Taux de précipitations (timeseries)
13. 📅 Pluviométrie mensuelle/annuelle (bar gauge)

### Ensoleillement (2 panels)
14. ☀️ Rayonnement solaire (timeseries)
15. 🌞 Durée d'ensoleillement (bar gauge)

### Indices de confort (3 stats)
16. 💦 Point de rosée
17. 🔥 Indice de chaleur
18. 🌡️ Indice THSW

### Monitoring système (4 stats)
19. ✅ État du scraping
20. ⏱️ Durée du scraping
21. 📦 Age du cache
22. 🕐 Dernière mise à jour

### Textes informatifs (2 panels)
23. 📝 En-tête avec titre et description
24. 📝 Séparateur "État du Système"

## ✨ Fonctionnalités

### Alertes visuelles automatiques
- 🔴 Température > 35°C → Rouge (canicule)
- 🔴 Vent > 80 km/h → Rouge (tempête)
- 🔴 Pression < 990 hPa → Rouge (dépression)
- 🔴 Scraping failed → Rouge (erreur système)

### Interactivité
- ✅ Auto-refresh : 1 minute
- ✅ Zoom temporel sur les graphiques
- ✅ Légendes interactives (clic pour masquer/afficher)
- ✅ Tooltips détaillés
- ✅ Responsive (desktop, tablet, mobile)

### Personnalisation
- ✅ Thème clair/sombre
- ✅ Seuils ajustables
- ✅ Couleurs personnalisables
- ✅ Layout modifiable
- ✅ Mode TV/Kiosk

## 🎯 Vérification

### 1. Vérifier que Grafana est démarré

```bash
docker logs grafana
```

Vous devriez voir :
```
✅ Provisioning dashboards
✅ Successfully provisioned 1 dashboards
```

### 2. Vérifier les données

```bash
# Prometheus doit scraper l'exporter
curl -s http://localhost:9090/api/v1/targets | grep weather

# L'exporter doit exposer des métriques
curl http://localhost:9100/metrics | grep weather_temperature
```

### 3. Accéder au dashboard

1. Ouvrir http://localhost:3000
2. Login : `admin` / `admin`
3. Menu (☰) → **Dashboards**
4. Cliquer sur "**Météo Roquefort-les-Pins**"

## 🎨 Aperçu du Design

Le dashboard utilise :
- **Emojis** pour une identification rapide
- **Dégradés de couleurs** selon les seuils
- **Graphiques variés** (gauges, timeseries, stats, pie, bar)
- **Layout optimisé** pour une lecture fluide
- **Descriptions** sur chaque panel (hover sur ℹ️)

### Exemple de rendu

```
┌─────────────┬─────────────┬─────────────┬─────────────┐
│ 🌡️ 23.5°C  │ 💧 65%     │ 🔽 1013 hPa│ 💨 15 km/h │
└─────────────┴─────────────┴─────────────┴─────────────┘

┌──────────────────────────┬──────────────────────────┐
│ 📈 Température 24h       │ 📊 Pression             │
│ [Graphique avec courbes] │ [Graphique tendance]    │
└──────────────────────────┴──────────────────────────┘
```

## 🛠️ Personnalisation

### Modifier les seuils de température

Éditer le dashboard → Panel Température → Edit :

```json
"thresholds": {
  "steps": [
    {"color": "blue", "value": null},
    {"color": "green", "value": 10},
    {"color": "yellow", "value": 20},
    {"color": "orange", "value": 30},
    {"color": "red", "value": 35}
  ]
}
```

### Ajouter une alerte

1. Éditer un panel → Tab **Alert**
2. **Create alert rule**
3. Condition : `weather_temperature_celsius{type="current"} > 35`
4. **Save** + Configurer les notifications

### Ajouter un panel

1. Dashboard → **Add** → **Visualization**
2. Datasource : Prometheus
3. Query : `weather_rain_mm{period="today"}`
4. Type de visualisation : au choix
5. **Apply**

## 📱 Mode TV / Kiosk

Afficher le dashboard en plein écran :

```bash
# Mode kiosk (masque menu et barre)
http://localhost:3000/d/meteo-roquefort?kiosk

# Avec auto-refresh 30s
http://localhost:3000/d/meteo-roquefort?kiosk&refresh=30s

# Range temporel fixe
http://localhost:3000/d/meteo-roquefort?kiosk&from=now-6h&to=now
```

Parfait pour :
- Écran TV dans un bureau
- Monitoring permanent
- Affichage public

## 🐛 Dépannage

### Dashboard vide ou "No data"

**Problème** : Panels affichent "No data"

**Solutions** :
```bash
# 1. Vérifier que l'exporter fonctionne
curl http://localhost:9100/metrics | grep weather_temperature

# 2. Vérifier que Prometheus scrape
open http://localhost:9090/targets
# → Le target "weather" doit être UP

# 3. Tester une requête PromQL
open http://localhost:9090/graph
# Query: weather_temperature_celsius{type="current"}
```

### Dashboard non provisionné

**Problème** : Dashboard n'apparaît pas automatiquement

**Solutions** :
```bash
# 1. Vérifier les logs Grafana
docker logs grafana | grep -i provision

# 2. Vérifier les volumes
docker inspect grafana | grep -A 5 Mounts

# 3. Forcer un redémarrage
docker compose restart grafana

# 4. Import manuel en fallback (voir Option 2)
```

### Erreur "Dashboard schema version"

**Problème** : Version de Grafana trop ancienne

**Solutions** :
```bash
# Mettre à jour Grafana
docker compose pull grafana
docker compose up -d grafana

# Ou éditer le JSON et réduire "schemaVersion"
```

## 📚 Documentation

- **Guide complet** : [config/grafana/README.md](config/grafana/README.md)
- **Aperçu visuel** : [config/grafana/DASHBOARD_OVERVIEW.md](config/grafana/DASHBOARD_OVERVIEW.md)
- **Métriques exposées** : [README.md](README.md#métriques-exposées)

## 🎉 Profitez !

Vous avez maintenant un dashboard météo **professionnel** et **élégant** !

Pour toute question ou suggestion, n'hésitez pas à ouvrir une issue.

**Bon monitoring ! ☀️🌧️🌡️💨**
