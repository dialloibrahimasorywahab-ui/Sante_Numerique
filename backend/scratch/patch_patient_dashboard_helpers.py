path_ts = r"c:\Users\Ibrahima Sory\Desktop\Sante\Sante_Numerique\frontend\src\app\features\patient\pages\dashboard\patient-dashboard.component.ts"
with open(path_ts, "r", encoding="utf-8") as f:
    ts = f.read()

helpers = """
  getHospRoomBed(hosp: any): string {
    if (!hosp) return '—';
    const ch = hosp.chambreNumero || hosp.chambre_numero || hosp.lit_details?.chambre_detail?.numero_chambre || hosp.litDetails?.chambre_detail?.numero_chambre || '—';
    const lit = hosp.litNumero || hosp.lit_numero || hosp.lit_details?.numero_lit || hosp.litDetails?.numero_lit || '—';
    return `Chambre ${ch} — Lit ${lit}`;
  }

  getHospDoctor(hosp: any): string {
    if (!hosp) return 'Dr. Médecin Référent';
    const m = hosp.medecinDetails || hosp.medecin_details || hosp.medecinDetail || hosp.medecin_detail;
    if (m && (m.prenom || m.nom)) {
      return `Dr. ${m.prenom || ''} ${m.nom || ''}`.trim();
    }
    const prenom = hosp.medecin_prenom || hosp.medecinPrenom || '';
    const nom = hosp.medecin_nom || hosp.medecinNom || '';
    if (prenom || nom) {
      return `Dr. ${prenom} ${nom}`.trim();
    }
    return 'Dr. Médecin Référent';
  }

  getConsultationDoctor(cons: any): string {
    if (!cons) return 'Dr. Praticien';
    const m = cons.medecinDetails || cons.medecin_details || cons.medecinDetail || cons.medecin_detail;
    if (m && (m.prenom || m.nom)) {
      return `Dr. ${m.prenom || ''} ${m.nom || ''}`.trim();
    }
    const prenom = cons.medecin_prenom || cons.medecinPrenom || '';
    const nom = cons.medecin_nom || cons.medecinNom || '';
    if (prenom || nom) {
      return `Dr. ${prenom} ${nom}`.trim();
    }
    return 'Dr. Praticien Hospitalier';
  }
"""

if "getHospRoomBed" not in ts:
    last_brace = ts.rfind("}")
    ts = ts[:last_brace] + helpers + "\n}\n"
    with open(path_ts, "w", encoding="utf-8") as f:
        f.write(ts)
    print("Added helpers to patient-dashboard.component.ts")

# Now update patient-dashboard.component.html
path_html = r"c:\Users\Ibrahima Sory\Desktop\Sante\Sante_Numerique\frontend\src\app\features\patient\pages\dashboard\patient-dashboard.component.html"
with open(path_html, "r", encoding="utf-8") as f:
    html = f.read()

# Replace hosp lit/chambre
old_hosp_bed_line = '<strong class="hosp-lit">Chambre {{ hosp.chambreNumero || hosp.chambre_numero || hosp.lit_details?.chambre_detail?.numero_chambre || \'—\' }} — Lit {{ hosp.litNumero || hosp.lit_numero || hosp.lit_details?.numero_lit || \'—\' }}</strong>'
new_hosp_bed_line = '<strong class="hosp-lit">{{ getHospRoomBed(hosp) }}</strong>'
html = html.replace(old_hosp_bed_line, new_hosp_bed_line)

# Replace hosp doctor line
old_hosp_doc_line = 'Admis le <strong>{{ formatDate(hosp.date_entree) }}</strong>. Médecin référent : <strong>Dr. {{ hosp.medecinDetails?.prenom || hosp.medecin_details?.prenom || hosp.medecinPrenom || hosp.medecin_prenom || \'\' }} {{ hosp.medecinDetails?.nom || hosp.medecin_details?.nom || hosp.medecinNom || hosp.medecin_nom || \'Médecin Référent\' }}</strong>.'
new_hosp_doc_line = 'Admis le <strong>{{ formatDate(hosp.date_entree) }}</strong>. Médecin référent : <strong>{{ getHospDoctor(hosp) }}</strong>.'
html = html.replace(old_hosp_doc_line, new_hosp_doc_line)

# Replace cons doctor line
old_cons_doc_line = """              <h4 class="cons-doctor">
                Dr. {{ cons.medecinDetails?.prenom || cons.medecin_details?.prenom || cons.medecinPrenom || cons.medecin_prenom || '' }} {{ cons.medecinDetails?.nom || cons.medecin_details?.nom || cons.medecinNom || cons.medecin_nom || 'Praticien' }}
              </h4>"""
new_cons_doc_line = """              <h4 class="cons-doctor">
                {{ getConsultationDoctor(cons) }}
              </h4>"""
html = html.replace(old_cons_doc_line, new_cons_doc_line)

with open(path_html, "w", encoding="utf-8") as f:
    f.write(html)
print("Updated patient-dashboard.component.html with clean helper calls")

