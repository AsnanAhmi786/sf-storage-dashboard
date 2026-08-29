# SF Self-Storage Manifest

A local dashboard that scrapes self-storage facility data in San Francisco
using OpenStreetMap's Overpass API, then displays it on an interactive
Leaflet map. **No API keys, accounts, or billing required anywhere.**

> Note: this project originally targeted the Google Places/Maps APIs per the
> assignment brief, but switched to OpenStreetMap + Leaflet after Google Cloud
> billing verification and Yelp's signup flow were both unavailable. The data
> source can be swapped back to Google later — see "Swapping back to Google
> Maps" below.

## Project structure

```
sf-storage-dashboard/
├── fetch_data.py          # Scrapes storage facilities via OSM Overpass API
├── data/
│   └── storage_units.json    # Generated output (created after running fetch_data.py)
├── index.html              # The dashboard (Leaflet map + sidebar list)
├── requirements.txt
└── README.md
```

## Setup

### 1. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the scraper

```bash
python fetch_data.py
```

This queries the Overpass API for anything tagged `shop=storage_rental` or
named like "storage" within San Francisco's bounding box, and writes the
results to `data/storage_units.json`. No key or signup needed — Overpass is
a public endpoint.

### 3. Serve and open the dashboard

Because the page fetches a local JSON file, you need to serve it over HTTP
(opening `index.html` directly via `file://` will be blocked by the browser).
From the project folder, run:

```bash
python -m http.server 8000
```

Then open **http://localhost:8000** in your browser.

## How the data is sourced

- **Map tiles**: CartoDB's free "Dark Matter" tiles (built on OpenStreetMap
  data), no key required.
- **Facility data**: OpenStreetMap, queried via the public Overpass API.
  Coverage is community-sourced, so it may be less complete than Google's
  or Yelp's business listings, especially for phone numbers/hours.
- **Map library**: [Leaflet.js](https://leafletjs.com/), loaded from a CDN.

## Swapping back to Google Maps later

If your Google Cloud billing clears up, swapping back is straightforward:

1. Restore a Places API-based `fetch_data.py` (Text Search + Place Details)
   to get richer data (ratings, review counts, business hours, phone).
2. Replace the Leaflet `L.map`/`L.tileLayer`/`L.marker` calls in `index.html`
   with the Google Maps JavaScript API equivalents (`google.maps.Map`,
   `google.maps.Marker`).
3. The `data/storage_units.json` schema is intentionally similar between
   both approaches, so most of the sidebar/list rendering code won't need
   to change.

## Notes

- Re-run `fetch_data.py` any time to refresh the data.
- Overpass's public instance is a shared community resource — please don't
  hammer it with rapid repeated requests.
