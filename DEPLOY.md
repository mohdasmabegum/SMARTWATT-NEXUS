# Deployment Guide — SMARTWATT NEXUS

This document explains how to deploy SMARTWATT NEXUS to a VPS using Docker and Nginx. For a quick PaaS deploy, skip to the "PaaS" section.

1) Prepare your VPS
- Ubuntu 22.04 or similar is recommended.
- Install Docker and docker-compose:

```bash
sudo apt update
sudo apt install -y docker.io docker-compose
sudo usermod -aG docker $USER
```

2) Copy repository to server

```bash
git clone <your-repo-url> /var/www/smartwatt
cd /var/www/smartwatt
```

3) Configure environment
- Copy the example env and set secure values:

```bash
cp .env.production.example .env.production
# Edit .env.production and set SECRET_KEY and DB credentials
```

4) Start services via docker-compose

```bash
cd /var/www/smartwatt
docker-compose up -d --build
```

Check the containers:

```bash
docker-compose ps
docker-compose logs -f web
```

5) Configure Nginx and SSL
- Copy `deploy/nginx/smartwatt.conf` to `/etc/nginx/sites-available/smartwatt` and edit `server_name` and `alias` paths.

```bash
sudo cp deploy/nginx/smartwatt.conf /etc/nginx/sites-available/smartwatt
sudo ln -s /etc/nginx/sites-available/smartwatt /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

Get TLS using Certbot:

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d example.com -d www.example.com
```
Quick public URL (ngrok) — temporary, for testing
- Install ngrok and expose local port 5000 to the internet (useful for demos).

```bash
# Install / sign in to ngrok, then run:
ngrok http 5000

# ngrok will print a public URL like https://abcd1234.ngrok.io
# Use that URL to access your local app from anywhere temporarily.
```

Note: ngrok is for testing/demos only — use a proper VPS or PaaS for production.

6) Optional: systemd service
- Install the provided systemd unit to run docker-compose on boot:

```bash
sudo cp deploy/systemd/smartwatt.service /etc/systemd/system/smartwatt.service
sudo systemctl daemon-reload
sudo systemctl enable --now smartwatt.service
```

PaaS quick option (Render / Railway / Fly)
- Push repo to GitHub and create a Web Service on the platform.
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn backend.app:app -w 4 -b 0.0.0.0:$PORT`
- Set environment variables `SECRET_KEY` and `DATABASE_URL` in the service settings.

Notes
- For production use PostgreSQL (docker-compose example uses Postgres). Update `SQLALCHEMY_DATABASE_URI` accordingly.
- Use a proper secrets manager for `SECRET_KEY`.
- Monitor logs: `docker-compose logs -f web`
