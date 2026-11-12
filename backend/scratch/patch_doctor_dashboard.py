import os

path_ts = r"c:\Users\Ibrahima Sory\Desktop\Sante\Sante_Numerique\frontend\src\app\features\doctor\pages\dashboard\doctor-dashboard.component.ts"
with open(path_ts, "r", encoding="utf-8") as f:
    content_ts = f.read()

# Add getPatientFullName and getPatientPhone
method_to_add = """  getPatientFullName(item: any): string {
    if (!item) return 'Patient';
    const p = item.patientDetails || item.patient_details || item.patientDetail || item.patient_detail;
    if (p && (p.prenom || p.nom)) {
      return `${p.prenom || ''} ${p.nom || ''}`.trim();
    }
    const prenom = item.patient_prenom || item.patientPrenom || '';
    const nom = item.patient_nom || item.patientNom || '';
    if (prenom || nom) {
      return `${prenom} ${nom}`.trim();
    }
    const id = item.patient || item.id_patient || item.idPatient;
    return id ? `Patient #${id}` : 'Patient suivi';
  }

  getPatientPhone(item: any): string {
    if (!item) return '';
    const p = item.patientDetails || item.patient_details || item.patientDetail || item.patient_detail;
    return p?.telephone || item.patient_telephone || item.patientTelephone || '';
  }
"""

if "getPatientFullName" not in content_ts:
    target = "  getPatientId("
    content_ts = content_ts.replace(target, method_to_add + "\n" + target)
    with open(path_ts, "w", encoding="utf-8") as f:
        f.write(content_ts)
    print("Updated doctor-dashboard.component.ts")
else:
    print("Already updated doctor-dashboard.component.ts")

# Update doctor-dashboard.component.html
path_html = r"c:\Users\Ibrahima Sory\Desktop\Sante\Sante_Numerique\frontend\src\app\features\doctor\pages\dashboard\doctor-dashboard.component.html"
with open(path_html, "r", encoding="utf-8") as f:
    content_html = f.read()

# In appointment item
old_rdv_patient = "{{ rdv.patient_details?.prenom || rdv.patient_detail?.prenom }} {{ rdv.patient_details?.nom || rdv.patient_detail?.nom }}"
if old_rdv_patient in content_html:
    content_html = content_html.replace(old_rdv_patient, "{{ getPatientFullName(rdv) }}")

old_rdv_phone = "<span>{{ rdv.patient_details?.telephone || rdv.patient_detail?.telephone }}</span>"
if old_rdv_phone in content_html:
    content_html = content_html.replace(old_rdv_phone, "<span>{{ getPatientPhone(rdv) }}</span>")

# In recent consultation item
old_cons_patient = "{{ cons.patient_details?.prenom || cons.patient_detail?.prenom }} {{ cons.patient_details?.nom || cons.patient_detail?.nom }}"
if old_cons_patient in content_html:
    content_html = content_html.replace(old_cons_patient, "{{ getPatientFullName(cons) }}")

with open(path_html, "w", encoding="utf-8") as f:
    f.write(content_html)
print("Updated doctor-dashboard.component.html")
