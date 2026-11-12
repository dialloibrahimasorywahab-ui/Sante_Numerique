import re

path_html = r"c:\Users\Ibrahima Sory\Desktop\Sante\Sante_Numerique\frontend\src\app\features\admin\pages\medical\admin-medical.component.html"
with open(path_html, "r", encoding="utf-8") as f:
    content = f.read()

svg_bed = """<svg class="w-4 h-4 text-teal-600 inline" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M3 14h18m-9-4v8m-9 2h18a1 1 0 001-1V5a1 1 0 00-1-1H3a1 1 0 00-1 1v14a1 1 0 001 1z"/></svg>"""
content = content.replace("🛏️", svg_bed)

# Replace patient display in RDV
old_rdv_pat = "{{ rdv.patient_details?.prenom || rdv.patient_detail?.prenom }} {{ rdv.patient_details?.nom || rdv.patient_detail?.nom || ('Patient #' + (rdv.patient_id || rdv.patient)) }}"
new_rdv_pat = "{{ rdv.patientDetails?.prenom || rdv.patient_details?.prenom || rdv.patient_detail?.prenom || rdv.patientPrenom || rdv.patient_prenom || '' }} {{ rdv.patientDetails?.nom || rdv.patient_details?.nom || rdv.patient_detail?.nom || rdv.patientNom || rdv.patient_nom || ('Patient #' + (rdv.patient_id || rdv.patient)) }}"
content = content.replace(old_rdv_pat, new_rdv_pat)

# Replace doctor display in RDV
old_rdv_doc = "Dr. {{ rdv.medecin_details?.prenom || rdv.medecin_detail?.prenom }} {{ rdv.medecin_details?.nom || rdv.medecin_detail?.nom || ('Médecin #' + (rdv.medecin_id || rdv.medecin)) }}"
new_rdv_doc = "Dr. {{ rdv.medecinDetails?.prenom || rdv.medecin_details?.prenom || rdv.medecin_detail?.prenom || rdv.medecinPrenom || rdv.medecin_prenom || '' }} {{ rdv.medecinDetails?.nom || rdv.medecin_details?.nom || rdv.medecin_detail?.nom || rdv.medecinNom || rdv.medecin_nom || ('Médecin #' + (rdv.medecin_id || rdv.medecin)) }}"
content = content.replace(old_rdv_doc, new_rdv_doc)

# Replace patient display in consultations
old_c_pat = "{{ c.patient_details?.prenom || c.patient?.prenom }} {{ c.patient_details?.nom || c.patient?.nom || ('Patient #' + (c.patient_id || c.patient)) }}"
new_c_pat = "{{ c.patientDetails?.prenom || c.patient_details?.prenom || c.patient?.prenom || c.patient_prenom || '' }} {{ c.patientDetails?.nom || c.patient_details?.nom || c.patient?.nom || c.patient_nom || ('Patient #' + (c.patient_id || c.patient)) }}"
content = content.replace(old_c_pat, new_c_pat)

# Replace doctor display in consultations
old_c_doc = "Dr. {{ c.medecin_details?.prenom || c.medecin?.prenom }} {{ c.medecin_details?.nom || c.medecin?.nom || ('Médecin #' + (c.medecin_id || c.medecin)) }}"
new_c_doc = "Dr. {{ c.medecinDetails?.prenom || c.medecin_details?.prenom || c.medecin?.prenom || c.medecin_prenom || '' }} {{ c.medecinDetails?.nom || c.medecin_details?.nom || c.medecin?.nom || c.medecin_nom || ('Médecin #' + (c.medecin_id || c.medecin)) }}"
content = content.replace(old_c_doc, new_c_doc)

# Replace patient in hosp
old_h_pat = "{{ h.patient_details?.prenom }} {{ h.patient_details?.nom || ('Patient #' + (h.patient_id || h.patient)) }}"
new_h_pat = "{{ h.patientDetails?.prenom || h.patient_details?.prenom || h.patientPrenom || h.patient_prenom || '' }} {{ h.patientDetails?.nom || h.patient_details?.nom || h.patientNom || h.patient_nom || ('Patient #' + (h.patient_id || h.patient)) }}"
content = content.replace(old_h_pat, new_h_pat)

# Replace doctor in hosp
old_h_doc = "Dr. {{ h.medecin_details?.prenom }} {{ h.medecin_details?.nom || 'Non assigné' }}"
new_h_doc = "Dr. {{ h.medecinDetails?.prenom || h.medecin_details?.prenom || h.medecinPrenom || h.medecin_prenom || '' }} {{ h.medecinDetails?.nom || h.medecin_details?.nom || h.medecinNom || h.medecin_nom || 'Non assigné' }}"
content = content.replace(old_h_doc, new_h_doc)

if '<div class="table-responsive">' not in content:
    def wrap_table(match):
        return f'<div class="table-responsive">\n        {match.group(0)}\n      </div>'
    content = re.sub(r'<table class="data-table">[\s\S]*?</table>', wrap_table, content)
    print("Wrapped tables in admin-medical.component.html")

with open(path_html, "w", encoding="utf-8") as f:
    f.write(content)

path_scss = r"c:\Users\Ibrahima Sory\Desktop\Sante\Sante_Numerique\frontend\src\app\features\admin\pages\medical\admin-medical.component.scss"
with open(path_scss, "r", encoding="utf-8") as f:
    scss = f.read()

if ".data-table {" in scss and "min-width:" not in scss:
    scss = scss.replace(".data-table {", ".data-table {\n  min-width: 720px;\n")
    with open(path_scss, "w", encoding="utf-8") as f:
        f.write(scss)
    print("Added min-width to data-table in admin-medical.component.scss")

