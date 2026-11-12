path_ts = r"c:\Users\Ibrahima Sory\Desktop\Sante\Sante_Numerique\frontend\src\app\features\patient\pages\dashboard\patient-dashboard.component.ts"
with open(path_ts, "r", encoding="utf-8") as f:
    ts = f.read()

old_get_doc = """  getDoctorFullName(rdv: RendezVousDto): string {
    if (rdv.medecin_nom || rdv.medecin_prenom) {
      return `Dr. ${rdv.medecin_prenom || ''} ${rdv.medecin_nom || ''}`.trim();
    }
    if (rdv.medecin_detail) {
      return `Dr. ${rdv.medecin_detail.prenom || ''} ${rdv.medecin_detail.nom || ''}`.trim();
    }
    return `Médecin #${rdv.id_medecin || ''}`.trim();
  }"""

new_get_doc = """  getDoctorFullName(rdv: any): string {
    const m = rdv.medecinDetails || rdv.medecin_details || rdv.medecinDetail || rdv.medecin_detail;
    if (m && (m.prenom || m.nom)) {
      return `Dr. ${m.prenom || ''} ${m.nom || ''}`.trim();
    }
    const prenom = rdv.medecin_prenom || rdv.medecinPrenom || '';
    const nom = rdv.medecin_nom || rdv.medecinNom || '';
    if (prenom || nom) {
      return `Dr. ${prenom} ${nom}`.trim();
    }
    return 'Dr. Praticien Hospitalier';
  }"""

if old_get_doc in ts:
    ts = ts.replace(old_get_doc, new_get_doc)
    with open(path_ts, "w", encoding="utf-8") as f:
        f.write(ts)
    print("Updated getDoctorFullName in patient-dashboard.component.ts")

# Update patient-dashboard.component.html
path_html = r"c:\Users\Ibrahima Sory\Desktop\Sante\Sante_Numerique\frontend\src\app\features\patient\pages\dashboard\patient-dashboard.component.html"
with open(path_html, "r", encoding="utf-8") as f:
    html = f.read()

# Update hosp doctor
old_hosp_doc = "Dr. {{ hosp.medecin_details?.prenom }} {{ hosp.medecin_details?.nom }}"
new_hosp_doc = "Dr. {{ hosp.medecinDetails?.prenom || hosp.medecin_details?.prenom || hosp.medecinPrenom || hosp.medecin_prenom || '' }} {{ hosp.medecinDetails?.nom || hosp.medecin_details?.nom || hosp.medecinNom || hosp.medecin_nom || 'Médecin Référent' }}"
html = html.replace(old_hosp_doc, new_hosp_doc)

# Update hosp room/bed
old_hosp_bed = "Chambre {{ hosp.lit_details?.chambre_detail?.numero_chambre || '—' }} — Lit {{ hosp.lit_details?.numero_lit || '—' }}"
new_hosp_bed = "Chambre {{ hosp.chambreNumero || hosp.chambre_numero || hosp.lit_details?.chambre_detail?.numero_chambre || '—' }} — Lit {{ hosp.litNumero || hosp.lit_numero || hosp.lit_details?.numero_lit || '—' }}"
html = html.replace(old_hosp_bed, new_hosp_bed)

# Update cons doctor
old_cons_doc = "Dr. {{ cons.medecin_details?.prenom }} {{ cons.medecin_details?.nom }}"
new_cons_doc = "Dr. {{ cons.medecinDetails?.prenom || cons.medecin_details?.prenom || cons.medecinPrenom || cons.medecin_prenom || '' }} {{ cons.medecinDetails?.nom || cons.medecin_details?.nom || cons.medecinNom || cons.medecin_nom || 'Praticien' }}"
html = html.replace(old_cons_doc, new_cons_doc)

with open(path_html, "w", encoding="utf-8") as f:
    f.write(html)
print("Updated patient-dashboard.component.html")

