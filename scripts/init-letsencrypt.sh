#!/bin/bash
# ==============================================================================
# Script d'initialisation et d'obtention des certificats SSL Let's Encrypt
# ==============================================================================
set -e

# Charger les variables du fichier .env
if [ -f .env ]; then
    export $(cat .env | grep -v '#' | awk '/=/ {print $1}')
fi

domains=(${DOMAIN_NAME:-sante.votre-hopital.fr})
rsa_key_size=4096
data_path="./certbot_data"
email="${CERTBOT_EMAIL:-admin@votre-hopital.fr}"
staging=0 # Mettre à 1 pour tester sans atteindre les limites de Let's Encrypt

if [ "$domains" = "sante.votre-hopital.fr" ]; then
    echo "ATTENTION : DOMAIN_NAME n'est pas configuré dans votre .env."
    echo "Veuillez définir votre nom de domaine réel avant d'exécuter ce script."
    exit 1
fi

echo "### Création des répertoires pour Certbot..."
mkdir -p "$data_path/conf/live/$domains"
mkdir -p "$data_path/www"

echo "### Vérification de l'existence de certificats précédents..."
if [ ! -e "$data_path/conf/live/$domains/cert.pem" ]; then
    echo "### Création d'un certificat factice temporaire pour permettre à Nginx de démarrer..."
    path="/etc/letsencrypt/live/$domains"
    mkdir -p "$data_path/conf/live/$domains"
    docker compose run --rm --entrypoint "\
        openssl req -x509 -nodes -newkey rsa:$rsa_key_size -days 1\
            -keyout '$path/privkey.pem' \
            -out '$path/fullchain.pem' \
            -subj '/CN=localhost'" certbot
    echo
fi

echo "### Démarrage de Nginx..."
docker compose up --force-recreate -d nginx
echo

echo "### Suppression du certificat factice temporaire..."
docker compose run --rm --entrypoint "\
    rm -Rf /etc/letsencrypt/live/$domains && \
    rm -Rf /etc/letsencrypt/archive/$domains && \
    rm -Rf /etc/letsencrypt/renewal/$domains.conf" certbot
echo

echo "### Demande du certificat officiel Let's Encrypt..."
domain_args=""
for domain in "${domains[@]}"; do
    domain_args="$domain_args -d $domain"
done

# Sélection de l'email
case "$email" in
    "") email_arg="--register-unsafely-without-email" ;;
    *) email_arg="--email $email" ;;
esac

# Mode staging ou production
if [ $staging != "0" ]; then staging_arg="--staging"; fi

docker compose run --rm --entrypoint "\
    certbot certonly --webroot -w /var/www/certbot \
        $staging_arg \
        $email_arg \
        $domain_args \
        --rsa-key-size $rsa_key_size \
        --agree-tos \
        --force-renewal" certbot
echo

echo "### Rechargement de Nginx avec le certificat officiel..."
docker compose exec nginx nginx -s reload
echo "Certificats SSL installés et Nginx rechargé avec succès !"

