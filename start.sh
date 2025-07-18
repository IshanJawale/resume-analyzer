#!/bin/bash

# Run database migrations first
echo "Running database migrations..."
python manage.py migrate

# Create superuser automatically (optional)
echo "Setting up admin user..."
python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', '', 'admin123')
    print('Superuser created: admin/admin123')
else:
    print('Superuser already exists')
"

# Collect static files at runtime when environment variables are available
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start Gunicorn for production
echo "Starting Gunicorn server..."
exec gunicorn a_core.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 120
