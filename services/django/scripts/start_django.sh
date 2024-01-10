#!/bin/bash

# Apply database migrations
echo "Applying database migrations..."
python src/manage.py makemigrations
python src/manage.py migrate

# Start server
echo "Starting server..."
python src/manage.py runserver 0.0.0.0:8000

sleep 1
echo "from django.contrib.auth.models import User; User.objects.create_superuser('tgernez', 'tgernez@student.42.fr', 'tgernez')" | python manage.py shell
