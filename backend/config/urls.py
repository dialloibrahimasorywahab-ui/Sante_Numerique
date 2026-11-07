"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
"""
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from .views import health_check_view


urlpatterns = [
    # Redirection de la racine vers Swagger (quand le backend est consulté directement)
    path('', RedirectView.as_view(url='swagger/', permanent=False), name='index'),

    # Sondes de santé (Health Check)
    path('health/', health_check_view, name='health_check'),
    path('api/health/', health_check_view, name='api_health_check'),

    # Documentation Swagger UI & OpenAPI 3.0
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui-docs'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # Administration Django
    path('admin/', admin.site.urls),

    # Routes API avec préfixe standard /api/
    path('api/', include('common.commonURLs.urls')),

    # Alias direct pour compatibilité ascendante et suite de tests existante
    path('', include('common.commonURLs.urls')),
]
