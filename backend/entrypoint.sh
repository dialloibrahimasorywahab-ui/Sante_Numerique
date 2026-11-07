#!/bin/sh
set -e

# Vérification de la disponibilité de PostgreSQL
if [ -n "$DATABASE_HOST" ] || [ -n "$DB_HOST" ]; then
    DB_H="${DATABASE_HOST:-$DB_HOST}"
    DB_P="${DATABASE_PORT:-${DB_PORT:-5432}}"
    echo "En attente de la disponibilité de PostgreSQL sur $DB_H:$DB_P..."
    while ! python -c "import socket; s = socket.socket(); s.settimeout(2); s.connect(('$DB_H', int('$DB_P'))); s.close()" 2>/dev/null; do
        sleep 1
    done
    echo "PostgreSQL est prêt !"
fi

# Collecte des fichiers statiques pour Nginx si nécessaire
if [ "$COLLECT_STATIC" = "1" ] || [ "$COLLECT_STATIC" = "true" ]; then
    echo "Collecte des fichiers statiques..."
    python manage.py collectstatic --noinput
fi

exec "$@"
