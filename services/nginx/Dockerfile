FROM nginx:alpine

RUN apk update && \
	apk upgrade && \
    apk add openssl && \ 
    rm -rf /var/cache/apk/*

# Create SSL directory
RUN mkdir -p /etc/nginx/ssl

# Remove the default Nginx configuration file
RUN rm /etc/nginx/conf.d/default.conf

COPY ressources/nginx.conf /etc/nginx/conf.d

# Generate SSL certificate
RUN openssl req -x509 -nodes \
	-out /etc/nginx/ssl/localhost.crt \
	-keyout /etc/nginx/ssl/localhost.key \
	-subj "/C=FR/ST=IDF/L=Paris/O=42/OU=42/CN=localhost/UID=tgernez@student.42.fr"

EXPOSE 443

CMD ["nginx", "-g", "daemon off;"]
