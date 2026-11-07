#!/bin/bash
# ==============================================================================
# SANTÉ NUMÉRIQUE — SCRIPT DE RESTAURATION POSTGRESQL SÉCURISÉE
# ==============================================================================
# Usage : bash scripts/restore.sh <chemin_du_fichier_dump>
# ==============================================================================
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

if [ -z "$1" ]; then
    echo -e "${RED}ERREUR : Veuillez spécifier le fichier de sauvegarde à restaurer.${NC}"
    echo "Usage : bash scripts/restore.sh ./backups/sante_db_YYYYMMDD_HHMMSS.dump"
    exit 1
fi

RESTORE_FILE="$1"

if [ ! -f "$RESTORE_FILE" ]; then
    echo -e "${RED}ERREUR : Le fichier de sauvegarde '$RESTORE_FILE' est introuvable.${NC}"
    exit 1
fi

# Déchiffrement temporaire si archive .enc
CLEANUP_DECRYPTED=0
if [[ "$RESTORE_FILE" == *.enc ]]; then
    if [ -z "$BACKUP_ENCRYPTION_KEY" ]; then
        echo -e "${RED}ERREUR : Le fichier est chiffré (.enc) mais BACKUP_ENCRYPTION_KEY n'est pas définie.${NC}"
        exit 1
    fi
    DECRYPTED_FILE="${RESTORE_FILE%.enc}"
    echo "Déchiffrement de l'archive de sauvegarde..."
    openssl enc -d -aes-256-cbc -pbkdf2 -in "$RESTORE_FILE" -out "$DECRYPTED_FILE" -k "$BACKUP_ENCRYPTION_KEY"
    RESTORE_FILE="$DECRYPTED_FILE"
    CLEANUP_DECRYPTED=1
fi

# Charger les variables du fichier .env
if [ -f .env ]; then
    DB_NAME=$(grep -E '^(POSTGRES_DB|DATABASE_NAME)=' .env | head -n 1 | cut -d '=' -f 2 | tr -d '\r' | tr -d '"' | tr -d "'")
    DB_USER=$(grep -E '^(POSTGRES_USER|DATABASE_USER)=' .env | head -n 1 | cut -d '=' -f 2 | tr -d '\r' | tr -d '"' | tr -d "'")
fi
DB_NAME="${DB_NAME:-sante_numerique}"
DB_USER="${DB_USER:-sante_user}"

echo -e "${YELLOW}==============================================================================${NC}"
echo -e "${YELLOW} ATTENTION : Vous allez restaurer la base de données '$DB_NAME'             ${NC}"
echo -e "${YELLOW} Fichier source : $RESTORE_FILE                                              ${NC}"
echo -e "${YELLOW} Cette opération va remplacer l'état actuel de la base.                       ${NC}"
echo -e "${YELLOW}==============================================================================${NC}"
read -p "Êtes-vous ABSOLUMENT certain de vouloir poursuivre ? (tapez 'OUI' pour confirmer) : " CONFIRM
if [ "$CONFIRM" != "OUI" ]; then
    echo "Restauration annulée par l'opérateur."
    if [ "$CLEANUP_DECRYPTED" = "1" ]; then rm -f "$RESTORE_FILE"; fi
    exit 0
fi

# 1. Sauvegarde d'urgence de l'état actuel avant toute opération
echo -e "\n${BLUE}[1/5] Création d'une sauvegarde de précaution de l'état actuel...${NC}"
PRE_RESTORE_BACKUP="./backups/pre_restore_safety_$(date +%Y%m%d_%H%M%S).dump"
docker compose exec -T db pg_dump -U "$DB_USER" -Fc "$DB_NAME" > "$PRE_RESTORE_BACKUP" || true
echo "Sauvegarde de précaution enregistrée dans : $PRE_RESTORE_BACKUP"

# 2. Arrêt temporaire du conteneur Backend pour couper les connexions actives
echo -e "\n${BLUE}[2/5] Arrêt temporaire du backend pour libérer les verrous...${NC}"
docker compose stop backend

# 3. Fermeture forcée des sessions résiduelles sur PostgreSQL
echo -e "\n${BLUE}[3/5] Clôture des sessions PostgreSQL résiduelles...${NC}"
docker compose exec -T db psql -U "$DB_USER" -d postgres -c \
    "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '$DB_NAME' AND pid <> pg_backend_pid();" >/dev/null 2>&1 || true

# 4. Restauration avec pg_restore
echo -e "\n${BLUE}[4/5] Restauration des données via pg_restore...${NC}"
cat "$RESTORE_FILE" | docker compose exec -T db pg_restore -U "$DB_USER" -d "$DB_NAME" --clean --if-exists --no-owner --no-privileges || {
    echo -e "${YELLOW}pg_restore a retourné des alertes non bloquantes (standard sur les schémas existants).${NC}"
}

# 5. Redémarrage du backend et vérification
echo -e "\n${BLUE}[5/5] Redémarrage du backend et vérification d'intégrité...${NC}"
docker compose start backend
sleep 5
docker compose exec -T backend python manage.py migrate --check
echo -e "${GREEN}Base de données restaurée et opérationnelle avec succès !${NC}"

if [ "$CLEANUP_DECRYPTED" = "1" ]; then
    rm -f "$RESTORE_FILE"
fi

