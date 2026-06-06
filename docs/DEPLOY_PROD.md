# Déploiement production LUTHOR (VPS européen)

Guide pas à pas pour déployer LUTHOR avec tous les outils MCP sur un VPS **OVH**, **Scaleway** ou **Hetzner** — sans dépendance à un cloud américain.

> L'environnement de développement reste `docker-compose.yml` (minimal).  
> La production utilise **`docker-compose.prod.yml`** (optionnel).

## 1. Choisir un VPS européen

| Fournisseur | Région recommandée | Config minimale |
|-------------|-------------------|-----------------|
| [OVH](https://www.ovhcloud.com/fr/vps/) | Gravelines / Strasbourg | 4 vCPU, 8 Go RAM, 80 Go SSD |
| [Scaleway](https://www.scaleway.com/fr/vps/) | PAR (Paris) | GP1-S ou supérieur |
| [Hetzner](https://www.hetzner.com/cloud) | Falkenstein / Nuremberg (UE) | CX32 ou supérieur |

**Estimation** : 15–30 €/mois pour une PME (API + monitoring + n8n + Plausible + Cal.com + Fooocus).

Créez une instance **Ubuntu 24.04 LTS** et notez l'IP publique.

## 2. DNS

Chez votre registrar (OVH, Gandi, Cloudflare EU…), créez des enregistrements **A** vers l'IP du VPS :

| Sous-domaine | Cible |
|--------------|-------|
| `luthor.example.com` | IP VPS |
| `grafana.luthor.example.com` | IP VPS |
| `prometheus.luthor.example.com` | IP VPS |
| `n8n.luthor.example.com` | IP VPS |
| `plausible.luthor.example.com` | IP VPS |
| `cal.luthor.example.com` | IP VPS |
| `fooocus.luthor.example.com` | IP VPS |

Traefik génère automatiquement les certificats Let's Encrypt.

## 3. Préparer le serveur

```bash
ssh root@VOTRE_IP

apt update && apt upgrade -y
apt install -y ca-certificates curl git ufw

# Docker (officiel)
curl -fsSL https://get.docker.com | sh
usermod -aG docker $USER

# Firewall
ufw allow OpenSSH
ufw allow 80,443/tcp
ufw enable
```

Reconnectez-vous pour appliquer le groupe `docker`.

## 4. Cloner LUTHOR et configurer

```bash
git clone https://github.com/ChawnRob/Luthor.git
cd Luthor

cp .env.prod.example .env.prod
nano .env.prod   # mots de passe, LUTHOR_DOMAIN, MISTRAL_API_KEY, ACME_EMAIL
```

Variables critiques :

| Variable | Description |
|----------|-------------|
| `LUTHOR_DOMAIN` | Domaine principal (ex. `luthor.monsite.fr`) |
| `ACME_EMAIL` | Email Let's Encrypt |
| `POSTGRES_PASSWORD` | Mot de passe PostgreSQL |
| `MISTRAL_API_KEY` | Clé Mistral (orchestration EU) |
| `GRAFANA_ADMIN_PASSWORD` | Accès Grafana |

## 5. Déployer

```bash
chmod +x scripts/deploy_prod.sh scripts/backup_prod.sh
./scripts/deploy_prod.sh
```

Le script :

1. Vérifie Docker Compose
2. Crée `.env.prod` depuis l'exemple si absent
3. `docker compose pull` + build API (`Dockerfile.prod`)
4. Démarre tous les services
5. Attend Postgres / Chroma / API
6. Affiche les URLs

Options :

```bash
./scripts/deploy_prod.sh --pull-only   # images seulement
./scripts/deploy_prod.sh --no-build    # sans rebuild API
```

## 6. Vérifier le bon fonctionnement

```bash
# État des conteneurs
docker compose -f docker-compose.prod.yml --env-file .env.prod ps

# Santé API
curl -fsS https://luthor.example.com/health | jq

# Métriques Prometheus
curl -fsS https://luthor.example.com/metrics | head

# Démo bout en bout
curl -X POST https://luthor.example.com/demo/full \
  -H "Content-Type: application/json" \
  -d '{"message": "Test déploiement production"}'
```

Interface web : `https://luthor.example.com/demo-ui`

## 7. Services inclus

| Service | Rôle |
|---------|------|
| `traefik` | HTTPS + reverse proxy |
| `api` | LUTHOR FastAPI |
| `postgres` | Base de données |
| `chromadb` | Embeddings |
| `prometheus` / `grafana` | Observabilité |
| `n8n` | Automatisations |
| `plausible` + `clickhouse` | Analytics self-hosted |
| `calcom` | Prise de rendez-vous |
| `fooocus` | Génération d'images |
| `watchtower` | Mises à jour quotidiennes des images |

PenPot et AppFlowy peuvent rester **externes** (SaaS ou autre VPS) via `.env.prod`.

## 8. Sécurité

### Firewall (UFW)

Seuls **22** (SSH), **80** et **443** doivent être publics. Les bases de données restent sur le réseau Docker interne.

### Mises à jour automatiques

`watchtower` vérifie les nouvelles images toutes les 24 h. Pour désactiver :

```bash
docker compose -f docker-compose.prod.yml --env-file .env.prod stop watchtower
```

### Backups

```bash
./scripts/backup_prod.sh
# → backups/YYYYMMDD-HHMMSS/*.tar.gz
```

Planifiez un cron hebdomadaire et copiez les archives hors du VPS (Scaleway Object Storage, OVH Object Storage…).

### Bonnes pratiques

- Changez tous les mots de passe par défaut dans `.env.prod`
- Limitez l'accès SSH par clé (désactivez le mot de passe root)
- Restreignez Grafana / Prometheus par IP ou authentification Traefik si exposés

## 9. Compatibilité développement

| Commande | Impact |
|----------|--------|
| `make demo` | Inchangé (local, sans Docker prod) |
| `make test` | Inchangé |
| `make docker-up` | Utilise `docker-compose.yml` minimal |

## 10. Dépannage

| Symptôme | Action |
|----------|--------|
| Certificat TLS en attente | Vérifier DNS (propagation 5–30 min), ports 80/443 ouverts |
| API `degraded` | `docker compose … logs api postgres chromadb` |
| Fooocus lent | Prévoir GPU ou désactiver `LUTHOR_MCP_FOOOCUS_ENABLED` |
| Cal.com ne démarre pas | Vérifier `CALCOM_NEXTAUTH_SECRET` et base `calcom` |

## Tests locaux (sans lancer Docker)

```bash
python3 -m unittest tests.test_prod_compose -v
```

Valide la syntaxe de `docker-compose.prod.yml` et la présence de tous les services.
