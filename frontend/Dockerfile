# Stage 1: Build de l'application Angular
FROM node:22-alpine AS builder

WORKDIR /app

# Copie des manifestes de dépendances
COPY package*.json ./

# Installation propre des dépendances avec cache npm
RUN npm ci

# Copie de l'intégralité du code frontend
COPY . .

# Build de production optimisé
RUN npm run build

# Stage 2: Serveur Nginx léger pour servir les fichiers statiques et gérer le routing SPA
FROM nginx:alpine

# Sécurité : suppression des fichiers de bienvenue par défaut
RUN rm -rf /usr/share/nginx/html/*

# Copie des fichiers compilés depuis le builder
COPY --from=builder /app/dist/sante-numerique/browser /usr/share/nginx/html

# Copie de la configuration Nginx optimisée pour Angular SPA
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Port HTTP interne
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

