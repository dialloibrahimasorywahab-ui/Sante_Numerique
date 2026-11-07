# Backend Dockerfile - Santé Numérique (Django / DRF / Gunicorn)
FROM python:3.12-slim

# Empêcher Python d'écrire des fichiers .pyc et activer le stdout/stderr non bufférisé
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Dépendances système requises (compilation psycopg2 si besoin, curl pour les healthchecks)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Création d'un utilisateur non-root de sécurité (UID 1000)
RUN groupadd -g 1000 appgroup && \
    useradd -u 1000 -g appgroup -m -s /bin/bash appuser

# Installation des dépendances Python
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Création des répertoires statiques et médias avec permissions adaptées
RUN mkdir -p /app/staticfiles /app/media && \
    chown -R appuser:appgroup /app/staticfiles /app/media

# Copie du code applicatif
COPY --chown=appuser:appgroup . /app/

# Rendre le script entrypoint exécutable
RUN chmod +x /app/entrypoint.sh

# Bascule vers l'utilisateur non-root
USER appuser

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120"]

