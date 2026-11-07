# Guide d'Utilisation Docker — Santé Numérique

Ce document décrit l'architecture multi-conteneurs de l'application **Santé Numérique** et fournit la liste des commandes opérationnelles au quotidien.

---

## 1. Architecture des Services

Le fichier [`docker-compose.yml`](docker-compose.yml) orchestre cinq conteneurs interconnectés au sein d'un réseau privé isolé (`sante_internal_network`) :

```text
                             INTERNET
                                 |
                          Ports 80 / 443
                                 |
                       [ Reverse Proxy Nginx ]
                                 |
        +------------------------+------------------------+
        |                                                 |
  [ Frontend ]                                      [ Backend ]
  Angular 22 / SPA                                  Django / DRF / Gunicorn
  Port interne : 80                                 Port interne : 8000
                                                          |
                                                    [ Base de Données ]
                                                    PostgreSQL 16 Alpine
                                                    Port interne : 5432
```

| Service | Image / Build | Rôle | Exposition externe |
| :--- | :--- | :--- | :--- |
| **`nginx`** | `nginx:alpine` | Point d'entrée HTTPS/HTTP unique, terminaison SSL, compression Gzip, rate-limiting, proxy vers Backend et Frontend. | **80 / 443** |
| **`frontend`** | `frontend/Dockerfile` | Application Angular SPA compilée, servie par un Nginx interne avec fallback sur `index.html`. | Aucun (Réseau interne) |
| **`backend`** | `backend/Dockerfile` | API REST Django / DRF exécutée avec le serveur WSGI Gunicorn (3 workers, utilisateur non-root `appuser`). | Aucun (Réseau interne) |
| **`db`** | `postgres:18-alpine` | Base de données relationnelle persistante avec vérification de santé `pg_isready`. | Aucun (Réseau interne) |
| **`certbot`** | `certbot/certbot` | Renouvellement automatique des certificats SSL Let's Encrypt via challenge HTTP-01. | Aucun (Réseau interne) |

---

## 2. Commandes Opérationnelles Usuelles

### Démarrage et Arrêt

```bash
# Démarrer tous les services en arrière-plan (mode détaché)
docker compose up -d

# Démarrer en reconstruisant les images (après modification de code ou de Dockerfile)
docker compose up -d --build

# Consulter l'état des conteneurs et leur santé (Healthcheck)
docker compose ps

# Arrêter l'ensemble des conteneurs sans détruire les volumes de données
docker compose stop

# Arrêter et supprimer les conteneurs (les données restent préservées dans les volumes)
docker compose down
```

### Consultation des Journaux (Logs)

```bash
# Suivre les logs de tous les services en continu
docker compose logs -f

# Suivre les logs d'un service spécifique
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f nginx
docker compose logs -f db

# Afficher les 100 dernières lignes de logs
docker compose logs --tail=100 backend
```

### Commandes Django dans le Conteneur Backend

```bash
# Ouvrir un shell interactif Django
docker compose exec backend python manage.py shell

# Exécuter les migrations de schéma
docker compose exec backend python manage.py migrate

# Vérifier l'état des migrations
docker compose exec backend python manage.py showmigrations

# Collecter les fichiers statiques
docker compose exec backend python manage.py collectstatic --noinput

# Exécuter la suite de tests
docker compose exec backend python manage.py test

# Vérifier le système et le déploiement
docker compose exec backend python manage.py check --deploy
```

### Commandes PostgreSQL dans le Conteneur Base de Données

```bash
# Ouvrir le client interactif psql
docker compose exec db psql -U sante_user -d sante_numerique

# Vérifier l'état de santé PostgreSQL
docker compose exec db pg_isready -U sante_user -d sante_numerique
```

---

## 3. Volumes Persistants et Données

Les données critiques sont isolées dans des volumes Docker nommés gérés par l'hôte :

| Volume Nommé | Emplacement Conteneur | Description |
| :--- | :--- | :--- |
| `sante_postgres_data` | `/var/lib/postgresql/data` | Données relationnelles de la base PostgreSQL |
| `sante_django_static` | `/app/staticfiles` | Fichiers statiques collectés par Django et servis par Nginx |
| `sante_django_media` | `/app/media` | Documents et pièces jointes médicales |
| `sante_certbot_www` | `/var/www/certbot` | Dossier temporaire des challenges ACME HTTP-01 |
| `sante_certbot_conf` | `/etc/letsencrypt` | Clés privées et certificats SSL officiels |

> [!CAUTION]
> Ne jamais exécuter `docker compose down -v` en production : l'option `-v` détruit irrémédiablement les volumes de données et la base PostgreSQL.

