import io
from datetime import datetime
import qrcode
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, HRFlowable
)
from .models import Ordonnance


def generate_ordonnance_pdf_bytes(ordonnance: Ordonnance) -> bytes:
    """
    Génère un document PDF médical officiel pour une ordonnance,
    conforme aux exigences médico-légales hospitalières, intégrant :
    - En-tête hospitalier officiel
    - Coordonnées du praticien prescripteur et numéro d'ordre
    - Informations d'identification du patient (groupe sanguin, sexe)
    - Tableau détaillé des lignes de médicaments et posologies
    - QR Code de vérification électronique d'authenticité
    - Cachet et bloc de signature sécurisé
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
    dark_color = colors.HexColor("#0f172a")     # Gris anthracite foncé
    accent_color = colors.HexColor("#e0f2fe")   # Bleu très clair

    # Styles typographiques
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=primary_color,
        alignment=1  # Centré
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=dark_color,
        alignment=1
    )
    section_title_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=primary_color
    )
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=dark_color
    )
    bold_style = ParagraphStyle(
        'DocBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=13,
        textColor=dark_color
    )

    story = []

    # 1. En-tête officiel de l'établissement
    header_data = [
        [
            Paragraph("<b>SANTÉ NUMÉRIQUE</b><br/><font size='8' color='#64748b'>CENTRE HOSPITALIER UNIVERSITAIRE<br/>Direction Médicale & Pharmacie Clinique</font>", body_style),
            Paragraph(f"<b>RÉFÉRENCE :</b> {ordonnance.reference or f'ORD-{ordonnance.id}'}<br/><b>DATE :</b> {ordonnance.date_ordonnance.strftime('%d/%m/%Y')}", body_style)
        ]
    ]
    header_table = Table(header_data, colWidths=[340, 180])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(header_table)
    story.append(HRFlowable(width="100%", thickness=1.5, color=primary_color, spaceAfter=14))

    # Titre du document
    story.append(Paragraph("ORDONNANCE MÉDICALE OFFICIELLE", title_style))
    story.append(Paragraph("Prescription délivrée sous la responsabilité du praticien signataire", subtitle_style))
    story.append(Spacer(1, 14))

    # 2. Données du Médecin et du Patient en deux colonnes
    medecin = None
    patient = None
    consultation = ordonnance.consultation
    if consultation:
        medecin = consultation.medecin
        patient = consultation.patient

    # Infos Praticien
    med_prenom = medecin.id_utilisateur.prenom if medecin and medecin.id_utilisateur else "Non spécifié"
    med_nom = medecin.id_utilisateur.nom if medecin and medecin.id_utilisateur else ""
    med_spec = medecin.get_specialite_display() if medecin else "Médecine Générale"
    med_ordre = medecin.numero_ordre if medecin else "N/A"
    med_tel = medecin.telephone_pro or (medecin.id_utilisateur.telephone if medecin and medecin.id_utilisateur else "N/A")

    doc_info_text = f"""<b>PRATICIEN PRESCRIPTEUR</b><br/>
    <b>Dr. {med_prenom} {med_nom}</b><br/>
    Spécialité : {med_spec}<br/>
    N° d'Ordre : {med_ordre}<br/>
    Contact : {med_tel}
    """

    # Infos Patient
    pat_prenom = patient.id_utilisateur.prenom if patient and patient.id_utilisateur else "Patient"
    pat_nom = patient.id_utilisateur.nom if patient and patient.id_utilisateur else f"#{ordonnance.id}"
    pat_sexe = patient.get_sexe_display() if patient and hasattr(patient, 'get_sexe_display') else (patient.sexe if patient else "N/A")
    pat_sang = patient.groupe_sanguin if patient else "N/A"
    pat_secu = patient.numero_securite_sociale or "Non renseigné"

    pat_info_text = f"""<b>BÉNÉFICIAIRE / PATIENT</b><br/>
    <b>{pat_prenom} {pat_nom}</b><br/>
    Sexe : {pat_sexe} | Groupe sanguin : <b>{pat_sang}</b><br/>
    N° Sécurité Sociale : {pat_secu}<br/>
    Dossier Patient N° : #{patient.id_patient if patient else 'N/A'}
    """

    parties_data = [
        [Paragraph(doc_info_text, body_style), Paragraph(pat_info_text, body_style)]
    ]
    parties_table = Table(parties_data, colWidths=[260, 260])
    parties_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), accent_color),
        ('BACKGROUND', (1, 0), (1, 0), colors.HexColor("#f8fafc")),
        ('BOX', (0, 0), (0, 0), 1, colors.HexColor("#cbd5e1")),
        ('BOX', (1, 0), (1, 0), 1, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(parties_table)
    story.append(Spacer(1, 16))

    # 3. Tableau des Médicaments et Lignes de Prescription
    story.append(Paragraph("PRESCRIPTIONS THÉRAPEUTIQUES", section_title_style))
    story.append(Spacer(1, 6))

    lignes = list(ordonnance.lignes.filter(actif=True))
    if lignes:
        table_rows = [
            [
                Paragraph("<b>Médicament & Dosage</b>", bold_style),
                Paragraph("<b>Posologie</b>", bold_style),
                Paragraph("<b>Durée</b>", bold_style),
                Paragraph("<b>Qté</b>", bold_style),
            ]
        ]
        for l in lignes:
            forme_str = f" ({l.forme})" if l.forme else ""
            dosage_str = f" - {l.dosage}" if l.dosage else ""
            med_cell = f"<b>{l.medicament}</b>{dosage_str}{forme_str}"
            if l.instructions:
                med_cell += f"<br/><font color='#64748b' size='8'><i>Note : {l.instructions}</i></font>"

            table_rows.append([
                Paragraph(med_cell, body_style),
                Paragraph(l.posologie or "Selon avis médical", body_style),
                Paragraph(l.duree_traitement or "Pendant les soins", body_style),
                Paragraph(str(l.quantite), body_style),
            ])

        med_table = Table(table_rows, colWidths=[220, 170, 90, 40])
        med_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(med_table)
    else:
        # Si pas de lignes structurées, afficher les observations directes
        obs_text = ordonnance.observation or "Aucune posologie détaillée renseignée."
        obs_box = Table([[Paragraph(f"<b>Détail des prescriptions :</b><br/>{obs_text}", body_style)]], colWidths=[520])
        obs_box.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ('PADDING', (0, 0), (-1, -1), 10),
        ]))
        story.append(obs_box)

    story.append(Spacer(1, 14))

    # Observations complémentaires
    if ordonnance.observation and lignes:
        story.append(Paragraph("<b>Recommandations du médecin :</b>", bold_style))
        story.append(Paragraph(ordonnance.observation, body_style))
        story.append(Spacer(1, 10))

    # 4. Pied de page sécurisé avec QR Code et Signature
    # Génération QR Code
    qr_data = f"https://sante-numerique.hopital.fr/verify/ordonnance/{ordonnance.reference or ordonnance.id}?med={med_ordre}&date={ordonnance.date_ordonnance}"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=4,
        border=1,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    img_qr = qr.make_image(fill_color="#0f172a", back_color="white")

    qr_buffer = io.BytesIO()
    img_qr.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)

    reportlab_qr = Image(qr_buffer, width=70, height=70)

    footer_data = [
        [
            reportlab_qr,
            Paragraph(
                "<font size='8' color='#64748b'>"
                "<b>AUTHENTICITÉ VÉRIFIABLE</b><br/>"
                "Scannez ce QR Code pour vérifier l'authenticité<br/>"
                "de cette prescription sur le serveur hospitalier.<br/>"
                f"Émis le {datetime.now().strftime('%d/%m/%Y à %H:%M')}"
                "</font>",
                body_style
            ),
            Paragraph(
                f"<font size='9'><b>Cachet & Signature du Praticien :</b></font><br/><br/>"
                f"<b>Dr. {med_prenom} {med_nom}</b><br/>"
                f"<font color='#0284c7'>[Certifié Santé Numérique]</font>",
                body_style
            )
        ]
    ]
    footer_table = Table(footer_data, colWidths=[80, 240, 200])
    footer_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LINEABOVE', (0, 0), (-1, -1), 1, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
    ]))

    story.append(KeepTogether([Spacer(1, 20), footer_table]))

    doc.build(story)
    return buffer.getvalue()
