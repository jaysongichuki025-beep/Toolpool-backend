# ToolPool Backend (`project-backend`)

Neighborhood tool-sharing API built with **Django REST Framework**, **JWT auth**, **PostgreSQL**, **Docker**, and **GitHub Actions**.

## What this repo does

- Register / login with JWT (`access` + `refresh` tokens)
- List tools with photos, categories, availability calendar data
- Borrowers request rentals; lenders approve/decline
- Admins manage categories and monitor rentals/disputes

## Quick start (beginner)

### Option A — Docker (recommended)

```bash
# 1. Copy env template
cp .env.example .env

# 2. Build & start Django + Postgres
docker compose up --build

# 3. In a NEW terminal — create an admin user
docker compose exec web python manage.py createsuperuser
```

API: http://localhost:8000/api/  
Admin: http://localhost:8000/admin/

### Option B — Local Python (SQLite, no Docker)

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
# Leave DATABASE_URL unset → uses SQLite
python manage.py migrate
python manage.py seed_categories
python manage.py createsuperuser
python manage.py runserver
```

## Main API routes

| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| POST | `/api/auth/register/` | Public | Create account |
| POST | `/api/auth/login/` | Public | Get JWT tokens |
| POST | `/api/auth/refresh/` | Public | Refresh access token |
| GET/PATCH | `/api/auth/me/` | JWT | Current user |
| GET/POST | `/api/categories/` | JWT / Admin | Categories |
| GET/POST | `/api/tools/` | JWT | Browse / list tools |
| PATCH | `/api/tools/{id}/status/` | Owner | Status toggle |
| GET | `/api/tools/{id}/availability/` | JWT | Blocked dates |
| GET/POST | `/api/rentals/` | JWT | Rental requests |
| PATCH | `/api/rentals/{id}/respond/` | Owner | Approve / decline |
| GET | `/api/admin/rentals/` | Admin | Transaction log |
| GET/POST | `/api/disputes/` | JWT / Admin | Disputes |

Login body example:

```json
{ "email": "you@example.com", "password": "yourpassword" }
```

## Database diagram

See [`docs/DB_DIAGRAM.md`](docs/DB_DIAGRAM.md) — paste the Mermaid into https://mermaid.live to export an image.

## Kanban tip

Create a GitHub Project board named **ToolPool MVP** with columns: Backlog → To Do → In Progress → Review → Done. Track backend cards (models, API, Docker, CI/CD) there.

## Deploy (Render)

1. Create a **Web Service** from this GitHub repo (Docker).
2. Add a **PostgreSQL** database on Render.
3. Set env vars: `SECRET_KEY`, `DEBUG=False`, `DATABASE_URL`, `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`.
4. Copy the Deploy Hook → GitHub secret `RENDER_DEPLOY_HOOK_URL`.

## Project structure

```
project-backend/
├── apps/users|tools|rentals   # models, serializers, views
├── config/                    # Django settings + root urls
├── docs/DB_DIAGRAM.md
├── Dockerfile
├── docker-compose.yml
└── .github/workflows/deploy.yml
```
