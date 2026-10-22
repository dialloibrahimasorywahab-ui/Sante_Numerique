from django.urls import path, include

urlpatterns = [
    path('users/', include('users.usersURLs')),
    path('patients/', include('patients.patientUrls')),
    path('medecins/', include('medecin.medecinUrls')),
    path('personnel/', include('personnel.personnelUrls')),
    path('services/', include('services.serviceUrls')),
    path('batiments/', include('batiment.batimentUrls')),
    path('chambres/', include('chambre.chambreUrls')),
    path('lits/', include('lit.litUrls')),
    path('rendezvous/', include('rendezvous.rendezvousUrls')),
    path('natalite/', include('natalite.nataliteUrls')),
    path('mortalite/', include('mortalite.mortaliteUrls')),
    path('hospitalisations/', include('hospitalisation.hospitalisationUrls')),
    path('consultations/', include('consultation.consultationUrls')),
    path('frais_consultations/', include('frais_consultation.fraisUrls')),
    path('ordonnances/', include('ordonnance.ordonnanceUrls')),
    path('lignes_ordonnances/', include('ligne_ordonnance.ligneUrls')),
    path('sejours/', include('sejour.sejourUrls')),
    path('localisations/', include('localisation.localisationUrls')),
    path('mouvements/', include('mouvement.mouvementUrls')),
    path('evenements/', include('evenement.evenementUrls')),
]


