# Santé Numérique - Frontend

Interface web de la plateforme de gestion hospitalière **Santé Numérique**. Le frontend permet notamment de consulter les services de soins et les médecins, de prendre un rendez-vous et de consulter les rendez-vous du patient connecté.

Le projet est construit avec [Angular](https://angular.dev/) 22, TypeScript, SCSS et RxJS. Il communique avec le backend Django du dépôt via l’API REST.

## Prérequis

- Node.js compatible avec Angular 22
- npm 11 (version déclarée par `package.json`)
- Le backend Django lancé sur `http://127.0.0.1:8000`

## Installation

Depuis ce dossier (`frontend/`) :

```bash
npm install
```

Pour lancer l’API dans un autre terminal, depuis `backend/` :

```bash
python manage.py runserver
```

## Développement

```bash
npm start
```

L’application est disponible sur <http://localhost:4200/>. Le serveur recharge automatiquement l’application après les modifications des fichiers source.

Les services Angular utilisent actuellement l’URL locale `http://127.0.0.1:8000`. Le backend doit donc être démarré avant de tester les appels API et les fonctionnalités nécessitant une session authentifiée.

## Routes disponibles

| Route | Fonctionnalité |
| --- | --- |
| `/` | Accueil |
| `/services` | Liste des services et pôles de soins |
| `/services/:id` | Détail d’un service |
| `/medecins` | Liste de l’équipe médicale |
| `/medecins/:id` | Profil d’un médecin |
| `/rendez-vous` | Prise de rendez-vous |
| `/mes-rendez-vous` | Rendez-vous du patient connecté |

## Commandes npm

| Commande | Description |
| --- | --- |
| `npm start` | Lance le serveur de développement |
| `npm run build` | Génère le build de production dans `dist/` |
| `npm run watch` | Recompile automatiquement en configuration développement |
| `npm test` | Lance les tests unitaires avec Vitest |
| `npm run ng -- generate component nom` | Génère un composant Angular |

Le projet ne contient pas de configuration e2e actuellement.

## Structure principale

```text
frontend/
├── public/                 # Ressources statiques
├── src/
│   ├── app/
│   │   ├── components/     # Composants partagés (en-tête, pied de page...)
│   │   ├── core/           # Services partagés et pagination générique
│   │   └── features/       # Fonctionnalités, pages et modèles métier
│   ├── main.ts             # Point d’entrée Angular
│   └── styles.scss         # Styles globaux
├── angular.json            # Configuration Angular CLI
└── package.json            # Dépendances et scripts npm
```

## Références

- [Documentation Angular](https://angular.dev/)
- [Documentation Angular CLI](https://angular.dev/tools/cli)
- [Documentation Vitest](https://vitest.dev/)
