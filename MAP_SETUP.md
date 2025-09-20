# Map Feature Setup

## Overview
The map feature displays an interactive Google Map showing NYC investment banks with their locations, details, and highlighting functionality.

## Setup Requirements

### 1. Google Maps API Key
You need to set up a Google Maps API key in your environment variables:

```bash
export GOOGLE_MAP_API="your_google_maps_api_key_here"
```

Or add it to your `.env` file:
```
GOOGLE_MAP_API=your_google_maps_api_key_here
```

### 2. API Key Setup Steps
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the "Maps JavaScript API"
4. Create credentials (API Key)
5. Restrict the API key to your domain for security
6. Add the API key to your environment variables

### 3. Features
- **Interactive Map**: Shows all NYC investment banks from `nyc_banks.json`
- **Sidebar Navigation**: Click on bank names to highlight them on the map
- **Bank Details**: Hover over markers to see bank information
- **Responsive Design**: Works on desktop and mobile devices

### 4. Access
Navigate to `/map` in your application to access the map feature.

### 5. Data Source
The map uses data from `api/static/data/nyc_banks.json` which contains:
- Bank names and locations (lat/lng coordinates)
- Address information
- Employee count, revenue, and assets
- Website links
- Bank tier classification

## Troubleshooting
- If the map doesn't load, check that your Google Maps API key is correctly set
- Ensure the Maps JavaScript API is enabled in your Google Cloud project
- Check browser console for any JavaScript errors
