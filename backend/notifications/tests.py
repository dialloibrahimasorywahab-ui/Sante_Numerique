from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User
from .models import NotificationHospitaliere
from .services import NotificationService


class NotificationHospitaliereTests(APITestCase):

    def setUp(self):
        self.admin = User.objects.create_superuser(
            login="admin_notif",
            email="admin_notif@hopital.fr",
            password="AdminPassword123!",
            nom="Admin",
            prenom="Directeur",
            telephone="0600000071"
        )

        self.doctor = User.objects.create_user(
            login="doctor_notif",
            email="doctor_notif@hopital.fr",
            password="DoctorPassword123!",
            nom="Barry",
            prenom="Mamadou",
            telephone="0600000072",
            role=User.Role.MEDECIN
        )

        self.patient = User.objects.create_user(
            login="patient_notif",
            email="patient_notif@hopital.fr",
            password="PatientPassword123!",
            nom="Sow",
            prenom="Aissatou",
            telephone="0600000073",
            role=User.Role.PATIENT
        )

        self.service = NotificationService()

    def test_emit_and_filter_notifications(self):
        # Emission notification urgente
        notif_urgence = self.service.emettre_notification(
            type_notification=NotificationHospitaliere.TypeNotification.LIT_URGENCE,
            titre="Lit de réanimation disponible",
            message="Le lit #104 au Pavillon Urgences a été libéré.",
            destinataire_role=NotificationHospitaliere.DestinataireRole.TOUS,
            donnees={"id_lit": 104, "statut": "DISPONIBLE"}
        )
        self.assertIsNotNone(notif_urgence.id_notification)

        # Le médecin se connecte et liste ses notifications
        self.client.force_authenticate(user=self.doctor)
        res = self.client.get("/notifications/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # La notification TOUS est visible pour le médecin
        results = res.data.get("results", res.data)
        self.assertTrue(any(n["id_notification"] == notif_urgence.id_notification for n in results))

    def test_mark_as_read(self):
        notif = self.service.emettre_notification(
            type_notification=NotificationHospitaliere.TypeNotification.PATIENT_ARRIVE,
            titre="Arrivée patient en salle d'attente",
            message="Mme Sow est arrivée pour sa consultation de 10h30.",
            destinataire_user=self.doctor
        )

        self.client.force_authenticate(user=self.doctor)
        res = self.client.post(f"/notifications/{notif.id_notification}/lire/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        notif.refresh_from_db()
        self.assertTrue(notif.lu)

    def test_trigger_alert_api(self):
        self.client.force_authenticate(user=self.doctor)
        payload = {
            "type_notification": "LIT_URGENCE",
            "titre": "Demande immédiate lit réanimation",
            "message": "Patient polytraumatisé en approche aux urgences",
            "destinataire_role": "MEDECIN"
        }
        res = self.client.post("/notifications/declencher/", payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["type_notification"], "LIT_URGENCE")

    def test_patient_cannot_see_hospital_governance_notifications(self):
        # Emission d'alertes internes de gouvernance (lits et salle d'attente)
        self.service.emettre_notification(
            type_notification=NotificationHospitaliere.TypeNotification.LIT_URGENCE,
            titre="Affectation Lit Réa 1",
            message="Lit 1 affecté à un autre patient",
            destinataire_role=NotificationHospitaliere.DestinataireRole.TOUS
        )
        self.service.emettre_notification(
            type_notification=NotificationHospitaliere.TypeNotification.PATIENT_ARRIVE,
            titre="Patient en salle d'attente",
            message="M. Traore est en salle d'attente",
            destinataire_role=NotificationHospitaliere.DestinataireRole.MEDECIN
        )

        # Le patient se connecte : les alertes hospitalières internes ne doivent JAMAIS apparaître
        self.client.force_authenticate(user=self.patient)
        res = self.client.get("/notifications/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        results = res.data.get("results", res.data)
        self.assertEqual(len(results), 0, "Le patient ne doit voir aucune alerte interne de gouvernance hospitalière.")

        # Si une notification est adressée spécifiquement au patient
        notif_patient = self.service.emettre_notification(
            type_notification=NotificationHospitaliere.TypeNotification.INFO,
            titre="Votre consultation est confirmée",
            message="Votre RDV de demain à 09h00 est validé.",
            destinataire_role=NotificationHospitaliere.DestinataireRole.PATIENT,
            destinataire_user=self.patient
        )
        res2 = self.client.get("/notifications/")
        results2 = res2.data.get("results", res2.data)
        self.assertEqual(len(results2), 1)
        self.assertEqual(results2[0]["id_notification"], notif_patient.id_notification)
