path_html = r"c:\Users\Ibrahima Sory\Desktop\Sante\Sante_Numerique\frontend\src\app\features\doctor\pages\appointments\doctor-appointments.component.html"
with open(path_html, "r", encoding="utf-8") as f:
    html = f.read()

target = """                    <div class="cell-title">
                      {{ rdv.patientDetails?.prenom || rdv.patient_details?.prenom || rdv.patient_detail?.prenom || rdv.patientPrenom || rdv.patient_prenom || '' }} {{ rdv.patientDetails?.nom || rdv.patient_details?.nom || rdv.patient_detail?.nom || rdv.patientNom || rdv.patient_nom || ('Patient #' + (rdv.patient || rdv.id_patient)) }}
                    </div>"""

replacement = """                    <div class="cell-title">{{ getPatientFullName(rdv) }}</div>"""

html = html.replace(target, replacement)

# In mobile card too (notice 20 spaces)
target2 = """                  <div class="cell-title">
                    {{ rdv.patientDetails?.prenom || rdv.patient_details?.prenom || rdv.patient_detail?.prenom || rdv.patientPrenom || rdv.patient_prenom || '' }} {{ rdv.patientDetails?.nom || rdv.patient_details?.nom || rdv.patient_detail?.nom || rdv.patientNom || rdv.patient_nom || ('Patient #' + (rdv.patient || rdv.id_patient)) }}
                  </div>"""

replacement2 = """                  <div class="cell-title">{{ getPatientFullName(rdv) }}</div>"""

html = html.replace(target2, replacement2)

with open(path_html, "w", encoding="utf-8") as f:
    f.write(html)
print("Replaced patient titles with getPatientFullName(rdv)")

