from rest_framework import serializers
from .models import NotificationHospitaliere


class NotificationHospitaliereSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_type_notification_display', read_only=True)
    idNotification = serializers.IntegerField(source='id_notification', read_only=True)
    typeNotification = serializers.CharField(source='type_notification', read_only=True)
    destinataireRole = serializers.CharField(source='destinataire_role', read_only=True)
    dateCreation = serializers.DateTimeField(source='date_creation', read_only=True)

    class Meta:
        model = NotificationHospitaliere
        fields = [
            'id_notification',
            'idNotification',
            'type_notification',
            'typeNotification',
            'type_display',
            'titre',
            'message',
            'donnees',
            'destinataire_role',
            'destinataireRole',
            'destinataire_user',
            'lu',
            'date_creation',
            'dateCreation',
            'actif',
        ]
        read_only_fields = ['id_notification', 'date_creation']


class TriggerAlertSerializer(serializers.Serializer):
    type_notification = serializers.ChoiceField(
        choices=NotificationHospitaliere.TypeNotification.choices,
        default=NotificationHospitaliere.TypeNotification.INFO
    )
    titre = serializers.CharField(max_length=200)
    message = serializers.CharField()
    destinataire_role = serializers.ChoiceField(
        choices=NotificationHospitaliere.DestinataireRole.choices,
        default=NotificationHospitaliere.DestinataireRole.TOUS
    )
    donnees = serializers.JSONField(required=False, default=dict)
