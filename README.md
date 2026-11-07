# 🏥 Santé Numérique — Système d'Information Hospitalier (SIH)

**Santé Numérique** est une plateforme hospitalière full-stack moderne, sécurisée et modulaire. Elle assure la gestion intégrée du parcours patient, de l'admission à la sortie, la planification des soins, l'infrastructure médicale, la traçabilité médico-légale et la conformité aux exigences de sécurité des données de santé.

---

## 🏗️ Architecture & Technologies

- **Backend** : Python 3.12+ / Django 5.x / Django REST Framework (DRF)
- **Base de Données** : PostgreSQL avec contraintes d'intégrité strictes et migrations
- **Frontend** : Angular (TypeScript, Vite, Architecture par composants modulaires)
- **Sécurité & Authentification** :
  - Authentification JWT via **Cookies HttpOnly**, `SameSite=Lax`, `Secure`
  - Protection contre les failles XSS, CSRF et l'escalade de privilèges
  - Contrôle d'accès basé sur les rôles (RBAC) : `ADMINISTRATEUR`, `MEDECIN`, `INFIRMIER`, `PATIENT`
- **Traçabilité Médico-Légale** : Audit trail complet avec `django-simple-history` (`HistoricalRecords`)
- **Documentation API** : OpenAPI 3.0 & Swagger UI (`drf-spectacular`)

---

## 🚀 Modules Fonctionnels

### 1. 👤 Comptes & Sécurité (`users`)
- Modèle utilisateur personnalisé dérivé d'`AbstractUser` avec identifiants uniques (login, email, téléphone).
- Validation robuste des mots de passe (complexité Django, hachage PBKDF2).
- Protection contre l'auto-élévation de rôle : l'inscription publique est strictement restreinte au rôle `PATIENT`. Seul un `ADMINISTRATEUR` peut créer ou modifier les rôles praticiens.

### 2. 🩺 Parcours Patient & Hospitalisation
- **Patients (`patients`)** : Dossier administratif et médical, contacts d'urgence, groupe sanguin, archivage logique (Soft Delete).
- **Séjours (`sejour`)** : Gestion du séjour hospitalier avec génération concurrente sécurisée du numéro de référence (`select_for_update`).
- **Localisations (`localisation`)** : Suivi temporel du patient (bâtiment, chambre, lit) avec contraintes d'exclusion mutuelle évitant les doubles affectations simultanées.
- **Mouvements (`mouvement`)** : Traçabilité des admissions, transferts de service et sorties médicales.
- **Événements (`evenement`)** : Journalisation chronologique des actes et observations cliniques du séjour.

### 3. 👨‍⚕️ Praticiens & Personnel Hospitalier (`medecin`, `personnel`)
- **Médecins** : Spécialités, matricule, numéro d'ordre CNOM, planning de disponibilités hebdomadaires et gestion des indisponibilités / congés.
- **Personnel soignant** : Infirmiers, techniciens et agents administratifs rattachés aux services.

### 4. 🏢 Infrastructure Médicale (`services`, `batiment`, `chambre`, `lit`)
- Cartographie des services (Cardiologie, Urgences, Pédiatrie, etc.).
- Bâtiments, étages et typologie des chambres avec tarification journalière.
- Gestion en temps réel de l'état des lits (`DISPONIBLE`, `OCCUPE`, `RESERVE`, `HORS_SERVICE`).

### 5. 📅 Consultations, Prescriptions & Facturation
- **Rendez-vous (`rendezvous`)** : Planification avec prévention des doubles réservations (détection de collision médecin/patient par date et heure).
- **Consultations (`consultation`)** : Observations médicales, motifs et diagnostics.
- **Ordonnances (`ordonnance`, `ligne_ordonnance`)** : Prescriptions médicales détaillées (médicament, forme, posologie, durée de traitement).
- **Frais de consultation (`frais_consultation`)** : Tarification et suivi financier des actes.

### 6. 👶 État Civil Hospitalier (`natalite`, `mortalite`)
- **Natalité** : Registre sécurisé des naissances (poids, taille, heure, score APGAR), accessible uniquement à la mère, au médecin accoucheur ou à l'administration.
- **Mortalité** : Déclarations de décès médicalement constatés avec cause et horodatage légal.

---

## 🛡️ Sécurité & Conformité de l'Audit

