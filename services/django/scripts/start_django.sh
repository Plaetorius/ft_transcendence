#!/bin/bash

# Apply database migrations
echo "Applying database migrations..."
python src/manage.py makemigrations
python src/manage.py migrate

# Start server
echo "Starting server..."
python src/manage.py runserver 0.0.0.0:8000

sleep 1
python src/manage.py createsuperuser --username=tgernez --email=tgernez@student.42.fr --profile-picture=profile_pictures/tgernez.jpg