#!/bin/bash

# Collect static files at runtime when environment variables are available
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start Gunicorn
echo "Starting Gunicorn..."
exec gunicorn --bind 0.0.0.0:8000 a_core.wsgi:application
