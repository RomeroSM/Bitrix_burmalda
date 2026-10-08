FROM nginx:1.27-alpine

COPY http.conf.template /etc/nginx/project-templates/http.conf.template
COPY https.conf.template /etc/nginx/project-templates/https.conf.template
COPY 40-render-configs.sh /docker-entrypoint.d/40-render-configs.sh

RUN sed -i 's/\r$//' /docker-entrypoint.d/40-render-configs.sh \
    && chmod +x /docker-entrypoint.d/40-render-configs.sh

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget -q --spider http://127.0.0.1/health || exit 1

CMD ["nginx", "-g", "daemon off;"]
