import logging
import re
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from config.pagination import paginate_response
from config.permissions import IsMedecinOuAdmin, IsStaffOrAdmin, deny_unless_owner_or_staff
from config.schema_helpers import (
    ErrorResponseSerializer,
    HARD_DELETE_PARAM,
    MessageResponseSerializer,
    PAGINATION_PARAMS,
    SEARCH_PARAM,
)
from .models import Hospitalisation
from .hospitalisationSerializers import HospitalisationReadSerializer, HospitalisationSerializer
from .hospitalisationServices import HospitalisationService

logger = logging.getLogger(__name__)
hospitalisation_service = HospitalisationService()


@extend_schema(
    tags=["Hospitalisation / Admissions"],
    summary="Lister ou créer une admission hospitalière",
    description="GET: Liste l'ensemble des admissions avec filtres (patient, médecin, lit, statut, recherche, all).\nPOST: Enregistre l'admission d'un patient. Supporte la sélection d'un patient existant ou la création atomique d'un nouveau patient sans doublon.",
    parameters=[
        OpenApiParameter(name="patient_id", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, required=False, description="Filtrer par identifiant patient."),
        OpenApiParameter(name="medecin_id", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, required=False, description="Filtrer par identifiant médecin."),
        OpenApiParameter(name="lit_id", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, required=False, description="Filtrer par identifiant du lit."),
        OpenApiParameter(name="statut", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, required=False, description="Filtrer par statut (PROGRAMMEE, EN_COURS, TERMINEE, ANNULEE)."),
        OpenApiParameter(name="all", type=OpenApiTypes.BOOL, location=OpenApiParameter.QUERY, required=False, description="Inclure aussi les hospitalisations inactives/archivées si true."),
        SEARCH_PARAM,
        *PAGINATION_PARAMS,
    ],
    request=HospitalisationSerializer,
    responses={
        200: HospitalisationReadSerializer(many=True),
        201: HospitalisationReadSerializer,
        400: ErrorResponseSerializer,
    },
)
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def hospitalisation_list_create_view(request):
    if request.method == "GET":
        user_role = getattr(request.user, "role", None)
        actif_only = request.query_params.get("all", "false").lower() != "true"
        qs = hospitalisation_service.repository.get_all_hospitalisations(actif_only=actif_only)

        if user_role == "ADMINISTRATEUR":
            pass
        elif user_role in ["MEDECIN", "INFIRMIER"]:
            pass
        elif user_role == "PATIENT":
            qs = qs.filter(patient__id_utilisateur=request.user)
        else:
            return Response({"error": "Accès réservé au personnel soignant, administrateurs et patients autorisés."}, status=status.HTTP_403_FORBIDDEN)

        patient_id = request.query_params.get("patient_id") or request.query_params.get("id_patient")
        if patient_id:
            qs = qs.filter(patient_id=patient_id)

        medecin_id = request.query_params.get("medecin_id") or request.query_params.get("id_medecin")
        if medecin_id:
            qs = qs.filter(medecin_id=medecin_id)

        lit_id = request.query_params.get("lit_id") or request.query_params.get("id_lit")
        if lit_id:
            qs = qs.filter(lit_id=lit_id)

        statut_param = request.query_params.get("statut")
        if statut_param:
            qs = qs.filter(statut=statut_param)

        search_query = request.query_params.get("search")
        if search_query:
            qs = qs.filter(
                patient__id_utilisateur__nom__icontains=search_query
            ) | qs.filter(
                patient__id_utilisateur__prenom__icontains=search_query
            ) | qs.filter(
                motif__icontains=search_query
            )

        return paginate_response(qs, request, HospitalisationReadSerializer)

    elif request.method == "POST":
        if getattr(request.user, "role", None) not in ["MEDECIN", "ADMINISTRATEUR"]:
            return Response({"error": "Seul un médecin ou administrateur peut enregistrer une admission."}, status=status.HTTP_403_FORBIDDEN)

        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)

        # Sécurité : Le médecin connecté est identifié et assigné automatiquement sans faire confiance à un id falsifié
        if getattr(request.user, "role", None) == "MEDECIN":
            from medecin.models import Medecin
            med_instance = Medecin.objects.filter(id_utilisateur=request.user).first()
            if med_instance:
                data["medecin"] = med_instance.pk

        serializer = HospitalisationSerializer(data=data)
        if serializer.is_valid():
            try:
                val_data = serializer.validated_data.copy()

                is_nouveau = val_data.pop('nouveau_patient', False) or (
                    not val_data.get('patient') and bool(val_data.get('nom'))
                )

                patient_account_info = None

                # Extraction des informations médicales enrichies
                priorite = val_data.pop('priorite', 'NORMAL') or 'NORMAL'
                symptomes = (val_data.pop('symptomes', '') or '').strip()
                diagnostic_provisoire = (val_data.pop('diagnostic_provisoire', '') or '').strip()
                service_nom = (val_data.pop('service_nom', '') or '').strip()
                antecedents = (val_data.pop('antecedents', '') or '').strip()
                allergies = (val_data.pop('allergies', '') or '').strip()
                traitements_en_cours = (val_data.pop('traitements_en_cours', '') or '').strip()
                raw_observation = (val_data.pop('observation', '') or '').strip()

                # Construction structurée des observations médicales
                obs_sections = []
                if priorite and priorite != 'NORMAL':
                    obs_sections.append(f"[Priorité]: {priorite}")
                if service_nom:
                    obs_sections.append(f"[Service]: {service_nom}")
                if symptomes:
                    obs_sections.append(f"[Symptômes]: {symptomes}")
                if diagnostic_provisoire:
                    obs_sections.append(f"[Diagnostic provisoire]: {diagnostic_provisoire}")
                if antecedents:
                    obs_sections.append(f"[Antécédents]: {antecedents}")
                if allergies:
                    obs_sections.append(f"[Allergies]: {allergies}")
                if traitements_en_cours:
                    obs_sections.append(f"[Traitements en cours]: {traitements_en_cours}")
                if raw_observation:
                    obs_sections.append(f"[Notes]: {raw_observation}")

                val_data['observation'] = "\n".join(obs_sections)

                # RÈGLE MÉTIER OBLIGATOIRE :
                # Statut initial EN_COURS et pas de date de sortie enregistrée à l'admission
                val_data['statut'] = Hospitalisation.StatutHospitalisation.EN_COURS
                val_data['date_sortie'] = None

                # TRANSACTION ATOMIQUE COMPLÈTE
                with transaction.atomic():
                    if is_nouveau:
                        from patients.models import Patient
                        from patients.patientServices import PatientService
                        from users.models import User

                        nom = (val_data.pop('nom', '') or '').strip()
                        prenom = (val_data.pop('prenom', '') or '').strip()
                        telephone = (val_data.pop('telephone', '') or '').strip()
                        email = val_data.pop('email', None)
                        date_naissance = val_data.pop('date_naissance', None)
                        sexe = val_data.pop('sexe', 'M') or 'M'
                        adresse = (val_data.pop('adresse', '') or '').strip()
                        groupe_sanguin = (val_data.pop('groupe_sanguin', 'O+') or 'O+').strip()
                        numero_securite_sociale = val_data.pop('numero_securite_sociale', None)
                        personne_a_contacter = (val_data.pop('personne_a_contacter', '') or '').strip()

                        # Vérification anti-doublon : Si un patient existe déjà avec ce téléphone, on l'associe sans créer de doublon
                        existing_patient = Patient.objects.filter(id_utilisateur__telephone=telephone).first()
                        if existing_patient:
                            val_data['patient'] = existing_patient
                            patient_account_info = {
                                'patient_id': existing_patient.id_patient,
                                'nom': existing_patient.nom,
                                'prenom': existing_patient.prenom,
                                'telephone': existing_patient.id_utilisateur.telephone,
                                'doublon_evite': True,
                                'message': "Ce numéro de téléphone correspond à un patient déjà enregistré. Son dossier existant a été automatiquement lié sans créer de doublon."
                            }
                        else:
                            clean_nom = re.sub(r'[^a-zA-Z0-9]', '', nom.lower())
                            clean_prenom = re.sub(r'[^a-zA-Z0-9]', '', prenom.lower())
                            base_login = f"patient.{clean_prenom}.{clean_nom}" if clean_prenom and clean_nom else f"patient.{telephone[-6:] if len(telephone)>=6 else 'nouveau'}"

                            login_candidate = base_login
                            suffix = 1
                            while User.objects.filter(login=login_candidate).exists():
                                login_candidate = f"{base_login}{suffix}"
                                suffix += 1

                            if not email:
                                email = f"{login_candidate}@santepro.local"

                            temp_pwd = "Securite2026!"

                            patient_service = PatientService()
                            new_patient = patient_service.createPatient(
                                nom=nom,
                                prenom=prenom,
                                telephone=telephone,
                                email=email,
                                login=login_candidate,
                                mot_de_passe=temp_pwd,
                                date_naissance=date_naissance,
                                sexe=sexe,
                                adresse=adresse,
                                groupe_sanguin=groupe_sanguin,
                                numero_securite_sociale=numero_securite_sociale or '',
                                personne_a_contacter=personne_a_contacter,
                            )
                            val_data['patient'] = new_patient

                            patient_account_info = {
                                'login': login_candidate,
                                'email': email,
                                'mot_de_passe_initial': temp_pwd,
                                'patient_id': new_patient.id_patient,
                                'nom': nom,
                                'prenom': prenom,
                                'message': "Dossier patient et espace personnel créés avec succès."
                            }
                    else:
                        for extra_field in ['nom', 'prenom', 'telephone', 'email', 'date_naissance', 'sexe', 'adresse', 'groupe_sanguin', 'numero_securite_sociale', 'personne_a_contacter', 'nouveau_patient']:
                            val_data.pop(extra_field, None)

                    # Si le médecin est manquant et l'utilisateur est médecin
                    if not val_data.get('medecin') and getattr(request.user, "role", None) == "MEDECIN":
                        from medecin.models import Medecin
                        med_obj = Medecin.objects.filter(id_utilisateur=request.user).first()
                        if med_obj:
                            val_data['medecin'] = med_obj

                    hospitalisation = hospitalisation_service.admettre_patient(**val_data)

                # Émission d'alerte temps réel pour l'affectation de lit
                try:
                    from notifications.services import NotificationService
                    from notifications.models import NotificationHospitaliere
                    lit_obj = getattr(hospitalisation, 'lit', None)
                    lit_label = f"Lit #{lit_obj.numero_lit}" if lit_obj and hasattr(lit_obj, 'numero_lit') else f"Lit #{getattr(lit_obj, 'id', 'N/A')}"
                    pat = getattr(hospitalisation, 'patient', None)
                    pat_user = getattr(pat, 'id_utilisateur', None) if pat else None
                    pat_nom = f"{pat_user.prenom} {pat_user.nom}" if pat_user else f"Patient #{hospitalisation.patient_id}"

                    NotificationService().emettre_notification(
                        type_notification=NotificationHospitaliere.TypeNotification.LIT_URGENCE,
                        titre=f"Nouvelle Admission : {lit_label}",
                        message=f"Admission hospitalière pour {pat_nom} ({lit_label}). Motif : {hospitalisation.motif or 'Soins continus'}.",
                        destinataire_role=NotificationHospitaliere.DestinataireRole.TOUS,
                        donnees={
                            "id_hospitalisation": hospitalisation.id,
                            "id_admission": hospitalisation.id,
                            "id_patient": hospitalisation.patient_id,
                            "id_lit": getattr(lit_obj, 'id', None)
                        }
                    )
                except Exception as notif_err:
                    logger.warning("Échec de diffusion de la notification d'affectation de lit: %s", str(notif_err))

                read_serializer = HospitalisationReadSerializer(hospitalisation)
                resp_data = read_serializer.data
                resp_data['id_admission'] = hospitalisation.id
                resp_data['id_patient'] = hospitalisation.patient_id
                resp_data['message'] = "Admission hospitalière enregistrée avec succès."
                if patient_account_info:
                    resp_data['nouveau_patient_cree'] = is_nouveau
                    resp_data['patient_identifiants'] = patient_account_info

                return Response(resp_data, status=status.HTTP_201_CREATED)
            except (ValueError, ValidationError, IntegrityError) as e:
                return Response({"error": "Données d'admission invalides.", "detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                logger.exception("Erreur inattendue lors de l'admission en hospitalisation: %s", str(e))
                return Response({"error": f"Erreur interne lors de l'admission : {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Hospitalisation / Admissions"],
    summary="Lister les admissions hospitalières en cours",
    description="Retourne les admissions actuellement actives (statut=EN_COURS, actif=True) avec filtres de recherche.",
    parameters=[SEARCH_PARAM, *PAGINATION_PARAMS],
    responses={200: HospitalisationReadSerializer(many=True)},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def hospitalisation_en_cours_view(request):
    user_role = getattr(request.user, "role", None)
    qs = hospitalisation_service.repository.get_all_hospitalisations(actif_only=True).filter(
        statut=Hospitalisation.StatutHospitalisation.EN_COURS
    )

    if user_role == "PATIENT":
        qs = qs.filter(patient__id_utilisateur=request.user)
    elif user_role == "MEDECIN":
        if request.query_params.get("mes_patients", "false").lower() == "true":
            qs = qs.filter(medecin__id_utilisateur=request.user)

    search_query = request.query_params.get("search")
    if search_query:
        qs = qs.filter(
            patient__id_utilisateur__nom__icontains=search_query
        ) | qs.filter(
            patient__id_utilisateur__prenom__icontains=search_query
        ) | qs.filter(
            motif__icontains=search_query
        )

    return paginate_response(qs, request, HospitalisationReadSerializer)


@extend_schema(
    tags=["Hospitalisation / Admissions"],
    summary="Détail, mise à jour partielle ou totale d'une admission",
    description="Accède aux détails complets d'une admission ou met à jour ses informations.",
    request=HospitalisationSerializer,
    responses={
        200: HospitalisationReadSerializer,
        400: ErrorResponseSerializer,
        403: ErrorResponseSerializer,
        404: ErrorResponseSerializer,
    },
)
@api_view(["GET", "PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def hospitalisation_detail_view(request, pk):
    hospitalisation = hospitalisation_service.repository.get_hospitalisation_by_id(pk)
    if not hospitalisation:
        return Response({"error": f"Admission #{pk} introuvable."}, status=status.HTTP_404_NOT_FOUND)

    deny_unless_owner_or_staff(request, hospitalisation)

    if request.method == "GET":
        serializer = HospitalisationReadSerializer(hospitalisation)
        return Response(serializer.data, status=status.HTTP_200_OK)

    if getattr(request.user, "role", None) not in ["MEDECIN", "INFIRMIER", "ADMINISTRATEUR"]:
        return Response({"error": "Action réservée au personnel soignant et administrateurs."}, status=status.HTTP_403_FORBIDDEN)

    # RÈGLE DE SÉCURITÉ : Un médecin ne peut pas modifier les admissions d'un confrère sans être administrateur
    if getattr(request.user, "role", None) == "MEDECIN":
        if hospitalisation.medecin and getattr(hospitalisation.medecin, "id_utilisateur", None) != request.user:
            return Response(
                {"error": "Accès refusé. Vous ne pouvez modifier que les admissions dont vous êtes le médecin responsable."},
                status=status.HTTP_403_FORBIDDEN
            )

    partial = (request.method == "PATCH")
    serializer = HospitalisationSerializer(hospitalisation, data=request.data, partial=partial)
    if serializer.is_valid():
        try:
            updated = hospitalisation_service.mettre_a_jour_hospitalisation(pk, **serializer.validated_data)
            return Response(HospitalisationReadSerializer(updated).data, status=status.HTTP_200_OK)
        except (ValueError, ValidationError, IntegrityError) as e:
            return Response({"error": "Données de modification invalides.", "detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception("Erreur inattendue lors de la mise à jour d'admission: %s", str(e))
            return Response({"error": "Erreur interne lors de la mise à jour."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Hospitalisation / Admissions"],
    summary="Clôturer une admission / hospitalisation (Sortie du patient)",
    description="Marque l'hospitalisation comme TERMINEE, enregistre la date de sortie et libère le lit.",
    request=HospitalisationSerializer,
    responses={
        200: HospitalisationReadSerializer,
        400: ErrorResponseSerializer,
        404: ErrorResponseSerializer,
    },
)
@api_view(["POST"])
@permission_classes([IsStaffOrAdmin])
def hospitalisation_cloturer_view(request, pk):
    observation = request.data.get("observation") or request.data.get("observation_finale") or request.data.get("motif_sortie")
    try:
        hospitalisation = hospitalisation_service.cloturer_hospitalisation(pk, observation_finale=observation)
        if not hospitalisation:
            return Response({"error": f"Admission #{pk} introuvable."}, status=status.HTTP_404_NOT_FOUND)
        return Response(HospitalisationReadSerializer(hospitalisation).data, status=status.HTTP_200_OK)
    except (ValueError, ValidationError) as e:
        return Response({"error": "Impossible de clôturer l'hospitalisation.", "detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.exception("Erreur inattendue lors de la clôture d'hospitalisation: %s", str(e))
        return Response({"error": "Erreur interne lors de la clôture."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    tags=["Hospitalisation / Admissions"],
    summary="Supprimer ou archiver une hospitalisation",
    description="Par défaut désactive l'hospitalisation (actif=False, statut=ANNULEE). Si hard=true, la supprime définitivement de la base.",
    parameters=[HARD_DELETE_PARAM],
    responses={
        200: MessageResponseSerializer,
        404: ErrorResponseSerializer,
    },
)
@api_view(["DELETE"])
@permission_classes([IsMedecinOuAdmin])
def hospitalisation_delete_view(request, pk):
    hard = request.query_params.get("hard", "false").lower() == "true"
    success = hospitalisation_service.supprimer_hospitalisation(pk, hard=hard)
    if not success:
        return Response({"error": f"Admission #{pk} introuvable."}, status=status.HTTP_404_NOT_FOUND)

    msg = f"Admission #{pk} supprimée définitivement." if hard else f"Admission #{pk} archivée (annulée)."
    return Response({"message": msg}, status=status.HTTP_200_OK)
