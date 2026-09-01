# SF Self-Storage Manifest

A local dashboard that scrapes self-storage facility data in San Francisco
using Geoapify's Places API, displays it on an interactive Leaflet map, and
lets you pin custom locations that are saved permanently in a local SQLite
database.

## Project structure

```
sf-storage-dashboard/
├── app.py                  # Flask server: serves the dashboard + pin API (SQLite)
├── fetch_data.py            # Scrapes storage facilities via Geoapify Places API
├── data/
│   └── storage_units.json      # Generated output (created after running fetch_data.py)
├── index.html                # The dashboard (Leaflet map + sidebar list + pin mode)
├── pins.db                   # SQLite database of your pinned locations (auto-created, gitignored)
├── requirements.txt
└── README.md
```

## Setup

### 1. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 2. Get a free Geoapify API key

Sign up at https://myprojects.geoapify.com/ (email only, no billing card),
create a project, and copy the API key it generates.

### 3. Set your API key and run the scraper

```bash
$env:GEOAPIFY_API_KEY="your_key_here"   # PowerShell
python fetch_data.py
```

This writes the results to `data/storage_units.json`.

### 4. Start the server

```bash
python app.py
```

This replaces the old `python -m http.server` command — `app.py` now
serves the dashboard **and** the pin database API. Then open
**http://localhost:8000**.

## Pinning locations

Click the **"📍 Pin Mode"** button in the top-right of the map to turn it on,
then click anywhere on the map to drop a pin with a label and optional note.
Pins are saved permanently to `pins.db` (a local SQLite file) via a small
Flask REST API (`/api/pins`), so they persist across restarts and page
refreshes. Click a pin's marker to view its details or delete it.

## How the data is sourced

- **Map tiles**: plain OpenStreetMap tiles (free, no key), with a CSS filter
  applied to fake a dark theme.
- **Facility data**: Geoapify Places API (free tier, 3,000 requests/day),
  which itself sources from OpenStreetMap. This is a **snapshot**, not
  live/real-time — re-run `fetch_data.py` periodically to refresh it.
- **Pinned locations**: stored locally in SQLite via the Flask backend in
  `app.py`. This part *is* live and persists automatically.
- **Map library**: [Leaflet.js](https://leafletjs.com/), loaded from a CDN.

## Notes

- `pins.db` is gitignored — your pinned locations stay local to your machine
  and won't be pushed to GitHub. If you want to share pins across machines,
  the database would need to move to a hosted service instead of a local file.
- Re-run `fetch_data.py` any time to refresh the storage facility data.