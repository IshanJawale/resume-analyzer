FROM python:3.11

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

# Create staticfiles directory and copy startup script
RUN mkdir -p /app/staticfiles
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

EXPOSE 8000

# Use startup script that collects static files then starts Gunicorn
CMD ["/app/start.sh"]