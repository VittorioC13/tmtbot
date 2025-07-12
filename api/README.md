# Flask Server

This is a Flask server that serves HTML templates from the `templates` folder.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Server

1. Navigate to the api directory:
```bash
cd api
```

2. Run the Flask server:
```bash
python index.py
```

The server will start on `http://localhost:5000`

## Available Routes

- `/` - Main webpage (serves webpage.html)
- `/health` - Health check endpoint
- Error handlers for 404 and 500 errors

## Configuration

- The server runs in debug mode by default
- Host: 0.0.0.0 (accessible from any IP)
- Port: 5000
- Secret key should be changed in production

## Templates

The server serves HTML files from the `templates` folder. Currently includes:
- `webpage.html` - Main webpage template 