import os
import sys
import io
import django
from datetime import date, timedelta

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.core.files.uploadedfile import SimpleUploadedFile
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

from patients.models import Patient
from medecin.models import Medecin
from consultation.models import Consultation
from documents_medicaux.models import DocumentMedical
from documents_medicaux.services import DocumentMedicalService


def build_sample_pdf(title: str, subtitle: str, patient_name: str, doctor_name: str, body_sections: list) -> bytes:
    """
    Génère un flux binaire PDF médical professionnel et structuré avec ReportLab.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    styles = getSampleStyleSheet()

    header_title_style = ParagraphStyle(
        'DocHeaderTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=18,
        textColor=colors.HexColor('#0f766e')
    )
    hospital_style = ParagraphStyle(
        'HospitalName',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=14,
        textColor=colors.HexColor('#1e293b')
    )
    meta_style = ParagraphStyle(
        'MetaText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#475569')
    )
    section_h_style = ParagraphStyle(
        'SectionH',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#0f766e')
    )
    body_style = ParagraphStyle(
        'BodyTxt',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor('#334155')
    )

    story = []

    # En-tête officiel
    header_data = [
        [
            Paragraph("<b>CENTRE HOSPITALIER UNIVERSITAIRE</b><br/>Santé Numérique — Pôle d'Excellence", hospital_style),
            Paragraph(f"<b>Document Médical Certifié</b><br/>{title}", header_title_style)
        ]
    ]
    t_header = Table(header_data, colWidths=[240, 280])
    t_header.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
    ]))
    story.append(t_header)
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0f766e'), spaceAfter=12))

    # Bloc informations administratives
    info_data = [
        [
            Paragraph(f"<b>Patient :</b> {patient_name}", meta_style),
            Paragraph(f"<b>Praticien :</b> {doctor_name}", meta_style)
        ],
        [
            Paragraph(f"<b>Examen :</b> {subtitle}", meta_style),
            Paragraph(f"<b>Date de réalisation :</b> {date.today().strftime('%d/%m/%Y')}", meta_style)
        ]
    ]
    t_info = Table(info_data, colWidths=[260, 260])
    t_info.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_info)
    story.append(Spacer(1, 14))

    # Corps du rapport
    for sec_title, sec_content in body_sections:
        story.append(Paragraph(sec_title, section_h_style))
        story.append(Spacer(1, 4))
        if isinstance(sec_content, list):
            # Table de résultats
            t_results = Table(sec_content, colWidths=[180, 110, 110, 120])
            t_results.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f766e')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8.5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f1f5f9')])
            ]))
            story.append(t_results)
        else:
            story.append(Paragraph(str(sec_content), body_style))
        story.append(Spacer(1, 10))

    # Signature et sécurité
    story.append(Spacer(1, 14))
    story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor('#cbd5e1'), spaceAfter=8))
    footer_text = Paragraph(
        "<i>Document médical confidentiel archivé dans la GED sécurisée de Santé Numérique. "
        "Chiffrement matériel AES-256 et empreinte cryptographique SHA-256 certifiée conforme HDS.</i>",
        meta_style
    )
    story.append(footer_text)

    doc.build(story)
    return buffer.getvalue()


def run_seed_documents_medicaux():
    print("\n=========================================================")
    print("=== SEEDING DES DOCUMENTS MÉDICAUX (GED AES-256) ===")
    print("=========================================================")

    ged_service = DocumentMedicalService()

    patients = list(Patient.objects.select_related('id_utilisateur').all())
    medecins = list(Medecin.objects.select_related('id_utilisateur').all())

    if not patients:
        print(" [X] Aucun patient trouvé. Exécutez d'abord seed_demo_accounts.py.")
        return

    medecin_referent = medecins[0] if medecins else None
    medecin_nom = f"Dr. {medecin_referent.id_utilisateur.prenom} {medecin_referent.id_utilisateur.nom}" if medecin_referent else "Dr. Praticien Hospitalier"

    DOCS_CATALOG = [
        {
            "titre": "Bilan Sanguin & Biologique Complet (NFS, Ionogramme)",
            "categorie": DocumentMedical.Categorie.ANALYSE_SANG,
            "filename": "bilan_sanguin_complet.pdf",
            "observation": "Bilan biologique satisfaisant. Hémogramme stable, fonction rénale normale. Pas d'anomalie électrolytique.",
            "sections": [
                ("1. Données de l'analyse hématologique", [
                    ["Paramètre", "Résultat", "Unité", "Valeurs de référence"],
                    ["Leucocytes (Globules blancs)", "6.8", "10^9/L", "4.0 - 10.0"],
                    ["Hématies (Globules rouges)", "4.9", "10^12/L", "4.5 - 5.5"],
                    ["Hémoglobine", "14.2", "g/dL", "13.0 - 17.0"],
                    ["Hématocrite", "42.5", "%", "40.0 - 52.0"],
                    ["Plaquettes", "245", "10^9/L", "150 - 400"],
                    ["Glycémie à jeun", "0.94", "g/L", "0.70 - 1.10"],
                    ["Créatinine plasmatique", "82", "µmol/L", "60 - 110"],
                    ["Protéine C-Réactive (CRP)", "2.1", "mg/L", "< 5.0"]
                ]),
                ("2. Conclusion du biologiste médical", "Absence de syndrome inflammatoire biologique. Lignées cellulaires équilibrées. Profil rénal normal.")
            ]
        },
        {
            "titre": "Compte-Rendu de Scanner Thoracique et Abdominal (TDM)",
            "categorie": DocumentMedical.Categorie.SCANNER,
            "filename": "scanner_thoraco_abdominal.pdf",
            "observation": "Examen tomodensitométrique réalisé avec injection de produit de contraste iodé au temps portal.",
            "sections": [
                ("1. Protocole technique", "Acquisition hélicoïdale volumique millimétrique thoraco-abdomino-pelvienne après injection intraveineuse de 90 mL de produit de contraste."),
                ("2. Étage thoracique", "Parenchyme pulmonaire sain, sans foyer de condensation alvéolaire ni micronodule suspect. Absence d'épanchement pleural ou péricardique. Trachée et bronches souches libres."),
                ("3. Étage abdomino-pelvien", "Foie de taille et morphologie normales, densité homogène sans lésion focale suspecte. Vésicule biliaire alithiasique. Pancréas, rate et reins sans anomalie notable."),
                ("4. Conclusion", "Examen scannographique dans les limites de la normale. Absence d'anomalie morphologique évolutive.")
            ]
        },
        {
            "titre": "Radiographie Pulmonaire de Contrôle (Face & Profil)",
            "categorie": DocumentMedical.Categorie.RADIO,
            "filename": "radio_pulmonaire_face_profil.pdf",
            "observation": "Radiographie thoracique standard réalisée en inspiration profonde en incidence postéro-antérieure.",
            "sections": [
                ("1. Indication clinique", "Contrôle post-infection respiratoire aiguë. Évaluation de la clairance parenchymateuse."),
                ("2. Résultats radiologiques", "Index cardio-thoracique normal (< 0.50). Silhouettes médiastinales et hiles pulmonaires harmonieux. Absence de syndrome alvéolaire ou interstitiel décelable. Culs-de-sac pleuraux libres."),
                ("3. Conclusion", "Restitutio ad integrum post-antibiothérapie. Radiographie thoracique sans particularité.")
            ]
        },
        {
            "titre": "Échographie Cardiaque Trans-Thoracique (Doppler)",
            "categorie": DocumentMedical.Categorie.ECHOGRAPHIE,
            "filename": "echographie_cardiaque_doppler.pdf",
            "observation": "Échocardiographie bidimensionnelle et Doppler couleur pulsé et continu.",
            "sections": [
                ("1. Paramètres cavitaires et fonction systolique", [
                    ["Paramètre", "Mesure", "Unité", "Norme"],
                    ["Diamètre télé-diastolique VG", "48", "mm", "< 55"],
                    ["Fraction d'éjection (Simpson)", "65", "%", "> 55%"],
                    ["Épaisseur septum interventriculaire", "10", "mm", "< 11"],
                    ["Diamètre Oreillette Gauche", "34", "mm", "< 40"],
                    ["Vitesse max aortique", "1.3", "m/s", "< 2.0"]
                ]),
                ("2. Analyse valvulaire", "Valves mitrale et aortique fines et mobiles. Absence d'insuffisance ou de sténose hémodynamiquement significative. Absence d'épanchement péricardique."),
                ("3. Conclusion cardiologique", "Bonne fonction systolique globale du VG. Pas de cardiopathie hypertensive ou valvulaire décelable.")
            ]
        },
        {
            "titre": "IRM Cérébrale et Angio-IRM Intra-Crânienne",
            "categorie": DocumentMedical.Categorie.IRM,
            "filename": "irm_cerebrale_sequences.pdf",
            "observation": "Examen IRM réalisé à 1.5 Tesla selon les séquences T1, T2, FLAIR, Diffusion et Angio-3D TOF.",
            "sections": [
                ("1. Indication", "Bilan de céphalées persistantes inhabituelles."),
                ("2. Parenchyme cérébral", "Absence de lésion d'allure ischémique aiguë sur la séquence de diffusion. Absence d'effet de masse ou d'anomalie du signal cérébral sur les séquences T2/FLAIR. Système ventriculaire médian symétrique."),
                ("3. Réseau artériel", "L'angio-IRM du polygone de Willis ne montre aucun anévrisme décelable ni anomalie morphologique artérielle."),
                ("4. Conclusion", "IRM cérébrale et angio-IRM strictement normales.")
            ]
        },
        {
            "titre": "Compte-Rendu Opératoire : Appendicectomie sous Coelioscopie",
            "categorie": DocumentMedical.Categorie.COMPTE_RENDU,
            "filename": "compte_rendu_operatoire.pdf",
            "observation": "Intervention chirurgicale réalisée sous anesthésie générale. Suites opératoires immédiates simples.",
            "sections": [
                ("1. Diagnostic pré-opératoire", "Appendicite aiguë catarrhale confirmée par échographie abdominale."),
                ("2. Description de l'intervention", "Introduction de l'optique ombilicale après insufflation. Découverte d'un appendice latéro-caecal congestif et inflammatoire. Dissection du méso-appendice, agrafage et extraction dans un endobag. Lavage abondant du cul-de-sac de Douglas."),
                ("3. Suites et prescriptions", "Reprise alimentaire progressive au soir de l'intervention. Antalgiques simples pallier 1. Sortie autorisée à J+1 avec soins de pansement à domicile.")
            ]
        },
        {
            "titre": "Certificat Médical d'Aptitude Physique & Sportive",
            "categorie": DocumentMedical.Categorie.CERTIFICAT,
            "filename": "certificat_aptitude_sport.pdf",
            "observation": "Examen clinique complet en vue de la pratique sportive en compétition.",
            "sections": [
                ("1. Déclaration clinique", "Je soussigné certifie avoir examiné ce jour le patient susmentionné. L'interrogatoire et l'examen clinique complet (cardiovasculaire, pulmonaire, ostéo-articulaire) ne révèlent aucune contre-indication médicale apparente à la pratique sportive."),
                ("2. Électrocardiogramme de repos", "Rythme sinusal régulier à 64 bpm. Pas d'anomalie de repolarisation ni d'allongement de l'intervalle QTc.")
            ]
        },
        {
            "titre": "Bilan Lipidique & Facteurs de Risque Cardiovasculaires",
            "categorie": DocumentMedical.Categorie.ANALYSE_SANG,
            "filename": "bilan_lipidique_prevention.pdf",
            "observation": "Exploration d'une anomalie lipidique (EAL) réalisée après 12 heures de jeûne.",
            "sections": [
                ("1. Dosage lipidique", [
                    ["Fraction", "Taux mesuré", "Unité", "Valeur cible"],
                    ["Cholestérol Total", "1.85", "g/L", "< 2.00"],
                    ["HDL Cholestérol", "0.58", "g/L", "> 0.40"],
                    ["LDL Cholestérol calculé", "1.05", "g/L", "< 1.30"],
                    ["Triglycérides", "1.10", "g/L", "< 1.50"]
                ]),
                ("2. Recommandations", "Profil lipidique équilibré. Poursuite des règles hygiéno-diététiques recommandées.")
            ]
        }
    ]

    total_uploaded = 0
    today = date.today()

    for idx, doc_item in enumerate(DOCS_CATALOG):
        patient_target = patients[idx % len(patients)]
        patient_nom = f"{patient_target.id_utilisateur.prenom} {patient_target.id_utilisateur.nom}" if patient_target.id_utilisateur else f"Patient #{patient_target.id_patient}"
        med_target = medecins[idx % len(medecins)] if medecins else None
        med_nom = f"Dr. {med_target.id_utilisateur.prenom} {med_target.id_utilisateur.nom}" if med_target and med_target.id_utilisateur else medecin_nom

        # Génération du binaire PDF réel
        pdf_bytes = build_sample_pdf(
            title=doc_item["titre"],
            subtitle=doc_item.get("observation", "Examen médical"),
            patient_name=patient_nom,
            doctor_name=med_nom,
            body_sections=doc_item["sections"]
        )

        uploaded_file = SimpleUploadedFile(
            name=doc_item["filename"],
            content=pdf_bytes,
            content_type="application/pdf"
        )

        doc_date = today - timedelta(days=(idx * 3) + 1)

        # Upload avec chiffrement automatique AES-256 Fernet + SHA-256
        created_doc = ged_service.upload_document(
            patient=patient_target,
            medecin=med_target,
            titre=doc_item["titre"],
            uploaded_file=uploaded_file,
            categorie=doc_item["categorie"],
            date_document=doc_date,
            observation=doc_item["observation"]
        )

        total_uploaded += 1
        print(f" [{total_uploaded}/{len(DOCS_CATALOG)}] GED : '{created_doc.titre}' "
              f"| Categorie: {created_doc.get_categorie_display()} "
              f"| Patient: {patient_nom} "
              f"| SHA-256: {created_doc.checksum_sha256[:12]}... (Chiffré AES-256)")

    print(f"\n[OK] {total_uploaded} documents médicaux chiffrés ont été injectés dans la GED avec succès !")
    print(f" Total Documents Médicaux en base : {DocumentMedical.objects.count()}")
    print("=========================================================\n")


if __name__ == "__main__":
    run_seed_documents_medicaux()
