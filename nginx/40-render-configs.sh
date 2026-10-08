#!/bin/sh
set -eu

envsubst '${DOMAIN}' \
    < /etc/nginx/project-templates/http.conf.template \
    > /etc/nginx/conf.d/default.conf

certificate="/etc/letsencrypt/live/${DOMAIN}/fullchain.pem"
if [ -f "$certificate" ]; then
    envsubst '${DOMAIN}' \
        < /etc/nginx/project-templates/https.conf.template \
        > /etc/nginx/conf.d/https.conf
else
    rm -f /etc/nginx/conf.d/https.conf
    echo "TLS certificate for ${DOMAIN} is not installed yet; HTTPS is disabled"
fi

# Certbot renews certificates in a shared volume. Reloading makes Nginx pick
# up the renewed files without restarting the container.
(
    while sleep 6h; do
        nginx -s reload || true
    done
) &
