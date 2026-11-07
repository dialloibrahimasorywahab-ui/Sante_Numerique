import logging
from django.db import connection
from django.http import JsonResponse

logger = logging.getLogger(__name__)


def health_check_view(request):
    """
    Health check endpoint pour les sondes Docker, Compose, Nginx et monitoring.
    Vérifie le runtime Django et la connectivité à PostgreSQL.
    Ne divulgue aucune information d'infrastructure ou de configuration sensible.
    """
    db_healthy = False
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1;")
            row = cursor.fetchone()
            if row and row[0] == 1:
                db_healthy = True
    except Exception as exc:
        logger.error("Échec de la sonde de santé sur la base de données: %s", exc)
        db_healthy = False

    if db_healthy:
        return JsonResponse(
            {
                "status": "healthy",
                "service": "sante-numerique-backend",
                "database": "connected",
            },
            status=200,
        )

    return JsonResponse(
        {
            "status": "unhealthy",
            "service": "sante-numerique-backend",
            "database": "disconnected",
        },
        status=503,
    )

