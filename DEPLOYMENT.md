# Guide de Déploiement en Production — Santé Numérique

Ce guide détaille la procédure complète pour déployer l'application **Santé Numérique** sur un serveur distant (VPS ou machine dédiée sous Ubuntu 22.04/24.04 LTS ou Debian 12).

---

## 1. Prérequis Serveur et Réseau

### Spécifications Matérielles Minimales
* **Processeur** : 2 cœurs vCPU ou plus.
* **Mémoire RAM** : 2 Go minimum (4 Go recommandé pour la compilation et le cache).
* **Espace Disque** : 25 Go SSD disponibles.
* **Système d'exploitation** : Ubuntu 22.04 LTS / 24.04 LTS ou Debian 12.

### Configuration DNS et Ports
1. Créez un enregistrement DNS de type **A** pointant votre nom de domaine (ex: `sante.votre-hopital.fr`) vers l'adresse IP publique de votre serveur.
2. Assurez-vous que les ports réseau suivants sont ouverts dans le pare-feu du fournisseur cloud :
   * **Port 22 TCP** : SSH (administration à distance).
   * **Port 80 TCP** : HTTP (redirection et validation Let's Encrypt).
   * **Port 443 TCP** : HTTPS (trafic sécurisé applicatif).
3. **Ports fermés à l'extérieur** : Les ports 5432 (PostgreSQL) et 8000 (Django/Gunicorn) **ne doivent jamais être ouverts** publiquement.

---

## 2. Préparation du Serveur Hôte

### 2.1. Mise à jour du système et pare-feu UFW

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y ufw curl git ca-certificates gnupg

# Configuration du pare-feu UFW
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 2.2. Installation de Docker et Docker Compose

```bash
# Installation du dépôt officiel Docker
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Autoriser l'utilisateur courant à exécuter Docker sans sudo
sudo usermod -aG docker $USER
newgrp docker
```

---

## 3. Déploiement de l'Application

### 3.1. Récupération du Code et Configuration de `.env`

```bash
# Cloner le dépôt
git clone <URL_DU_DEPOT> /opt/sante-numerique
cd /opt/sante-numerique

# Créer le fichier de variables d'environnement de production
cp .env.example .env
chmod 600 .env
nano .env
```

> [!IMPORTANT]
> **Checklist des variables indispensables à renseigner dans `.env` :**
> - `DOMAIN_NAME` : Votre nom de domaine public (ex: `sante.votre-hopital.fr`).
> - `CERTBOT_EMAIL` : Votre adresse email pour les alertes SSL.
> - `POSTGRES_PASSWORD` et `DATABASE_PASSWORD` : Un mot de passe robuste et complexe.
> - `DJANGO_SECRET_KEY` : Générer une clé aléatoire forte :
>   ```bash
>   python3 -c "import secrets; print(secrets.token_urlsafe(50))"
>   ```
> - `DJANGO_DEBUG` : Impérativement positionné à `False`.
> - `CSRF_TRUSTED_ORIGINS` et `CORS_ALLOWED_ORIGINS` : `https://sante.votre-hopital.fr`.

### 3.2. Exécution du Script de Déploiement Automatisé

Le script [`scripts/deploy.sh`](scripts/deploy.sh) exécute les 18 étapes requises en toute sécurité :

```bash
chmod +x scripts/*.sh
bash scripts/deploy.sh
```

---

## 4. Activation du Certificat SSL HTTPS avec Let's Encrypt

Une fois le déploiement HTTP initial validé et le DNS pointé vers le serveur :

```bash
bash scripts/init-letsencrypt.sh
```

Ce script :
1. Crée un certificat auto-signé temporaire pour initialiser Nginx.
2. Effectue la demande officielle auprès de Let's Encrypt via le challenge HTTP-01.
3. Remplace la configuration HTTP par la configuration HTTPS durcie ([`nginx/conf.d/ssl.conf.template`](nginx/conf.d/ssl.conf.template)).
4. Recharge Nginx sans coupure de service.

Le conteneur `certbot` inclus dans [`docker-compose.yml`](docker-compose.yml) renouvelle automatiquement les certificats toutes les 12 jours.

---

## 5. Procédure de Mise à Jour en Production

Lors de la livraison d'une nouvelle version de l'application :

```bash
cd /opt/sante-numerique

# 1. Sauvegarde préventive de la base de données
bash scripts/backup.sh

# 2. Récupérer les nouvelles sources
git pull origin main

# 3. Relancer la procédure de déploiement
bash scripts/deploy.sh
```

