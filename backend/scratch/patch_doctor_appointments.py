path_html = r"c:\Users\Ibrahima Sory\Desktop\Sante\Sante_Numerique\frontend\src\app\features\doctor\pages\appointments\doctor-appointments.component.html"
with open(path_html, "r", encoding="utf-8") as f:
    html = f.read()

old_pat = "{{ rdv.patient_details?.prenom || rdv.patient_detail?.prenom }} {{ rdv.patient_details?.nom || rdv.patient_detail?.nom }}"
new_pat = "{{ rdv.patientDetails?.prenom || rdv.patient_details?.prenom || rdv.patient_detail?.prenom || rdv.patientPrenom || rdv.patient_prenom || '' }} {{ rdv.patientDetails?.nom || rdv.patient_details?.nom || rdv.patient_detail?.nom || rdv.patientNom || rdv.patient_nom || ('Patient #' + (rdv.patient || rdv.id_patient)) }}"
html = html.replace(old_pat, new_pat)

old_phone = "{{ rdv.patient_details?.telephone || rdv.patient_detail?.telephone || 'Pas de téléphone' }}"
new_phone = "{{ rdv.patientDetails?.telephone || rdv.patient_details?.telephone || rdv.patient_detail?.telephone || rdv.patientTelephone || rdv.patient_telephone || 'Pas de téléphone' }}"
html = html.replace(old_phone, new_phone)

old_phone_mob = "{{ rdv.patient_details?.telephone || rdv.patient_detail?.telephone || 'Sans tél' }}"
new_phone_mob = "{{ rdv.patientDetails?.telephone || rdv.patient_details?.telephone || rdv.patient_detail?.telephone || rdv.patientTelephone || rdv.patient_telephone || 'Sans tél' }}"
html = html.replace(old_phone_mob, new_phone_mob)

with open(path_html, "w", encoding="utf-8") as f:
    f.write(html)
print("Updated doctor-appointments.component.html")

