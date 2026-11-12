path_doc_models = r"c:\Users\Ibrahima Sory\Desktop\Sante\Sante_Numerique\frontend\src\app\features\doctor\models\doctor.models.ts"
with open(path_doc_models, "r", encoding="utf-8") as f:
    doc_models = f.read()

# Add direct fields to DoctorAppointmentDto
old_apt_target = "  statut: AppointmentStatus;\n}"
new_apt_target = """  statut: AppointmentStatus;
  patient_nom?: string;
  patientNom?: string;
  patient_prenom?: string;
  patientPrenom?: string;
  patient_telephone?: string;
  patientTelephone?: string;
  medecin_nom?: string;
  medecinNom?: string;
  medecin_prenom?: string;
  medecinPrenom?: string;
  medecin_specialite?: string;
  medecinSpecialite?: string;
}"""
if "patient_nom?:" not in doc_models and old_apt_target in doc_models:
    doc_models = doc_models.replace(old_apt_target, new_apt_target, 1)

# Add to DoctorConsultationDto
old_cons_target = "  date_cons?: string;"
new_cons_target = """  patient_nom?: string;
  patientNom?: string;
  patient_prenom?: string;
  patientPrenom?: string;
  medecin_nom?: string;
  medecinNom?: string;
  medecin_prenom?: string;
  medecinPrenom?: string;
  date_cons?: string;"""
if "patient_nom?:" in doc_models and old_cons_target in doc_models:
    doc_models = doc_models.replace(old_cons_target, new_cons_target, 1)

with open(path_doc_models, "w", encoding="utf-8") as f:
    f.write(doc_models)
print("Updated doctor.models.ts")

# Now patch patient.models.ts
path_pat_models = r"c:\Users\Ibrahima Sory\Desktop\Sante\Sante_Numerique\frontend\src\app\features\patient\models\patient.models.ts"
with open(path_pat_models, "r", encoding="utf-8") as f:
    pat_models = f.read()

old_c_target = "  date_cons?: string;"
new_c_target = """  patient_nom?: string;
  patientNom?: string;
  patient_prenom?: string;
  patientPrenom?: string;
  medecin_nom?: string;
  medecinNom?: string;
  medecin_prenom?: string;
  medecinPrenom?: string;
  date_cons?: string;"""
if "medecin_nom?:" not in pat_models[:1200] and old_c_target in pat_models:
    pat_models = pat_models.replace(old_c_target, new_c_target, 1)

old_h_target = "  motif: string;"
new_h_target = """  patientDetails?: PatientRecord;
  patient_nom?: string;
  patientNom?: string;
  patient_prenom?: string;
  patientPrenom?: string;
  medecinDetails?: MedecinDto;
  medecin_nom?: string;
  medecinNom?: string;
  medecin_prenom?: string;
  medecinPrenom?: string;
  litDetails?: LitDetailsDto;
  chambre_numero?: string;
  chambreNumero?: string;
  lit_numero?: string;
  litNumero?: string;
  batiment_nom?: string;
  batimentNom?: string;
  dateEntree?: string;
  dateSortie?: string | null;
  motif: string;"""
if "chambreNumero?:" not in pat_models and old_h_target in pat_models:
    pat_models = pat_models.replace(old_h_target, new_h_target, 1)

with open(path_pat_models, "w", encoding="utf-8") as f:
    f.write(pat_models)
print("Updated patient.models.ts")

