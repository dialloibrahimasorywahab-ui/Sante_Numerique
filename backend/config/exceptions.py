from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    """
    Gestionnaire d'exceptions DRF personnalisé :
    Garantit que les réponses d'erreur contiennent à la fois 'detail' (standard DRF)
    et 'error' (standard de l'API Santé Numérique) pour une cohérence totale des clients.
    """
    response = exception_handler(exc, context)

    if response is not None and isinstance(response.data, dict):
        if 'detail' in response.data and 'error' not in response.data:
            response.data['error'] = str(response.data['detail'])
        elif 'error' in response.data and 'detail' not in response.data:
            response.data['detail'] = response.data['error']

    return response
