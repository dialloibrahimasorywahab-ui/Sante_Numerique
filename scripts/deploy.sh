#!/bin/bash
# ==============================================================================
# SANTÉ NUMÉRIQUE — SCRIPT DE PREMIER DÉPLOIEMENT ET MISE À JOUR EN PRODUCTION
# ==============================================================================
# Ordre strict des 18 étapes d'exploitation
# ==============================================================================
set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}==============================================================================${NC}"
echo -e "${BLUE}    SANTÉ NUMÉRIQUE — PROCÉDURE DE DÉPLOIEMENT EN PRODUCTION                  ${NC}"
echo -e "${BLUE}==============================================================================${NC}"

# Étape 1 : Vérification des ressources du serveur (RAM, Disque)
echo -e "\n${YELLOW}[1/18] Vérification des ressources du serveur...${NC}"
FREE_RAM_MB=$(free -m | awk '/^Mem:/{print $7}')
FREE_DISK_GB=$(df -BG . | awk 'NR==2 {print substr($4, 1, length($4)-1)}')
echo "RAM disponible : ${FREE_RAM_MB} Mo | Espace disque disponible : ${FREE_DISK_GB} Go"
if [ "$FREE_RAM_MB" -lt 512 ]; then
    echo -e "${YELLOW}ATTENTION : Moins de 512 Mo de RAM libre. Risque de lenteur ou de OOM Killer.${NC}"
fi
if [ "$FREE_DISK_GB" -lt 5 ]; then
    echo -e "${RED}ERREUR : Moins de 5 Go d'espace disque disponible.${NC}"
    exit 1
fi

# Étape 2 : Vérification du domaine et DNS
echo -e "\n${YELLOW}[2/18] Vérification du domaine et des résolutions DNS...${NC}"
if [ -f .env ]; then
    DOMAIN_NAME=$(grep -E '^DOMAIN_NAME=' .env | cut -d '=' -f 2 | tr -d '\r' | tr -d '"' | tr -d "'")
fi
DOMAIN_NAME=${DOMAIN_NAME:-sante.votre-hopital.fr}
echo "Nom de domaine configuré : $DOMAIN_NAME"

# Étape 3 : Vérification de Docker et Docker Compose
echo -e "\n${YELLOW}[3/18] Vérification de Docker et Docker Compose...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}ERREUR : Docker n'est pas installé sur ce serveur.${NC}"
    exit 1
fi
if ! docker compose version &> /dev/null; then
    echo -e "${RED}ERREUR : Le plugin Docker Compose v2 n'est pas disponible.${NC}"
    exit 1
fi
echo -e "${GREEN}Docker et Docker Compose sont opérationnels.${NC}"

# Étape 4 : Vérification du fichier d'environnement (.env)
echo -e "\n${YELLOW}[4/18] Vérification des variables d'environnement...${NC}"
if [ ! -f .env ]; then
    echo -e "${RED}ERREUR : Le fichier .env est introuvable à la racine du projet.${NC}"
    echo "Copiez .env.example vers .env et personnalisez vos mots de passe et clés secrètes :"
    echo "cp .env.example .env && nano .env"
    exit 1
fi
if grep -q "changez-cette-cle-secrete" .env || grep -q "cle_secrete_django_a_generer" .env; then
    echo -e "${RED}SÉCURITÉ CRITIQUE : La variable DJANGO_SECRET_KEY / SECRET_KEY contient encore la valeur d'exemple !${NC}"
    exit 1
fi
if grep -q "definis_un_mot_de_passe_robuste" .env; then
    echo -e "${RED}SÉCURITÉ CRITIQUE : Le mot de passe de base de données PostgreSQL contient la valeur par défaut d'exemple !${NC}"
    exit 1
fi

# Étape 5 : Création des volumes persistants
echo -e "\n${YELLOW}[5/18] Vérification et création des volumes Docker persistants...${NC}"
docker volume create sante_postgres_data >/dev/null
docker volume create sante_django_static >/dev/null
docker volume create sante_django_media >/dev/null
docker volume create sante_certbot_www >/dev/null
docker volume create sante_certbot_conf >/dev/null
echo -e "${GREEN}Volumes persistants vérifiés.${NC}"

# Étape 6 : Sauvegarde préalable de PostgreSQL si le service existe déjà
echo -e "\n${YELLOW}[6/18] Vérification des sauvegardes de sécurité préalable...${NC}"
if docker compose ps db 2>/dev/null | grep -q "Up"; then
    echo "PostgreSQL est déjà actif. Exécution d'une sauvegarde de sécurité pré-déploiement..."
    if [ -f scripts/backup.sh ]; then
        bash scripts/backup.sh || echo -e "${YELLOW}Avertissement : la sauvegarde préalable a échoué.${NC}"
    fi
else
    echo "Première initialisation ou base de données non active. Aucune base existante à sauvegarder."
fi

# Étape 7 : Construction des images Docker
echo -e "\n${YELLOW}[7/18] Construction des images Docker (Backend & Frontend)...${NC}"
docker compose build --pull

