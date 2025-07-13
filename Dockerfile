FROM python:3.11

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

# Create staticfiles directory and collect static files
RUN mkdir -p /app/staticfiles
RUN python manage.py collectstatic --noinput --settings=a_core.settings

EXPOSE 8000

# Use Gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "a_core.wsgi:application"]