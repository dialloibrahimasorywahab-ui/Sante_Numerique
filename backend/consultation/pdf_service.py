import io
from datetime import datetime
import qrcode
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, HRFlowable
)
from .models import Consultation


def generate_consultation_pdf_bytes(consultation: Consultation) -> bytes:
    """
    Génère un compte-rendu officiel et certificat de consultation médicale en PDF,
    avec en-tête hospitalier, identification patient/praticien, synthèse clinique,
    observations, QR Code de contrôle d'authenticité et cachet du médecin.
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
    primary_color = colors.HexColor("#0284c7")  # Bleu médical CHU
    dark_color = colors.HexColor("#0f172a")     # Gris anthracite
    accent_color = colors.HexColor("#f0fdf4")   # Vert d'eau très clair
    border_color = colors.HexColor("#cbd5e1")   # Bordure ardoise claire

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=17,
        leading=21,
        textColor=primary_color,
        alignment=1
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=dark_color,
        alignment=1
    )
    section_title_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=primary_color,
        spaceAfter=4
    )
    label_style = ParagraphStyle(
        'LabelStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#334155")
    )
    val_style = ParagraphStyle(
        'ValStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#0f172a")
    )
    body_style = ParagraphStyle(
        'BodyContent',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=15,
        textColor=colors.HexColor("#1e293b")
    )
    legal_style = ParagraphStyle(
        'LegalStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#64748b"),
        alignment=1
    )

    story = []

    # 1. En-tête officiel
    header_data = [
    [
        Paragraph(
            "<b>RÉPUBLIQUE DE GUINÉE</b><br/>"
            "<i>Travail - Justice - Solidarité</i><br/>"
            "Ministère de la Santé et de l'Hygiène Publique",
            subtitle_style
        ),
        Paragraph(
            "<b>CENTRE HOSPITALIER UNIVERSITAIRE</b><br/>"
            "Santé_Numérique - Service des Consultations<br/>"
            "Conakry, République de Guinée | Tél : +224 627 35 03 03",
            subtitle_style
        )
    ]
]
    t_header = Table(header_data, colWidths=[260, 260])
    t_header.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_header)
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1.5, color=primary_color, spaceAfter=10))

    # 2. Titre et référence
    ref_certificat = f"CR-CONS-{consultation.id:06d}-{consultation.date_cons.strftime('%Y%m%d')}"
    story.append(Paragraph("CERTIFICAT MÉDICAL &amp; COMPTE-RENDU DE CONSULTATION", title_style))
    story.append(Spacer(1, 3))
    story.append(Paragraph(f"Réf. Acte: <b>{ref_certificat}</b> &nbsp;|&nbsp; Date de l'acte: <b>{consultation.date_cons.strftime('%d/%m/%Y à %H:%M')}</b>", subtitle_style))
    story.append(Spacer(1, 12))

    # 3. Informations Patient & Médecin
    patient = getattr(consultation, 'patient', None)
    patient_user = getattr(patient, 'id_utilisateur', None) if patient else None
    medecin = getattr(consultation, 'medecin', None)
    medecin_user = getattr(medecin, 'idUtilisateur', None) if medecin else None

    nom_medecin = f"Dr. {medecin_user.prenom} {medecin_user.nom}" if medecin_user else "Praticien Hospitalier"
    spec_medecin = getattr(medecin, 'specialite', 'Médecine Générale') or 'Médecine Générale'
    matricule_med = getattr(medecin, 'matricule', 'N/A') or 'N/A'

    nom_patient = f"{patient_user.prenom} {patient_user.nom}" if patient_user else f"Patient #{consultation.patient_id}"
    date_naiss = str(getattr(patient, 'date_naissance', 'N/A') or 'N/A')
    sexe_patient = getattr(patient, 'sexe', 'N/A') or 'N/A'
    groupe_sanguin = getattr(patient, 'groupe_sanguin', 'Non renseigné') or 'Non renseigné'
    allergies = getattr(patient, 'allergies', 'Aucune') or 'Aucune'

    bloc_medecin = [
        Paragraph("<b>PRATICIEN EXAMINATEUR</b>", section_title_style),
        Spacer(1, 2),
        Paragraph(f"<b>Nom:</b> {nom_medecin}", val_style),
        Paragraph(f"<b>Spécialité:</b> {spec_medecin}", val_style),
        Paragraph(f"<b>Matricule:</b> {matricule_med}", val_style),
    ]

    bloc_patient = [
        Paragraph("<b>PATIENT EXAMINÉ</b>", section_title_style),
        Spacer(1, 2),
        Paragraph(f"<b>Nom &amp; Prénom:</b> {nom_patient}", val_style),
        Paragraph(f"<b>Né(e) le:</b> {date_naiss} &nbsp;|&nbsp; <b>Sexe:</b> {sexe_patient}", val_style),
        Paragraph(f"<b>Groupe sanguin:</b> {groupe_sanguin}", val_style),
        Paragraph(f"<b>Terrain / Allergies:</b> {allergies}", val_style),
    ]

    t_ident = Table([[bloc_medecin, bloc_patient]], colWidths=[260, 260])
    t_ident.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BACKGROUND', (0, 0), (0, 0), colors.HexColor("#f8fafc")),
        ('BACKGROUND', (1, 0), (1, 0), colors.HexColor("#f8fafc")),
        ('BOX', (0, 0), (0, 0), 0.5, border_color),
        ('BOX', (1, 0), (1, 0), 0.5, border_color),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(t_ident)
    story.append(Spacer(1, 14))

    # 4. Corps Clinique (Symptômes, Diagnostic, Observations)
    story.append(Paragraph("1. MOTIF DE CONSULTATION &amp; SYMPTÔMES", section_title_style))
    symptomes_txt = consultation.symptomes.strip() if consultation.symptomes else "Aucun symptôme particulier mentionné lors de l'examen."
    p_symp = Table([[Paragraph(symptomes_txt, body_style)]], colWidths=[520])
    p_symp.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#ffffff")),
        ('BOX', (0, 0), (-1, -1), 0.5, border_color),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(p_symp)
    story.append(Spacer(1, 10))

    story.append(Paragraph("2. CONCLUSION CLINIQUE &amp; DIAGNOSTIC", section_title_style))
    diagnostic_txt = consultation.diagnostic.strip() if consultation.diagnostic else "Examen clinique normal. Aucun diagnostic pathologique posé."
    p_diag = Table([[Paragraph(diagnostic_txt, body_style)]], colWidths=[520])
    p_diag.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#eff6ff")),  # Légère teinte bleue
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#93c5fd")),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(p_diag)
    story.append(Spacer(1, 10))

    story.append(Paragraph("3. RECOMMANDATIONS &amp; OBSERVATIONS MÉDICALES", section_title_style))
    observations_txt = consultation.observations.strip() if consultation.observations else "Repos préconisé et respect scrupuleux des posologies prescrites."
    p_obs = Table([[Paragraph(observations_txt, body_style)]], colWidths=[520])
    p_obs.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#ffffff")),
        ('BOX', (0, 0), (-1, -1), 0.5, border_color),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(p_obs)
    story.append(Spacer(1, 16))

    # 5. QR Code de certification & Bloc Signature
    qr_data = (
        f"CERTIFICAT-MED:{ref_certificat}|DATE:{consultation.date_cons.isoformat()}|"
        f"PATIENT:{nom_patient}|MEDECIN:{nom_medecin}|ID_CONS:{consultation.id}"
    )
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=3,
        border=1,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")

    qr_buffer = io.BytesIO()
    qr_img.save(qr_buffer, format='PNG')
    qr_buffer.seek(0)
    qr_reportlab = Image(qr_buffer, width=70, height=70)

    bloc_qr = [
        qr_reportlab,
        Spacer(1, 3),
        Paragraph("<b>Contrôle d'authenticité</b><br/>Scannez pour certifier l'acte", legal_style)
    ]

    bloc_signature = [
        Paragraph(f"Fait à Dakar, le {datetime.now().strftime('%d/%m/%Y')}", val_style),
        Spacer(1, 4),
        Paragraph("<b>Signature et Cachet du Médecin Consultant</b>", label_style),
        Spacer(1, 24),
        Paragraph(f"<b>{nom_medecin}</b><br/>{spec_medecin}", val_style),
        Paragraph("<i>Certifié conforme par signature électronique</i>", legal_style)
    ]

    t_footer = Table([[bloc_qr, bloc_signature]], colWidths=[160, 360])
    t_footer.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (0, 0), (0, 0), 'CENTER'),
        ('LEFTPADDING', (1, 0), (1, 0), 20),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))

    closing_elements = KeepTogether([
        HRFlowable(width="100%", thickness=0.8, color=border_color, spaceAfter=8),
        t_footer,
        Spacer(1, 10),
        Paragraph(
            "Ce document médical officiel est strictement confidentiel et protégé par le secret médical "
            "(Art. 378 du Code Pénal). Toute altération ou falsification expose à des poursuites judiciaires.",
            legal_style
        )
    ])
    story.append(closing_elements)

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
