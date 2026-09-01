# Backend - Santé Numérique

Ce dossier contient l’API Django de la plateforme Santé Numérique.

## Stack technique

- Python 3.12+
- Django 6.1
- Django REST Framework
- Simple JWT
- drf-spectacular (OpenAPI / Swagger)
- django-cors-headers
- SQLite en environnement de développement

## Structure du backend

```text
backend/
├── config/                 # Paramétrage global Django
│   ├── settings.py
│   ├── urls.py
│   ├── authentication.py
│   ├── pagination.py
│   ├── permissions.py
│   └── validators.py
├── common/                 # Utils et URLs communes
├── users/                  # Authentification et gestion des comptes
├── patients/               # Dossiers patients
├── medecin/                # Médecins
├── personnel/              # Personnel hospitalier
├── services/               # Services hospitaliers
├── batiment/               # Bâtiments
├── chambre/                # Chambres
├── lit/                    # Lits
├── rendezvous/             # Rendez-vous
├── natalite/               # Registre de natalité
├── mortalite/              # Registre de mortalité
├── hospitalisation/        # Hospitalisations
├── consultation/           # Consultations
├── frais_consultation/     # Frais de consultation
├── ordonnance/             # Ordonnances
├── seeder/                 # Données de démonstration
├── db.sqlite3              # Base locale
├── manage.py               # Point d’entrée Django
├── requirements.txt        # Dépendances Python
├── .env                    # Variables locales
├── .env.example            # Exemple de configuration
└── pyrightconfig.json      # Configuration Pyright
```

## Prérequis

- Python installé
- Environnement virtuel Python
- Accès au projet depuis un terminal

## Setup

Depuis le dossier backend :

```bash
cd backend
python -m venv venv
```

Sur Windows :

```bash
venv\Scripts\activate
```

Sur Linux / macOS :

```bash
source venv/bin/activate
```

Puis installer les dépendances :

```bash
pip install -r requirements.txt
```

Créer le fichier d’environnement local :

```bash
copy .env.example .env
```

ou sur Linux/macOS :

```bash
cp .env.example .env
```

Exemple de contenu recommandé :

```env
SECRET_KEY=votre_cle_secrete
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
CORS_ALLOWED_ORIGINS=http://localhost:4200
JWT_COOKIE_SAMESITE=Lax
JWT_COOKIE_SECURE=False
THROTTLE_ANON_RATE=100/day
THROTTLE_USER_RATE=1000/day
THROTTLE_LOGIN_RATE=5/minute
```

## Migrations et base de données

```bash
python manage.py migrate
```

Si vous souhaitez générer de nouvelles migrations :

```bash
python manage.py makemigrations
python manage.py migrate
```

## Démarrer le serveur

```bash
python manage.py runserver 0.0.0.0:8000
```

L’API sera alors disponible sur :

- http://localhost:8000/
- http://localhost:8000/swagger/
- http://localhost:8000/redoc/
- http://localhost:8000/api/schema/

## Vérification rapide

```bash
python manage.py check
```

## Tests

```bash
python manage.py test
```

## Notes importantes

- Le projet utilise une authentification JWT via `rest_framework_simplejwt`.
- Le backend est configuré pour accepter les requêtes CORS depuis le frontend Angular sur `http://localhost:4200`.
- Le mode `DEBUG` est piloté via le fichier `.env`.
- Le dépôt contient déjà une base SQLite locale pour les tests et le développement.

## Commandes utiles

```bash
python manage.py createsuperuser
python manage.py shell
python manage.py collectstatic
```
