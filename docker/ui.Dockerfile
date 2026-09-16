FROM nginx:1.27-alpine

# Swap standard defaults with our routing rules
COPY deploy/nginx/default.conf /etc/nginx/conf.d/default.conf

# Map static file assets into the server directory
COPY app/ui/ /usr/share/nginx/html/

EXPOSE 80
