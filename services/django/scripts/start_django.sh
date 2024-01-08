#!/bin/bash

# Apply database migrations
echo "Applying database migrations..."
# python src/manage.py makemigrations # TODO maybe remove
python src/manage.py migrate

# Start server
echo "Starting server..."
python src/manage.py runserver 0.0.0.0:8000
