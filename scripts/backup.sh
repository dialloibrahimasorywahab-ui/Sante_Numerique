#!/bin/bash
# ==============================================================================
# SANTÉ NUMÉRIQUE — SCRIPT DE SAUVEGARDE POSTGRESQL AUTOMATISÉE
# ==============================================================================
# Format : pg_dump -Fc (format personnalisé compressé et intègre)
# Rétention : 30 jours
# ==============================================================================
set -e

BACKUP_DIR="${BACKUP_DIR:-./backups}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/sante_db_$TIMESTAMP.dump"
LOG_FILE="$BACKUP_DIR/backup.log"
RETENTION_DAYS=30

mkdir -p "$BACKUP_DIR"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Début de la sauvegarde de la base de données..." | tee -a "$LOG_FILE"

# Charger les variables du fichier .env si présent
if [ -f .env ]; then
    DB_NAME=$(grep -E '^(POSTGRES_DB|DATABASE_NAME)=' .env | head -n 1 | cut -d '=' -f 2 | tr -d '\r' | tr -d '"' | tr -d "'")
    DB_USER=$(grep -E '^(POSTGRES_USER|DATABASE_USER)=' .env | head -n 1 | cut -d '=' -f 2 | tr -d '\r' | tr -d '"' | tr -d "'")
fi

DB_NAME="${DB_NAME:-sante_numerique}"
DB_USER="${DB_USER:-sante_user}"

# Exécution de pg_dump via le conteneur Docker 'db'
if ! docker compose exec -T db pg_dump -U "$DB_USER" -Fc "$DB_NAME" > "$BACKUP_FILE"; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERREUR CRITIQUE : Échec de l'exécution de pg_dump !" | tee -a "$LOG_FILE"
    rm -f "$BACKUP_FILE"
    exit 1
fi

# Vérification de l'intégrité et de la taille du fichier
FILE_SIZE=$(stat -c%s "$BACKUP_FILE" 2>/dev/null || stat -f%z "$BACKUP_FILE" 2>/dev/null || echo 0)
if [ "$FILE_SIZE" -le 1024 ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERREUR : Le fichier de sauvegarde est anormalement petit (${FILE_SIZE} octets) !" | tee -a "$LOG_FILE"
    exit 1
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Sauvegarde réussie : $BACKUP_FILE (${FILE_SIZE} octets)." | tee -a "$LOG_FILE"

# Chiffrement optionnel avec OpenSSL si une clé est définie
if [ -n "$BACKUP_ENCRYPTION_KEY" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Chiffrement de l'archive de sauvegarde..." | tee -a "$LOG_FILE"
    openssl enc -aes-256-cbc -salt -pbkdf2 -in "$BACKUP_FILE" -out "$BACKUP_FILE.enc" -k "$BACKUP_ENCRYPTION_KEY"
    rm -f "$BACKUP_FILE"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Archive chiffrée avec succès : $BACKUP_FILE.enc" | tee -a "$LOG_FILE"
fi

# Nettoyage des sauvegardes datant de plus de RETENTION_DAYS jours
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Application de la politique de rétention ($RETENTION_DAYS jours)..." | tee -a "$LOG_FILE"
find "$BACKUP_DIR" -type f \( -name "sante_db_*.dump" -o -name "sante_db_*.dump.enc" \) -mtime +$RETENTION_DAYS -exec rm -f {} \;

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Sauvegarde et maintenance terminées avec succès." | tee -a "$LOG_FILE"

