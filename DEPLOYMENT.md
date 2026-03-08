# PDFsIn5 Production Deployment Guide

This guide describes how to deploy the PDFsIn5 platform (React FastAPI) to a production server environment using Nginx, Gunicorn, and Vite.

---

## 1. Environment Preparation

### Backend Environment (`backend/.env`)
Create a `.env` file in the `backend/` directory:
```env
# Size limit for PDF and image uploads in MB
MAX_FILE_SIZE_MB=50

# How long files should be retained before cleanup (in minutes)
TEMP_FILE_LIFETIME_MINUTES=30

# The production URL of the frontend (for CORS restrictions)
FRONTEND_URL=https://pdfsin5.com
```

### Frontend Environment (`frontend/.env.production`)
Create a `.env.production` file in the `frontend/` directory:
```env
# The production URL of your backend API
VITE_API_URL=https://api.pdfsin5.com
```

---

## 2. Frontend Deployment (React + Vite)

The frontend should be bundled into static files and served by a high-performance web server like Nginx or deployed directly to Vercel/Netlify.

### Build the Application
1. Navigate to the `frontend/` directory.
2. Run `npm install` to ensure dependencies are up-to-date.
3. Run `npm run build` to generate the static files.
4. The production-ready files will be output to `frontend/dist`.

### Nginx Configuration (Example)
To serve the frontend via Nginx and ensure React Router (`/tool/merge-pdf`, `/blog`) works correctly:
```nginx
server {
    listen 80;
    server_name pdfsin5.com www.pdfsin5.com;
    root /path/to/PDFsIn5/frontend/dist;
    index index.html;

    # Enable Gzip Compression for Performance
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    location / {
        # Fallback to index.html for React Router
        try_files $uri $uri/ /index.html;
    }

    # HTTP Caching for static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|svg|ico|webp)$ {
        expires 1y;
        add_header Cache-Control "public, max-age=31536000, immutable";
    }
}
```

---

## 3. Backend Deployment (FastAPI + Gunicorn)

The FastAPI backend should be run using `gunicorn` with `UvicornWorker` classes for robust handling of asynchronous requests.

### Setup
1. Navigate to the `backend/` directory.
2. Ensure you have installed standard dependencies from `requirements.txt` and the server bindings:
   `pip install gunicorn uvicorn`

### Running the Server
Run Gunicorn on your production port (e.g., 8000). You can run this inside a `systemd` service or a `tmux` session.

```bash
gunicorn -k uvicorn.workers.UvicornWorker --workers 4 --timeout 120 --bind 127.0.0.1:8000 app.main:app
```
*Note: Adjust `--workers` based on your server's CPU cores (typically `(2 x $num_cores) + 1`).*

### Render Deployment
If you are deploying the backend using Render (Web Service), you need to make sure Ghostscript is installed in the environment for tools like Compress PDF.
Create a custom build script (e.g. `render-build.sh`) and configure Render to use it for the Build Command (`./render-build.sh`):

```bash
#!/usr/bin/env bash
# Update and install ghostscript and tesseract-ocr
apt-get update
apt-get install -y ghostscript tesseract-ocr

# Install python dependencies
pip install -r backend/requirements.txt
```

### Reverse Proxy Configuration (Example Nginx setup for API)
Expose the Gunicorn server safely to the web on your subdomain (`api.pdfsin5.com`):

```nginx
server {
    listen 80;
    server_name api.pdfsin5.com;

    # Important: Allow Large Uploads! (50MB) 
    client_max_body_size 55M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_addrs;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 4. Maintenance & Cleanup Ensurement
The background cleanup task is automatically initialized with FastAPI through the `lifespan` event hook. It will routinely poll and safely delete orphaned byte files in `uploads/` and `outputs/`. The duration can be adjusted using `TEMP_FILE_LIFETIME_MINUTES` in the `.env` settings.
