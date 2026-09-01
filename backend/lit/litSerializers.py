# pyrefly: ignore [missing-import]
from rest_framework import serializers
from .models import Lit
from chambre.models import Chambre
from chambre.chambreSerializers import ChambreSerializer


class LitSerializer(serializers.ModelSerializer):
    id_chambre = serializers.PrimaryKeyRelatedField(
        queryset=Chambre.objects.all(),
        source='chambre',
        write_only=True,
        required=False
    )
    chambre_detail = ChambreSerializer(source='chambre', read_only=True)
    etatDisplay = serializers.CharField(source="get_etat_display", read_only=True)

    class Meta:
        model = Lit
        fields = [
            'id',
            'idLit',
            'id_chambre',
            'chambre_detail',
            'numero_lit',
            'etat',
            'etatDisplay',
        ]

    def to_internal_value(self, data):
        if isinstance(data, dict):
            if 'chambre_id' in data and 'id_chambre' not in data:
                data = data.copy()
                data['id_chambre'] = data['chambre_id']
        return super().to_internal_value(data)

    def validate_etat(self, value):
        if value not in Lit.EtatLit.values:
            valid_choices = ", ".join(Lit.EtatLit.values)
            raise serializers.ValidationError(f"État invalide. Choix valides: {valid_choices}")
        return value

    def validate(self, attrs):
        chambre = attrs.get('chambre') or (self.instance.chambre if self.instance else None)
        if not self.instance and 'chambre' not in attrs:
            raise serializers.ValidationError({"id_chambre": "Le champ id_chambre est obligatoire."})

        if not self.instance and chambre:
            lits_count = chambre.lits.count()
            if lits_count >= chambre.capacite:
                raise serializers.ValidationError({
                    "id_chambre": f"La capacité maximale de la Chambre {chambre.numero_chambre} ({chambre.capacite} lit(s)) est déjà atteinte."
                })
        return attrs