Le projet applique les règles de sécurité suivantes issues de l'audit de sécurisation :
1. **Contrôle d'accès au parcours patient** : Périmètre strict selon le rôle ; un patient n'accède qu'à ses propres données, un médecin à sa patientèle autorisée.
2. **Cloisonnement des profils** : Impossibilité pour un praticien ou un patient de modifier ou supprimer le compte d'un autre utilisateur.
3. **Protection des secrets** : Aucun mot de passe ni clé en clair dans le code, les seeders ou les dépôts.
4. **Soft Delete par défaut** : Préservation des historiques légaux via `actif = False` ou état `HORS_SERVICE` (suppression physique possible via `?hard=true` par un administrateur).
5. **Audit historique** : Historisation automatique de chaque modification (`HistoricalRecords`) sur les tables critiques (sans jamais stocker le hash des mots de passe dans l'historique).

---

## ⚙️ Installation & Démarrage

### 1. Prérequis
- **Python 3.10+** et **PostgreSQL 14+**
- **Node.js 18+** et **npm**

### 2. Configuration du Backend

```bash
# Se placer dans le dossier backend
cd Sante_Numerique/backend

# Créer et activer l'environnement virtuel
python -m venv ../venv
# Windows (PowerShell) :
..\venv\Scripts\Activate.ps1
# Linux / macOS :
source ../venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Configurer les variables d'environnement (.env)
cp .env.example .env
# Renseigner DATABASE_URL=postgres://user:password@localhost:5432/sante_numerique

# Appliquer les migrations
python manage.py migrate

# Démarrer le serveur backend Django
python manage.py runserver 0.0.0.0:8000
```

### 3. Configuration du Frontend Angular

```bash
# Se placer dans le dossier frontend
cd Sante_Numerique/frontend

# Installer les dépendances Node
npm install

# Démarrer le serveur de développement Angular
npm start
```
L'application est disponible sur `http://localhost:4200/`.

> 💡 **Sous Windows PowerShell** : Si l'exécution des scripts est restreinte, exécutez au préalable :  
> `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` ou utilisez `npm.cmd start`.

> 🌐 **Accès distant via VS Code DevTunnels** : Le projet prend en charge automatiquement les domaines `*.devtunnels.ms` (CORS et détection d'API dynamique).

---

## 🧪 Tests Automatisés

Le projet intègre une suite de **224 tests automatisés** couvrant les modèles, les services, les validateurs, les contrôles d'accès RBAC et les scénarios de l'audit de sécurité.

Pour exécuter l'ensemble des tests :

```bash
cd Sante_Numerique/backend
python manage.py test
```

Pour exécuter uniquement les tests de sécurité de l'audit :
```bash
python manage.py test tests_audit_securite
```

---

## 📖 Documentation Interactive de l'API

Lorsque le backend est en cours d'exécution, la documentation est accessible sur :
- **Swagger UI** : [http://127.0.0.1:8000/swagger/](http://127.0.0.1:8000/swagger/)
- **ReDoc** : [http://127.0.0.1:8000/redoc/](http://127.0.0.1:8000/redoc/)
- **Schéma OpenAPI 3.0** : [http://127.0.0.1:8000/api/schema/](http://127.0.0.1:8000/api/schema/)

---

## 📂 Structure du Répertoire

```text
Sante_Numerique/
├── backend/
│   ├── config/              # Paramètres globaux, URLs, permissions RBAC, JWT
│   ├── users/               # Comptes, rôles, profils et authentification
│   ├── patients/            # Dossiers patients et antécédents
│   ├── medecin/             # Médecins, disponibilités et congés
│   ├── personnel/           # Personnel soignant et administratif
│   ├── services/            # Pôles et services hospitaliers
│   ├── batiment/            # Bâtiments hospitaliers
│   ├── chambre/             # Chambres d'hospitalisation
│   ├── lit/                 # Lits et disponibilités
│   ├── rendezvous/          # Prise de RDV et prévention de collision
│   ├── consultation/        # Actes de consultation et diagnostics
│   ├── ordonnance/          # Ordonnances médicales
│   ├── ligne_ordonnance/    # Lignes de prescription et posologies
│   ├── frais_consultation/  # Facturation des consultations
│   ├── sejour/              # Séjours d'hospitalisation
│   ├── localisation/        # Affectation temporelle (chambre / lit)
│   ├── mouvement/           # Admissions, mutations et sorties
│   ├── evenement/           # Journal des événements cliniques
│   ├── natalite/            # Registre des naissances
│   ├── mortalite/           # Registre des décès
│   ├── seeder/              # Jeux de données d'initialisation sécurisés
│   ├── tests_audit_securite.py # Suite de validation de sécurité
│   └── manage.py
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── core/        # Services d'authentification, intercepteurs JWT
│   │   │   ├── features/    # Modules métiers (admin, patient, médecin, soignant)
│   │   │   └── shared/      # Composants réutilisables, pipes, modèles
│   │   └── environments/    # Détection dynamique des endpoints API & tunnels
│   └── package.json
└── README.md
```
