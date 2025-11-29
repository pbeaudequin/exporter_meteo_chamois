# 🌤️ Aperçu du Dashboard Météo Roquefort-les-Pins

## Layout du Dashboard

```
┌─────────────────────────────────────────────────────────────────────────┐
│ 🌤️ Station Météo Roquefort-les-Pins - La Rose des Vents                │
│ Tableau de bord en temps réel - Rafraîchissement: 60s                   │
└─────────────────────────────────────────────────────────────────────────┘

┌────────────────┬────────────────┬────────────────┬────────────────────┐
│ 🌡️ Température │ 💧 Humidité    │ 🔽 Pression    │ 💨 Vitesse du Vent│
│                │                │                │                    │
│   [GAUGE]      │   [GAUGE]      │   [GAUGE]      │   [GAUGE]          │
│   23.5°C       │   65%          │   1013 hPa     │   15 km/h          │
│                │                │                │                    │
└────────────────┴────────────────┴────────────────┴────────────────────┘

┌─────────────────────────────────────┬──────────────────────────────────┐
│ 📈 Température - Historique 24h     │ 📊 Pression Atmosphérique        │
│                                     │                                  │
│  [TIMESERIES]                       │  [TIMESERIES]                    │
│  - Actuelle (orange)                │  - Évolution 24h                 │
│  - Maximum (rouge)                  │  - Tendance sur 6h               │
│  - Minimum (bleu)                   │                                  │
│                                     │                                  │
└─────────────────────────────────────┴──────────────────────────────────┘

┌─────────────────────────────────────┬──────────────┬─────────────────┐
│ 💨 Vent - Vitesse et Rafales        │ 🧭 Direction │ 🌪️ Rafale Max  │
│                                     │              │                 │
│  [TIMESERIES]                       │  [GAUGE]     │ [STAT]          │
│  - Actuelle (vert)                  │              │                 │
│  - Moyenne (bleu)                   │   270°       │  45 km/h        │
│  - Rafale max (rouge)               │   (O)        │                 │
│                                     │              │─────────────────│
│                                     │              │ 💨 Vent Moyen   │
│                                     │              │ [STAT]          │
│                                     │              │  18 km/h        │
└─────────────────────────────────────┴──────────────┴─────────────────┘

┌──────────────────────┬──────────────────────┬───────────────────────┐
│ 🌧️ Précipitations   │ 💧 Taux de Précipi-  │ 📅 Pluviométrie       │
│    Cumulées          │    tations           │    Mensuelle/Annuelle │
│                      │                      │                       │
│  [PIE CHART]         │  [TIMESERIES]        │  [BAR GAUGE]          │
│  - Dernière heure    │  - Taux actuel       │  - Mois: 45 mm        │
│  - Aujourd'hui       │  - Taux maximum      │  - Année: 580 mm      │
│  - 24h               │                      │                       │
│  - Mois              │                      │                       │
└──────────────────────┴──────────────────────┴───────────────────────┘

┌─────────────────────────────────────┬──────────────────────────────────┐
│ ☀️ Rayonnement Solaire              │ 🌞 Durée d'Ensoleillement        │
│                                     │                                  │
│  [TIMESERIES]                       │  [BAR GAUGE]                     │
│  - Actuel (jaune)                   │  - Aujourd'hui: 420 min          │
│  - Maximum (orange)                 │  - Mois: 8500 min                │
│                                     │                                  │
└─────────────────────────────────────┴──────────────────────────────────┘

┌────────────────────┬────────────────────┬──────────────────────────┐
│ 💦 Point de Rosée  │ 🔥 Indice de       │ 🌡️ Indice THSW          │
│                    │    Chaleur         │                          │
│  [STAT]            │  [STAT]            │  [STAT]                  │
│   18.2°C           │   26.5°C           │   27.8°C                 │
│                    │                    │                          │
└────────────────────┴────────────────────┴──────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│ 📊 État du Système                                                      │
│ Données de monitoring de l'exporter Prometheus                          │
└─────────────────────────────────────────────────────────────────────────┘

┌────────────────┬────────────────┬────────────────┬──────────────────┐
│ État du        │ ⏱️ Durée du    │ 📦 Age du      │ 🕐 Dernière      │
│ Scraping       │   Scraping     │   Cache        │   Mise à Jour    │
│                │                │                │                  │
│  [STAT]        │  [STAT]        │  [STAT]        │  [STAT]          │
│  ✅ OK         │  0.8s          │  15s           │  il y a 30s      │
│                │                │                │                  │
└────────────────┴────────────────┴────────────────┴──────────────────┘
```

## 🎨 Codes Couleurs

### Température
- 🔵 **Bleu** : < 0°C (Gel)
- 🔵 **Bleu clair** : 0-10°C (Froid)
- 🟢 **Vert** : 10-20°C (Frais)
- 🟡 **Jaune** : 20-30°C (Doux/Chaud)
- 🟠 **Orange** : 30-35°C (Très chaud)
- 🔴 **Rouge** : > 35°C (Canicule)

