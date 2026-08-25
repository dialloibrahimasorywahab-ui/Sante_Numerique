# 🏥 Santé Numérique - Plateforme de Gestion Hospitalière

**Santé Numérique** est une application web RESTful complète dédiée à la digitalisation et la gestion intégrée des établissements hospitaliers. Elle permet la centralisation des données médicales, le suivi des patients, la gestion du personnel soignant, la réservation d'infrastructures (bâtiments, chambres, lits), la planification des rendez-vous ainsi que la traçabilité des actes d'état civil hospitalier (natalité et mortalité).

---

## 🚀 Fonctionnalités Principales

### 👤 1. Gestion des Utilisateurs & Accès (`users`)
- **Modèle Utilisateur Personnalisé** basé sur `AbstractUser` de Django.
- **Gestion des Rôles** : `ADMINISTRATEUR`, `MEDECIN`, `INFIRMIER`, `PATIENT`.
- Authentification par `login` ou `email` avec hachage sécurisé des mots de passe.

### 🩺 2. Dossiers Patients (`patients`)
- Enregistrement des dossiers médicaux patients.
- Informations personnelles, groupe sanguin, contacts d'urgence, adresse et historique.
- Désactivation/Archivage du dossier avec conservation de l'historique médical.

### 👨‍⚕️ 3. Corps Médical & Personnel (`medecin` & `personnel`)
- Gestion des médecins (spécialité, statut d'activité, rattachement aux services).
- Gestion du personnel soignant et administratif (infirmiers, agents de réception).

### 🏢 4. Infrastructure Hospitalière (`services`, `batiment`, `chambre`, `lit`)
- **Services** : Création et gestion des services hospitaliers (Urgences, Maternité, Cardiologie...).
- **Bâtiments** : Suivi des bâtiments et capacité globale.
- **Chambres** : Gestion des chambres individuelles et communes avec tarification journalière.
- **Lits** : Suivi en temps réel de la disponibilité des lits et génération automatique de lits par chambre.

### 📅 5. Planification des Rendez-Vous (`rendezvous`)
- Prise de rendez-vous entre patients et médecins.
- Suivi du cycle de vie du RDV (`PLANIFIE`, `CONFIRME`, `TERMINE`, `ANNULE`).

### 👶 6. Module Natalité (`natalite`)
- Enregistrement des naissances hospitalières.
- Association avec la mère (dossier patient) et le médecin accoucheur.
- Suivi des données physiologiques du nouveau-né (poids en kg, taille en cm, heure de naissance, sexe, observation).

### ⚰️ 7. Module Mortalité (`mortalite`)
- Déclaration et registre des décès hospitaliers.
- Association avec le patient décédé et le médecin ayant constaté le décès.
- Saisie de la date, l'heure et la cause du décès.

---

## 🛡️ Gestion de la Suppression (Soft Delete / Archivage)

Pour garantir l'intégrité des données médicales et légales, la suppression d'enregistrements s'effectue par **désactivation logique (Soft Delete)** par défaut :
- **Utilisateurs / Patients / Médical / Personnel** : Marqué comme inactif (`actif = False`).
- **Services & Bâtiments** : Passage à inactif (`actif = False`).
- **Chambres & Lits** : Statut/État basculé sur `HORS_SERVICE`.
- **Rendez-vous** : Statut basculé sur `ANNULE`.

> 💡 *Note* : La suppression définitive de la base de données peut être forcée en ajoutant le paramètre de requête `?hard=true` à l'URL de suppression (ex: `DELETE /patients/1/delete/?hard=true`).

---

## 🛠️ Spécifications Techniques

- **Langage & Framework** : Python 3.12+ / Django 6.1
- **API REST** : Django REST Framework (DRF)
- **Documentation API** : `drf-spectacular` (OpenAPI 3.0 & Swagger UI)
- **Base de Données** : SQLite3 (Environnement de Développement)

---

## ⚙️ Installation & Démarrage

### 1. Prérequis
- Python 3.10+ installé sur votre machine.

### 2. Cloner le Projet & Créer l'environnement virtuel
```bash
# Cloner le dépôt
git clone <URL_DU_DEPOT>
cd Sante_Numerique

# Créer un environnement virtuel
python -m venv venv

# Activer l'environnement virtuel (Windows)
.\venv\Scripts\activate

# Activer l'environnement virtuel (Linux/MacOS)
source venv/bin/activate
```

### 3. Installer les Dépendances
```bash
pip install -r requirements.txt
```

### 4. Appliquer les Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Lancer le Serveur de Développement
```bash
python manage.py runserver
```
L'application sera accessible sur `http://127.0.0.1:8000/`.

---

## 📖 Documentation Interactive de l'API (Swagger / OpenAPI)

Lorsque le serveur de développement est en cours d'exécution, la documentation Swagger et ReDoc est immédiatement accessible :

- 📌 **Swagger UI** : [http://127.0.0.1:8000/swagger/](http://127.0.0.1:8000/swagger/) (ou `/docs/`)
- 📌 **ReDoc** : [http://127.0.0.1:8000/redoc/](http://127.0.0.1:8000/redoc/)
- 📌 **Schéma OpenAPI 3.0** : [http://127.0.0.1:8000/api/schema/](http://127.0.0.1:8000/api/schema/)

---

## 🧪 Exécution des Tests Automatisés

Le projet intègre une suite de **84 tests unitaires et d'intégration** couvrant l'ensemble des modèles, dépôts, services et endpoints REST API.

Pour lancer tous les tests :
```bash
python manage.py test
```

---

## 📌 Structure du Projet

```text
Sante_Numerique/
│
├── config/             # Configuration globale Django (settings, urls, wsgi)
├── users/              # Authentification & Modèle Utilisateur AbstractUser
├── patients/           # Gestion des patients et dossiers médicaux
├── medecin/            # Gestion des médecins et praticiens
├── personnel/          # Gestion du personnel infirmier & administratif
├── services/           # Services hospitaliers
├── batiment/           # Infrastructure bâtiment
├── chambre/            # Chambres d'hospitalisation
├── lit/                # Lits et disponibilités
├── rendezvous/         # Prise et suivi des rendez-vous
├── natalite/           # Registre des naissances & nouveaux-nés
├── mortalite/          # Registre des décès hospitaliers
│
├── db.sqlite3          # Base de données de développement
├── manage.py           # Script de gestion Django
└── requirements.txt    # Dépendances du projet
```
