FROM nginx:alpine

EXPOSE 8000
WORKDIR /usr/share/nginx/html
COPY index.html python-rest-api.js favicon.ico ./
COPY default.template /etc/nginx/conf.d/default.template
COPY docker-entrypoint.sh /
ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"]