### Humidité
- 🔴 **Rouge** : < 20% (Très sec)
- 🟠 **Orange** : 20-40% (Sec)
- 🟢 **Vert** : 40-70% (Confortable)
- 🔵 **Bleu clair** : 70-85% (Humide)
- 🔵 **Bleu** : > 85% (Très humide)

### Pression
- 🔴 **Rouge** : < 990 hPa (Dépression)
- 🟠 **Orange** : 990-1000 hPa (Bas)
- 🟡 **Jaune** : 1000-1010 hPa (Normal bas)
- 🟢 **Vert** : 1010-1025 hPa (Normal)
- 🔵 **Bleu clair** : > 1025 hPa (Anticyclone)

### Vent
- 🟢 **Vert** : < 20 km/h (Faible)
- 🟡 **Jaune** : 20-40 km/h (Modéré)
- 🟠 **Orange** : 40-60 km/h (Fort)
- 🔴 **Rouge** : 60-80 km/h (Très fort)
- 🔴 **Rouge foncé** : > 80 km/h (Violent)

## 📊 Types de Visualisations

### Gauges (Jauges)
- **Usage** : Métriques instantanées avec seuils
- **Panels** : Température, Humidité, Pression, Vent, Direction
- **Avantages** : Lecture rapide, alertes visuelles immédiates

### Time Series (Séries temporelles)
- **Usage** : Évolution dans le temps
- **Panels** : Température 24h, Pression, Vent, Pluie, Solaire
- **Avantages** : Tendances, comparaisons, historique

### Stats (Statistiques)
- **Usage** : Valeurs uniques avec contexte
- **Panels** : Rafale max, Vent moyen, Indices (rosée, chaleur, THSW)
- **Avantages** : Mise en valeur, graphiques sparkline intégrés

### Pie Chart (Camembert)
- **Usage** : Répartition proportionnelle
- **Panels** : Précipitations cumulées
- **Avantages** : Visualisation des parts relatives

### Bar Gauge (Jauge à barres)
- **Usage** : Comparaison de valeurs
- **Panels** : Pluviométrie, Ensoleillement
- **Avantages** : Comparaison mois/année, seuils

## 🔄 Interactions

### Navigation temporelle
- **Zoom** : Cliquer-glisser sur un graphique
- **Range** : Sélecteur en haut à droite (6h, 12h, 24h, 7d, 30d)
- **Refresh** : Auto-refresh configuré à 1 minute

### Légendes
- **Clic** : Masquer/afficher une série
- **Maj+Clic** : Isoler une série
- **Stats** : Affichage de last, min, max, mean selon le panel

### Tooltips
- **Hover** : Affiche les valeurs exactes
- **Multi-series** : Valeurs de toutes les séries à cet instant
- **Timestamp** : Date/heure précise

## 🎯 Cas d'Usage

### Planification d'activités extérieures
1. Vérifier température et indice de chaleur
2. Consulter les prévisions de vent
3. Vérifier les précipitations des dernières heures

### Jardinage
1. Point de rosée → Risque de gel
2. Pluviométrie mensuelle → Besoin d'arrosage
3. Ensoleillement → Exposition optimale

### Suivi météo détaillé
1. Évolution pression → Changement météo
2. Direction du vent → Provenance masses d'air
3. Tendances sur 24h → Patterns météo

### Monitoring technique
1. État scraping → Service opérationnel
2. Age cache → Fraîcheur données
3. Durée scraping → Performance système

## 🚀 Prochaines étapes

### Import manuel dans Grafana
```bash
# 1. Accéder à Grafana
open http://localhost:3000

# 2. Menu → Dashboards → Import
# 3. Upload le fichier JSON ou copier-coller le contenu
# 4. Sélectionner la datasource Prometheus
# 5. Import → Dashboard prêt !
```

### Personnalisation
- Modifier les seuils d'alerte selon vos besoins
- Ajouter des panels personnalisés
- Créer des alertes avec notifications
- Ajuster les couleurs et le layout

### Partage
- Créer des snapshots publics
- Générer des liens de partage
- Exporter en PDF pour rapports
- Intégrer dans des iframes

## 📱 Mode TV/Kiosk

Pour afficher le dashboard en plein écran (mode TV) :

```
http://localhost:3000/d/meteo-roquefort?kiosk
```

Options disponibles :
- `?kiosk` : Mode plein écran
- `?kiosk&refresh=30s` : Avec rafraîchissement 30s
- `?from=now-6h&to=now` : Range temporel fixe

## 💡 Astuces

1. **Performance** : Si le dashboard est lent, augmenter l'intervalle de refresh
2. **Mobile** : Le dashboard est responsive, parfait pour smartphone
3. **Alertes** : Configurer des notifications Slack/Email pour les seuils critiques
4. **Variables** : Ajouter `$station` pour gérer plusieurs stations
5. **Annotations** : Marquer des événements importants (orages, canicules)

## 📞 Support

Documentation complète : [config/grafana/README.md](README.md)

Profitez de votre dashboard météo professionnel ! ☀️🌧️❄️
