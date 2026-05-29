# ESG Ops Console (Ingestion & Review)

Prototype ESG ingestion and analyst review platform built for enterprise sustainability workflows.

The platform ingests ESG-related operational data from SAP exports, utility electricity reports, and corporate travel systems, normalizes the records, flags suspicious entries, and enables analyst review with immutable audit tracking.


## Quick overview
- Backend: Django REST API serving under `http://127.0.0.1:8000` by default.
- Frontend: Vite + React running on `http://localhost:5173` during development.

## Tech Stack

### Backend

* Django
* Django REST Framework
* SQLite
* django-cors-headers

### Frontend

* React
* Vite
* TailwindCSS
* Axios
* React Router


## Backend — local setup
1. Create and activate a virtualenv (Windows PowerShell):

```
python -m venv .venv
(Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned) ; (& .venv\Scripts\Activate.ps1)
```

2. Install dependencies (if you have a `requirements.txt`):

```
python -m pip install -r requirements.txt
```

If you don't have a `requirements.txt`, install core packages:

```
python -m pip install django djangorestframework django-cors-headers
```

3. Apply migrations and (optionally) create a superuser:

```
python manage.py migrate
python manage.py createsuperuser
```

4. Seed demo data (provided management command):

```
python manage.py seed_demo_data
```

5. Run the development server:

```
python manage.py runserver
```

## Frontend — local setup
1. From the `frontend` folder install node deps and run dev server:

```
cd frontend
npm install
npm run dev
```

The frontend uses `VITE_API_BASE_URL` (defaults to `http://127.0.0.1:8000`).

## CORS and tenant header (development)
- This project uses `django-cors-headers` to allow the React dev client to talk to the API.
- The backend CORS config explicitly allows `http://localhost:5173` and `http://127.0.0.1:5173`, and permits the custom header `X-Tenant` so Axios requests with that header pass preflight.
- Relevant file: [backend/config/settings.py](backend/config/settings.py#L1-L140)

If you need to install the package manually in your venv:

```
python -m pip install django-cors-headers
```

## How the tenant header is sent
- The React client sets an `X-Tenant` header on requests. The frontend stores the tenant in localStorage under the key `esg.tenant` and the Axios client attaches it automatically.
- UI: change the Tenant input in the app to switch tenant context.

## Notes
- `DEBUG` is `True` in the provided settings for development. Lock down secrets, CORS, and `ALLOWED_HOSTS` for production.
- The tenant lookup middleware is minimal and expects the `X-Tenant` header; CORS is configured so `OPTIONS` preflight requests succeed before tenant logic runs.

## Troubleshooting
- If browser blocks requests with CORS errors, confirm the frontend is served from `http://localhost:5173` and the backend is running at `http://127.0.0.1:8000`.
- Confirm `X-Tenant` is being sent (browser devtools → Network → request headers) and that the backend's `CORS_ALLOW_HEADERS` includes `x-tenant` (case-insensitive).

## Features

* Multi-source ESG data ingestion
* SAP CSV normalization
* Utility electricity ingestion
* Corporate travel data ingestion
* Suspicious record detection
* Analyst approval/rejection workflow
* Immutable audit logging
* Multi-tenant support using tenant headers
* React analyst dashboard
* Review filtering and pagination

## Sample Data

Sample ingestion files are available under:

```text
backend/sample_data/
```

The sample datasets intentionally contain:

* mixed date formats
* German SAP headers
* missing fields
* suspicious outlier values
* airport codes
* non-calendar utility billing periods

to simulate realistic enterprise ingestion scenarios.

## Deployment

Frontend: Vercel  
Backend: Railway