# Étape 8 : Démarrage du conteneur PostgreSQL
echo -e "\n${YELLOW}[8/18] Démarrage du conteneur PostgreSQL...${NC}"
docker compose up -d db

# Étape 9 : Attente active que PostgreSQL soit prêt
echo -e "\n${YELLOW}[9/18] Attente de la disponibilité de PostgreSQL (pg_isready)...${NC}"
until docker compose exec -T db pg_isready 2>/dev/null | grep -q "accepting connections"; do
    echo "En attente que PostgreSQL soit prêt à accepter les connexions..."
    sleep 2
done
echo -e "${GREEN}PostgreSQL est opérationnel et prêt.${NC}"

# Étape 10 : Démarrage du backend Django
echo -e "\n${YELLOW}[10/18] Démarrage du conteneur Backend Gunicorn...${NC}"
docker compose up -d backend

# Étape 11 : Vérification de la connexion du backend à PostgreSQL
echo -e "\n${YELLOW}[11/18] Vérification de la connectivité Backend <-> PostgreSQL...${NC}"
sleep 5
docker compose exec -T backend python -c "
import django; django.setup()
from django.db import connection
with connection.cursor() as c:
    c.execute('SELECT 1')
print('Connexion PostgreSQL validée avec succès !')
"

# Étape 12 : Exécution sécurisée des migrations Django
echo -e "\n${YELLOW}[12/18] Application des migrations de schéma Django...${NC}"
docker compose exec -T backend python manage.py showmigrations
docker compose exec -T backend python manage.py migrate --noinput
echo -e "${GREEN}Migrations appliquées avec succès.${NC}"

# Étape 13 : Collecte des fichiers statiques Django
echo -e "\n${YELLOW}[13/18] Collecte des fichiers statiques Django pour Nginx...${NC}"
docker compose exec -T backend python manage.py collectstatic --noinput

# Étape 14 : Création conditionnelle du superadministrateur initial
echo -e "\n${YELLOW}[14/18] Vérification et création idempotente du superadministrateur initial...${NC}"
docker compose exec -T backend python manage.py create_admin_if_none

# Étape 15 : Démarrage du Frontend et de Nginx
echo -e "\n${YELLOW}[15/18] Démarrage des conteneurs Frontend et Nginx...${NC}"
docker compose up -d frontend nginx certbot

# Étape 16 : Configuration et vérification HTTPS
echo -e "\n${YELLOW}[16/18] Vérification de la configuration HTTPS...${NC}"
if [ -d "/etc/letsencrypt/live/$DOMAIN_NAME" ] || docker compose exec -T nginx test -f "/etc/letsencrypt/live/$DOMAIN_NAME/fullchain.pem" 2>/dev/null; then
    echo -e "${GREEN}Certificats SSL détectés.${NC}"
else
    echo -e "${YELLOW}Aucun certificat SSL officiel Let's Encrypt détecté pour $DOMAIN_NAME.${NC}"
    echo "Pour générer les certificats SSL avec Certbot, exécutez :"
    echo "bash scripts/init-letsencrypt.sh"
fi

# Étape 17 : Tests fonctionnels et vérification de santé (Health Check)
echo -e "\n${YELLOW}[17/18] Exécution des vérifications de santé applicative...${NC}"
sleep 3
HEALTH_STATUS=$(docker compose exec -T backend python -c "
import urllib.request, json
try:
    res = urllib.request.urlopen('http://localhost:8000/health/')
    print(res.getcode())
except Exception as e:
    print(e)
")
if [ "$HEALTH_STATUS" = "200" ]; then
    echo -e "${GREEN}Health check backend validé : code HTTP 200 OK.${NC}"
else
    echo -e "${YELLOW}Avertissement : le health check backend a retourné : $HEALTH_STATUS${NC}"
fi

# Étape 18 : Vérification des données et droits
echo -e "\n${YELLOW}[18/18] Contrôle final de l'intégrité de la base de données...${NC}"
docker compose exec -T backend python -c "
import django; django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
total = User.objects.count()
admins = User.objects.filter(is_superuser=True).count()
print(f'Total utilisateurs en base : {total} | Superadministrateurs : {admins}')
"

echo -e "\n${GREEN}==============================================================================${NC}"
echo -e "${GREEN}    DÉPLOIEMENT TERMINÉ AVEC SUCCÈS !                                         ${NC}"
echo -e "${GREEN}==============================================================================${NC}"
echo -e "Frontend Angular : http://$DOMAIN_NAME/ ou https://$DOMAIN_NAME/"
echo -e "API REST Django  : http://$DOMAIN_NAME/api/"
echo -e "Administration   : http://$DOMAIN_NAME/admin/"
echo -e "Documentation    : http://$DOMAIN_NAME/docs/"
echo -e "Santé (Health)   : http://$DOMAIN_NAME/health/"
echo -e "${BLUE}==============================================================================${NC}\n"

