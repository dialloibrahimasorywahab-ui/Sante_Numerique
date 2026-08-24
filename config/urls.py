"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# pyrefly: ignore [missing-import]
from django.contrib import admin
# pyrefly: ignore [missing-import]
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.usersURLs')),
    path('user/', include('users.usersURLs')),
    path('patients/', include('patients.patientUrls')),
    path('patient/', include('patients.patientUrls')),
    path('medecins/', include('medecin.medecinUrls')),
    path('medecin/', include('medecin.medecinUrls')),
    path('personnels/', include('personnel.personnelUrls')),
    path('personnel/', include('personnel.personnelUrls')),
    path('services/', include('services.serviceUrls')),
    path('service/', include('services.serviceUrls')),
    path('batiments/', include('batiment.batimentUrls')),
    path('batiment/', include('batiment.batimentUrls')),
    path('chambres/', include('chambre.chambreUrls')),
    path('chambre/', include('chambre.chambreUrls')),
    path('lits/', include('lit.litUrls')),
    path('lit/', include('lit.litUrls')),
    path('rendezvous/', include('rendezvous.rendezvousUrls')),
    path('rdv/', include('rendezvous.rendezvousUrls')),
    path('natalite/', include('natalite.nataliteUrls')),
    path('natalites/', include('natalite.nataliteUrls')),
    path('mortalite/', include('mortalite.mortaliteUrls')),
    path('mortalites/', include('mortalite.mortaliteUrls')),
]


