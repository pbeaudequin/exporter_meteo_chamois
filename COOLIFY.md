# Déploiement sur Coolify

Guide complet pour déployer le Meteo Chamois Exporter sur Coolify.

## Prérequis

- Instance Coolify fonctionnelle
- Repository Git (GitHub, GitLab, etc.)
- Prometheus déjà déployé (optionnel)

## Étape 1 : Préparer le Repository

1. Initialisez un repository Git :
```bash
git init
git add .
git commit -m "Initial commit: Meteo Chamois Exporter"
```

2. Poussez vers votre plateforme Git :
```bash
git remote add origin https://github.com/votre-user/exporter_meteo_chamois.git
git push -u origin main
```

## Étape 2 : Créer l'Application dans Coolify

### 2.1 Nouvelle Application

1. Dans Coolify, cliquez sur **"+ New Resource"**
2. Sélectionnez **"Application"**
3. Choisissez votre serveur de destination

### 2.2 Configuration Source

1. **Type de Build** : `Dockerfile`
2. **Git Repository** : URL de votre repository
3. **Branch** : `main` (ou votre branche de production)
4. **Dockerfile Path** : `./Dockerfile` (défaut)

### 2.3 Configuration Build

Coolify détectera automatiquement le Dockerfile. Aucune configuration spéciale nécessaire.

## Étape 3 : Configuration des Variables d'Environnement

Dans l'onglet **Environment Variables**, ajoutez :

| Variable | Valeur | Note |
|----------|--------|------|
| `LISTEN_ADDRESS` | `0.0.0.0` | Ne pas modifier |
| `LISTEN_PORT` | `9100` | Port interne |
| `STATION_URL` | `https://www.meteo-roquefort-les-pins.com` | URL du site météo |
| `STATION_NAME` | `roquefort_les_pins` | Label Prometheus |
| `SCRAPE_TIMEOUT` | `10` | Timeout en secondes |
| `CACHE_TTL` | `60` | Cache en secondes |
| `LOG_LEVEL` | `INFO` | DEBUG/INFO/WARNING/ERROR |
| `LOG_FORMAT` | `json` | json/text |

**Copier-coller rapide :**
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

## Étape 4 : Configuration Réseau

### 4.1 Port Mapping

1. Dans **"Network"**, ajoutez un port :
   - **Container Port** : `9100`
   - **Public Port** : `9100` (ou autre si déjà utilisé)
   - **Protocol** : `TCP`

### 4.2 Domain (Optionnel)

Si vous voulez un domaine personnalisé :
1. Ajoutez un domaine : `meteo-exporter.votre-domaine.com`
2. Coolify configurera automatiquement SSL avec Let's Encrypt

## Étape 5 : Health Checks

Coolify peut automatiquement configurer les health checks :

1. **Liveness Probe** :
   - Path : `/health`
   - Port : `9100`
   - Interval : `30s`
   - Timeout : `10s`

2. **Readiness Probe** :
   - Path : `/ready`
   - Port : `9100`
   - Interval : `30s`
   - Timeout : `10s`

Configuration JSON pour Coolify :
```json
{
  "healthcheck": {
    "test": ["CMD-SHELL", "curl -f http://localhost:9100/health || exit 1"],
    "interval": "30s",
    "timeout": "10s",
    "retries": 3,
    "start_period": "10s"
  }
}
```

## Étape 6 : Déploiement

1. Cliquez sur **"Deploy"** ou **"Redeploy"**
2. Suivez les logs de build en temps réel
3. Une fois déployé, testez les endpoints

## Étape 7 : Vérification

### 7.1 Test des Endpoints

```bash
# Health check
curl https://meteo-exporter.votre-domaine.com/health

# Readiness
curl https://meteo-exporter.votre-domaine.com/ready

# Métriques
curl https://meteo-exporter.votre-domaine.com/metrics

# Info
curl https://meteo-exporter.votre-domaine.com/
```

### 7.2 Vérifier les Logs

Dans Coolify, allez dans l'onglet **"Logs"** pour voir :
- Les logs de build
- Les logs d'exécution
- Les erreurs éventuelles

