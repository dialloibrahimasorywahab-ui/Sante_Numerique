path_ts = r"c:\Users\Ibrahima Sory\Desktop\Sante\Sante_Numerique\frontend\src\app\features\doctor\pages\appointments\doctor-appointments.component.ts"
with open(path_ts, "r", encoding="utf-8") as f:
    ts = f.read()

methods = """  getPatientFullName(rdv: any): string {
    if (!rdv) return 'Patient';
    const p = rdv.patientDetails || rdv.patient_details || rdv.patientDetail || rdv.patient_detail;
    if (p && (p.prenom || p.nom)) {
      return `${p.prenom || ''} ${p.nom || ''}`.trim();
    }
    const prenom = rdv.patient_prenom || rdv.patientPrenom || '';
    const nom = rdv.patient_nom || rdv.patientNom || '';
    if (prenom || nom) {
      return `${prenom} ${nom}`.trim();
    }
    const id = rdv.patient || rdv.id_patient || rdv.idPatient;
    return id ? `Patient #${id}` : 'Patient suivi';
  }

  getPatientPhone(rdv: any): string {
    if (!rdv) return 'Pas de téléphone';
    const p = rdv.patientDetails || rdv.patient_details || rdv.patientDetail || rdv.patient_detail;
    return p?.telephone || rdv.patient_telephone || rdv.patientTelephone || 'Pas de téléphone';
  }
"""

if "getPatientFullName" not in ts:
    # insert before the last closing brace
    last_brace = ts.rfind("}")
    ts = ts[:last_brace] + methods + "\n}\n"
    with open(path_ts, "w", encoding="utf-8") as f:
        f.write(ts)
    print("Added getPatientFullName to doctor-appointments.component.ts")

# Now update doctor-appointments.component.html
path_html = r"c:\Users\Ibrahima Sory\Desktop\Sante\Sante_Numerique\frontend\src\app\features\doctor\pages\appointments\doctor-appointments.component.html"
with open(path_html, "r", encoding="utf-8") as f:
    html = f.read()

# Replace any complex patient name expression in desktop table and mobile card
import re
html = re.sub(
    r'<div class="cell-title">\s*\{\{[^\}]*patient[^\}]*\}\}\s*</div>',
    '<div class="cell-title">{{ getPatientFullName(rdv) }}</div>',
    html
)
html = re.sub(
    r'<div class="cell-sub">\s*\{\{[^\}]*telephone[^\}]*\}\}\s*</div>',
    '<div class="cell-sub">{{ getPatientPhone(rdv) }}</div>',
    html
)

with open(path_html, "w", encoding="utf-8") as f:
    f.write(html)
print("Updated doctor-appointments.component.html")

# Also add properties to DoctorAppointmentDto in doctor.models.ts
path_models = r"c:\Users\Ibrahima Sory\Desktop\Sante\Sante_Numerique\frontend\src\app\features\doctor\models\doctor.models.ts"
with open(path_models, "r", encoding="utf-8") as f:
    models = f.read()

target = "export interface DoctorAppointmentDto {"
fields = """export interface DoctorAppointmentDto {
  patient_nom?: string;
  patientNom?: string;
  patient_prenom?: string;
  patientPrenom?: string;
  patient_telephone?: string;
  patientTelephone?: string;
  medecin_nom?: string;
  medecinNom?: string;
  medecin_prenom?: string;
  medecinPrenom?: string;"""

if target in models and "patient_nom?:" not in models:
    models = models.replace(target, fields, 1)
    with open(path_models, "w", encoding="utf-8") as f:
        f.write(models)
    print("Updated DoctorAppointmentDto in doctor.models.ts")

