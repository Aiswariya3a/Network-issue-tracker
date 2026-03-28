# Network Issue Monitoring Frontend

React + Vite frontend for the FastAPI Network Issue Monitoring backend.

## Setup

1. Install dependencies:

```bash
npm install
```

2. (Optional) Create `.env`:

```bash
VITE_API_BASE_URL=http://localhost:8000
```

3. Run:

```bash
npm run dev
```

## Routes

- `/` Public dashboard
- `/login` Admin login
- `/admin` Protected status-management panel

## Features

- Real API integration (`/issues`, `/dashboard`, `/login`, `/update-status/{row_index}`)
- JWT token storage in `localStorage`
- Route protection for admin
- Auto-refresh dashboard every 30 seconds
- Responsive charts (status, issue type, location)
- Admin filters and per-row status updates
