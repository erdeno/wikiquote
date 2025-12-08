# Frontend Dockerfile
FROM nginx:alpine

# Copy frontend files to nginx html directory
COPY frontend/ /usr/share/nginx/html/

# Copy custom nginx configuration
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 8080

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