## Étape 8 : Intégration avec Prometheus

### 8.1 Si Prometheus est sur Coolify

1. Créez un **réseau interne** dans Coolify pour connecter les services
2. Ajoutez l'exporter au réseau
3. Dans la config Prometheus, utilisez le nom du service :

```yaml
scrape_configs:
  - job_name: 'weather'
    scrape_interval: 60s
    static_configs:
      - targets: ['meteo-exporter:9100']  # Nom du service Coolify
```

### 8.2 Si Prometheus est externe

1. Exposez l'exporter sur un port public ou utilisez le domaine
2. Dans Prometheus :

```yaml
scrape_configs:
  - job_name: 'weather'
    scrape_interval: 60s
    static_configs:
      - targets: ['meteo-exporter.votre-domaine.com:443']
    scheme: https
```

## Étape 9 : Auto-Deploy (CI/CD)

Pour que Coolify redéploie automatiquement lors de commits :

1. Dans Coolify, activez **"Auto Deploy"**
2. Configurez le **webhook** dans votre Git provider :
   - URL du webhook fournie par Coolify
   - Events : `push` sur branche `main`

Maintenant, chaque push sur `main` déclenche un redéploiement automatique !

## Configuration Avancée

### Resources Limits

Pour limiter les ressources (recommandé) :

```yaml
# Dans Coolify, section "Advanced"
resources:
  limits:
    cpus: '0.5'
    memory: 256M
  reservations:
    cpus: '0.1'
    memory: 64M
```

### Restart Policy

```yaml
restart: unless-stopped
```

### Scaling

L'exporter peut tourner en plusieurs instances avec un load balancer :
1. Coolify peut gérer plusieurs replicas
2. Chaque instance scrappe indépendamment
3. Prometheus peut scraper toutes les instances

## Troubleshooting

### Build échoue

```bash
# Vérifier le Dockerfile
cat Dockerfile

# Tester le build localement
docker build -t test .
```

### Container ne démarre pas

1. Vérifier les logs dans Coolify
2. Vérifier les variables d'environnement
3. Tester le port 9100 n'est pas déjà utilisé

### Pas de métriques

```bash
# Test depuis le container
docker exec -it <container_id> curl http://localhost:9100/metrics

# Vérifier les logs
docker logs <container_id>
```

### Site météo inaccessible

Si le site source est down ou inaccessible :
1. L'exporter retournera les dernières données en cache
2. `weather_scrape_success` sera à 0
3. Configurez une alerte Prometheus pour être notifié

## Monitoring de l'Exporter

Créez des alertes Prometheus :

```yaml
groups:
  - name: meteo_exporter
    rules:
      - alert: MeteoExporterDown
        expr: up{job="weather"} == 0
        for: 5m
        annotations:
          summary: "Meteo exporter is down"

      - alert: MeteoScrapeFailed
        expr: weather_scrape_success == 0
        for: 10m
        annotations:
          summary: "Weather scraping is failing"

      - alert: MeteoDataStale
        expr: time() - weather_last_update_timestamp > 300
        for: 5m
        annotations:
          summary: "Weather data is stale (>5min)"
```

## Mise à Jour

Pour mettre à jour l'exporter :

1. **Automatique** : Si auto-deploy activé, git push suffit
2. **Manuel** : Cliquez sur "Redeploy" dans Coolify

## Backup

Aucun backup nécessaire car :
- Pas de données persistantes
- Configuration dans le code (Git)
- Variables d'env dans Coolify (exportables)

## Coûts

Resources utilisées (estimation) :
- **CPU** : <1% (pics lors du scraping toutes les 60s)
- **RAM** : ~50-80MB
- **Réseau** : ~50KB toutes les 60s = ~70MB/jour
- **Stockage** : ~150MB (image Docker)

**Total** : Très léger, peut tourner sur le plus petit serveur Coolify.

## Support

Questions ? Problèmes ?
1. Vérifier les logs dans Coolify
2. Tester localement avec `docker-compose up`
3. Consulter le README.md
4. Ouvrir une issue GitHub

---

**C'est tout !** Votre exporter météo tourne maintenant sur Coolify 🎉
