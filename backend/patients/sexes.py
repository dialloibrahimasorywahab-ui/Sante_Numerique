PRENOMS_FEMININS = {
    "fatoumata",
    "aissatou",
    "mariama",
    "kadiatou",
    "binta",
    "sainabou",
    "hawa",
    "aminata",
    "fanta",
    "habayatou",
}

PRENOMS_MASCULINS = {
    "amadou",
    "ibrahima",
    "mamadou",
    "ousmane",
    "boubacar",
    "alpha",
    "mohamed",
    "cherif",
    "sory",
    "alhassane",
}


def sexe_depuis_prenom(prenom):
    prenom_principal = str(prenom or "").strip().casefold().split()[0:1]
    if not prenom_principal:
        return None

    prenom_principal = prenom_principal[0]
    if prenom_principal in PRENOMS_FEMININS:
        return "F"
    if prenom_principal in PRENOMS_MASCULINS:
        return "M"
    return None
