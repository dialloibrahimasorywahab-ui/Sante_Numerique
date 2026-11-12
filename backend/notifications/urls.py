from django.urls import path
from .views import stream_notifications, list_notifications, mark_as_read, mark_all_as_read, trigger_alert

urlpatterns = [
    path('', list_notifications, name='notification-list'),
    path('stream/', stream_notifications, name='notification-stream'),
    path('<int:notif_id>/lire/', mark_as_read, name='notification-mark-read'),
    path('lire-tout/', mark_all_as_read, name='notification-mark-all-read'),
    path('declencher/', trigger_alert, name='notification-trigger-alert'),
]
