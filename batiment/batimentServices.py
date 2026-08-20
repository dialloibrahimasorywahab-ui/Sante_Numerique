from .batimentRepositories import BatimentRepository
from .models import Batiment


class BatimentService:

    def __init__(self):
        self.repository = BatimentRepository()

    def create_batiment(self, **data):
        return self.repository.create_batiment(**data)

    def get_batiment(self, batiment_id):
        return self.repository.get_batiment(batiment_id)

    def get_batiment_by_nom(self, nom):
        return self.repository.get_batiment_by_nom(nom)

    def get_all_batiments(self):
        return self.repository.get_all_batiments()

    def search_batiments(self, query):
        return self.repository.search_batiments(query)

    def get_or_create_batiment(self, nom, nombre_chambre=0, description=""):
        if not nom:
            return None
        batiment = self.get_batiment_by_nom(nom)
        if batiment:
            return batiment
        return self.create_batiment(
            nom=nom.strip(),
            nombre_chambre=nombre_chambre,
            description=description
        )

    def update_batiment(self, batiment, **data):
        return self.repository.update_batiment(batiment, **data)

    def delete_batiment(self, batiment):
        return self.repository.delete_batiment(batiment)

    def sync_nombre_chambres(self, batiment_id):
        batiment = self.get_batiment(batiment_id)
        if batiment:
            return batiment.sync_nombre_chambres()
        return 0

    def seed_default_batiments(self):
        default_batiments = [
            {"nom": "Bâtiment Principal A", "description": "Bâtiment principal accueillant la médecine générale et les consultations.", "nombre_chambre": 20},
            {"nom": "Pavillon des Urgences", "description": "Bâtiment dédié aux soins d'urgence et réanimation.", "nombre_chambre": 15},
            {"nom": "Bâtiment Maternité B", "description": "Soins gynécologiques et espace maternité.", "nombre_chambre": 12},
            {"nom": "Bloc Opératoire & Chirurgie", "description": "Bâtiment réservé aux blocs opératoires et suivi post-chirurgical.", "nombre_chambre": 10},
            {"nom": "Centre Administratif", "description": "Accueil central, administration et direction.", "nombre_chambre": 0},
        ]
        created = []
        for bat_data in default_batiments:
            bat, _ = Batiment.objects.get_or_create(
                nom=bat_data["nom"],
                defaults={
                    "description": bat_data["description"],
                    "nombre_chambre": bat_data["nombre_chambre"]
                }
            )
            created.append(bat)
        return created

