from rest_framework import serializers
from .models import MouvementPatient
from localisation.localisationSerializers import LocalisationReadSerializer


class MouvementReadSerializer(serializers.ModelSerializer):
    localisation_origine_details = LocalisationReadSerializer(source="localisation_origine", read_only=True)
    localisation_destination_details = LocalisationReadSerializer(source="localisation_destination", read_only=True)
    type_mouvement_display = serializers.CharField(source="get_type_mouvement_display", read_only=True)
    sejour_reference = serializers.CharField(source="sejour.reference", read_only=True)

    class Meta:
        model = MouvementPatient
        fields = [
            "id",
            "sejour",
            "sejour_reference",
            "localisation_origine",
            "localisation_origine_details",
            "localisation_destination",
            "localisation_destination_details",
            "date_mouvement",
            "type_mouvement",
            "type_mouvement_display",
            "motif",
            "commentaire",
            "enregistre_par",
        ]


class MouvementTransfertCreateSerializer(serializers.Serializer):
    """Serializer pour déclencher un transfert de patient."""
    sejour = serializers.IntegerField(required=True)
    service = serializers.IntegerField(required=True)
    batiment = serializers.IntegerField(required=False, allow_null=True)
    chambre = serializers.IntegerField(required=False, allow_null=True)
    lit = serializers.IntegerField(required=False, allow_null=True)
    type_mouvement = serializers.ChoiceField(
        choices=MouvementPatient.TypeMouvement.choices,
        default=MouvementPatient.TypeMouvement.TRANSFERT_SERVICE,
    )
    date_mouvement = serializers.DateTimeField(required=False, allow_null=True)
    motif = serializers.CharField(required=True, allow_blank=False)
    commentaire = serializers.CharField(required=False, allow_blank=True)
