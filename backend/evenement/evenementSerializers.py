from rest_framework import serializers
from .models import EvenementParcours


class EvenementReadSerializer(serializers.ModelSerializer):
    type_evenement_display = serializers.CharField(source="get_type_evenement_display", read_only=True)
    importance_display = serializers.CharField(source="get_importance_display", read_only=True)
    sejour_reference = serializers.CharField(source="sejour.reference", read_only=True)
    declare_par_nom = serializers.SerializerMethodField()

    class Meta:
        model = EvenementParcours
        fields = [
            "id",
            "sejour",
            "sejour_reference",
            "type_evenement",
            "type_evenement_display",
            "titre",
            "description",
            "date_evenement",
            "declare_par",
            "declare_par_nom",
            "importance",
            "importance_display",
            "donnees_additionnelles",
            "actif",
            "created_at",
        ]

    def get_declare_par_nom(self, obj):
        if not obj.declare_par:
            return None
        return f"{obj.declare_par.first_name} {obj.declare_par.last_name}".strip() or obj.declare_par.username


class EvenementCreateSerializer(serializers.ModelSerializer):
    sejour = serializers.IntegerField(required=True)

    class Meta:
        model = EvenementParcours
        fields = [
            "sejour",
            "type_evenement",
            "titre",
            "description",
            "date_evenement",
            "importance",
            "donnees_additionnelles",
        ]
