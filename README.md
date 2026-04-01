# Network Performance Tracker - FastAPI Backend

FastAPI backend that reads Google Sheet data from a **public CSV URL** and exposes issues via `GET /issues`.
Issue status updates are stored in PostgreSQL and protected with JWT authentication.
It also sends an automated daily analytics email report using APScheduler, with a PDF attachment and chart.
No Google service account is required for this flow.

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

- `GET /issues`: Fetches latest CSV rows in real time, skips empty rows and bad rows, merges stored PostgreSQL status, and returns structured JSON.
- `GET /dashboard`: Returns aggregated analytics computed dynamically from merged issue data.
- `GET /status-workflow`: Returns allowed statuses, transition matrix, and field validation rules.
- `POST /sync-complaints`: Pulls current sheet rows and inserts only new complaints into PostgreSQL (dedupe-safe).
- `GET /admin/export?from_date=YYYY-MM-DD&to_date=YYYY-MM-DD`: Downloads one Excel file for ACKNOWLEDGED/RESOLVED complaints in the selected range (max last 30 days).
- `POST /login`: Returns JWT access token.
- `PUT /issues/{row_index}/status`: Updates complaint status with transition validation and ICT metadata (Bearer token required).
- `PUT /update-status/{row_index}`: Backward-compatible alias for the same status update workflow.
- `GET /health`: Health check.

## Docker Deployment

1. Copy `.env.example` to `.env` and fill values.
2. Build and run:

```bash
docker compose up --build -d
```

PostgreSQL is persisted in a named Docker volume (`postgres_data`) mounted at `/var/lib/postgresql/data`.
Persisted `complaints` records include `created_at` and `updated_at` timestamps for date/time persistence.

3. Access:
   - Frontend: `http://localhost:8080`
   - Backend API: `http://localhost:8000`

4. Stop:

```bash
docker compose down
```

## PostgreSQL Connection

Set database URL in `.env` for non-Docker runs:

```text
DATABASE_URL=postgresql+psycopg2://npt_user:npt_password@localhost:5432/npt_db
```

`DATABASE_URL` is required and must be a PostgreSQL SQLAlchemy URL.

## Migrate Existing SQLite Data to PostgreSQL

1. Ensure PostgreSQL is running and `TARGET_DATABASE_URL` is set:

```bash
set TARGET_DATABASE_URL=postgresql+psycopg2://npt_user:npt_password@localhost:5432/npt_db
```

2. Optionally point to a specific SQLite file (defaults to `issues.db`):

```bash
set SOURCE_SQLITE_DB_PATH=issues.db
```

3. Run migration:

```bash
python scripts/migrate_sqlite_to_postgres.py
```

Compatibility notes:
- Existing table names are preserved: `users`, `issue_status`.
- Existing columns are preserved: `users(id, username, password_hash, role)`, `issue_status(id, row_index, status)`.
- New timestamp columns are auto-added when missing: `issue_status.created_at`, `issue_status.updated_at`.
- Archive table used by retention cleanup: `archived_complaints`.

## Complaint Sync Design

The sheet can reset daily, so row numbers are not treated as persistent IDs.

Persistence strategy:
- Complaints are stored in `complaints` table.
- Every complaint gets a deterministic `complaint_key` (SHA-256 hash) from:
  `timestamp + email + location + issue_type + description + cluster_key`.
- `complaint_key` is `UNIQUE`, so duplicates are ignored.

Sync behavior:
- Sync reads sheet rows.
- Inserts only rows with new `complaint_key`.
- Existing rows are never overwritten by sheet data.
- Status history (`NOT RESOLVED`/`ACKNOWLEDGED`/`RESOLVED`) persists in DB even after sheet reset.
- Sync runs at app startup and can be triggered manually via `POST /sync-complaints`.

## Admin Excel Export

- Available from admin UI via **Download Resolved Issues**.
- Date range supports single-day export (`from_date == to_date`).
- Only the last 30 days are allowed.
- Export includes only `ACKNOWLEDGED` and `RESOLVED` complaints.

Columns:
- Complaint ID
- Title / Description
- Location (Floor, Room, SSID)
- User Email
- Status
- Resolution Note
- Resolved By (ICT Name)
- Created At
- Resolved At

## Data Retention

- Runs once daily via APScheduler.
- Deletes complaints older than `RETENTION_DAYS` from main `complaints` table.
- Deletes only status: `RESOLVED`.
- `NOT RESOLVED` and `ACKNOWLEDGED` complaints are never deleted by retention job.
- When `ARCHIVE_BEFORE_DELETE=true`, records are copied to `archived_complaints` before deletion.
- Configs: `RETENTION_DAYS`, `RETENTION_CLEANUP_HOUR`, `RETENTION_CLEANUP_MINUTE`, `ARCHIVE_BEFORE_DELETE`.

## Daily Email Report (6:00 PM)

- Runs in background scheduler (APScheduler), started automatically with FastAPI startup.
- Uses internal dashboard service logic directly (no HTTP self-calls).
- Sends summary email via SMTP (Gmail default: `smtp.gmail.com:587`).
- Generates a pie chart for status distribution and embeds it in a PDF report.

Summary includes:

- Total issues
- RESOLVED / ACKNOWLEDGED / NOT RESOLVED counts
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
    "status": "NOT RESOLVED",
    "ict_member_name": null,
    "resolution_remark": null,
    "acknowledged_at": null,
    "resolved_at": null
  }
]
```

## Update status payload

```json
{
  "status": "ACKNOWLEDGED",
  "ict_member_name": "ICT Member Name",
  "resolution_remark": "Ticket picked up and diagnostics started."
}
```

Allowed values:

- `NOT RESOLVED` (default)
- `ACKNOWLEDGED` (requires `ict_member_name`, `resolution_remark`)
- `RESOLVED` (requires `ict_member_name`, `resolution_remark` optional)

Validation:

- `ict_member_name` is required whenever status is updated.
- `resolution_remark` is mandatory only for `ACKNOWLEDGED`.

Status transitions:

- `NOT RESOLVED` -> `ACKNOWLEDGED`, `RESOLVED`
- `ACKNOWLEDGED` -> `RESOLVED`, `NOT RESOLVED`
- `RESOLVED` -> no further transitions

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
