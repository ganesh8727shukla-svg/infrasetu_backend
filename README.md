# InfraSetu Backend — FastAPI + PostgreSQL/PostGIS

This backend implements the API contract recovered from the InfraSetu frontend analysis.

## Scope

Implemented modules:
- Authentication: login, me, logout
- Assets + maintenance
- Complaints
- AI detections
- Risk + critical alerts
- Work orders and contractor transitions
- Contractors
- Dashboard analytics
- Audit trail
- File/image uploads
- Satellite records/history
- Notifications

The frontend report says the current UI uses `VITE_API_BASE_URL` (default `/api`) and sends `Authorization: Bearer <token>`. The API below therefore exposes the routes under `/api`.

## Important contract decisions

1. The frontend currently uses `PUT /work-orders/{id}` for three semantically different transitions:
   - `{ "status": "In Progress" }`
   - evidence fields (`beforeImage`, `afterImage`, `notes`)
   - verification fields (`verificationStatus`, `verificationConfidence`)
   This backend preserves that exact contract.

2. The report says upload storage/type/size details are "Needs clarification". This implementation uses configurable local storage for development:
   - `POST /api/uploads`
   - returned URL is `/media/<filename>`
   Production should replace local storage with object storage.

3. Refresh-token behavior is "Needs clarification" in the source report. This implementation uses short-lived access JWTs only. A refresh-token system can be added later without changing the main resource APIs.

4. AI is implemented as a deterministic development adapter, not a real computer-vision model. Replace `app/services/ai_service.py` with the actual AI service when ready.

5. Risk calculation is implemented as a deterministic development engine. Its inputs are limited to data available in this backend. It is intentionally replaceable.

6. The report says exact seed data should come from `src/data/mock.ts`, but that source file was not supplied with the backend report. No fabricated production seed is included.

## Run locally

### Option A — Docker

```bash
cp .env.example .env
docker compose up --build
```

API docs:
- http://localhost:8000/docs
- http://localhost:8000/redoc

### Option B — Local Python

Requirements:
- Python 3.12+
- PostgreSQL 16+
- PostGIS installed

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

## Environment

See `.env.example`.

## Frontend switch-over

The report states the frontend can switch from mock mode with configuration:

```env
VITE_USE_MOCK_DATA=false
VITE_API_BASE_URL=http://localhost:8000/api
```

Keep the existing frontend API layer unchanged.

## API contract

The main resource routes are:

```text
POST   /api/auth/login
GET    /api/auth/me
POST   /api/auth/logout

GET    /api/assets
GET    /api/assets/{id}
POST   /api/assets
PUT    /api/assets/{id}
GET    /api/assets/{id}/maintenance

GET    /api/complaints
GET    /api/complaints/{id}
POST   /api/complaints

POST   /api/ai/analyze
GET    /api/ai/detections/{asset_id}

GET    /api/risk/{asset_id}
GET    /api/risk/critical

GET    /api/work-orders
GET    /api/work-orders/{id}
POST   /api/work-orders
PUT    /api/work-orders/{id}

GET    /api/contractors
GET    /api/contractors/{id}

GET    /api/satellite/{asset_id}
GET    /api/satellite/{asset_id}/history

GET    /api/analytics/overview
GET    /api/analytics/health
GET    /api/analytics/risk
GET    /api/analytics/work-orders

GET    /api/audit
GET    /api/audit/{id}

POST   /api/uploads

GET    /api/notifications
PUT    /api/notifications/{id}
```

## Development order

1. Database/migrations
2. Auth
3. Assets/maintenance
4. Uploads
5. Complaint pipeline
6. AI/risk
7. Work orders
8. Contractors
9. Analytics
10. Audit
11. Satellite/notifications
12. Turn off frontend mock mode and run end-to-end validation
