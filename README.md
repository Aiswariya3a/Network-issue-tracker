# Network Performance Tracker - FastAPI Backend

FastAPI backend that reads Google Sheet data from a **public CSV URL** and exposes issues via `GET /issues`.
Issue status updates are stored locally in SQLite and protected with JWT authentication.
It also sends an automated daily analytics email report using APScheduler, with a PDF attachment and chart.

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and set:
   - `GOOGLE_SHEET_CSV_URL` (published CSV export link)
   - `JWT_SECRET_KEY` (change for production)
   - `EMAIL_SENDER`, `EMAIL_PASSWORD`, `EMAIL_RECEIVER` (for daily email report)

Example:

```text
https://docs.google.com/spreadsheets/d/<SHEET_ID>/export?format=csv
```

## Run

```bash
uvicorn main:app --reload
```

## Endpoints

- `GET /issues`: Fetches latest CSV rows in real time, skips empty rows and bad rows, merges local SQLite status, and returns structured JSON.
- `GET /dashboard`: Returns aggregated analytics computed dynamically from merged issue data.
- `POST /login`: Returns JWT access token.
- `PUT /update-status/{row_index}`: Updates local status for a specific sheet row (Bearer token required).
- `GET /health`: Health check.

## Docker Deployment

1. Copy `.env.example` to `.env` and fill values.
2. Build and run:

```bash
docker compose up --build -d
```

3. Access:
   - Frontend: `http://localhost:8080`
   - Backend API: `http://localhost:8000`

4. Stop:

```bash
docker compose down
```

## Daily Email Report (6:00 PM)

- Runs in background scheduler (APScheduler), started automatically with FastAPI startup.
- Uses internal dashboard service logic directly (no HTTP self-calls).
- Sends summary email via SMTP (Gmail default: `smtp.gmail.com:587`).
- Generates a pie chart for status distribution and embeds it in a PDF report.

Summary includes:

- Total issues
- Resolved / Not Resolved counts
- Resolution rate
- Top issue type
- Most affected location
- Issue type breakdown
- Status summary
- Top clusters

Attachments:

- `daily_report.pdf` (includes summary + insights + breakdown + status pie chart)
- Optional raw CSV if `ATTACH_RAW_CSV_REPORT=true`

### Test scheduler quickly

Set this in `.env`:

```text
REPORT_TEST_INTERVAL_MINUTES=1
```

This runs the job every minute for testing. Set it back to `0` for daily schedule.

## Expected columns

- `Timestamp`
- `Classroom / Location` (or `Location`)
- `Issue Type`
- `Time Slot`
- `Description`

## Output shape

```json
[
  {
    "row_index": 2,
    "timestamp": "...",
    "floor": "2F",
    "room": "301",
    "ssid": "KITE-I-YR-301",
    "location": "2F - 301 (KITE-I-YR-301)",
    "issue_type": "...",
    "time_slot": "...",
    "description": "...",
    "status": "Not Resolved"
  }
]
```

## Update status payload

```json
{
  "status": "Resolved"
}
```

Allowed values:

- `Resolved`
- `Not Resolved`

## Authentication

Default user created on startup:

- `username`: `ict_admin`
- `password`: `admin123`
- `role`: `ICT`

### Login request

```json
{
  "username": "ict_admin",
  "password": "admin123"
}
```

### Login response

```json
{
  "access_token": "<jwt_token>",
  "token_type": "bearer"
}
```

Use header for protected endpoint:

```text
Authorization: Bearer <jwt_token>
```
