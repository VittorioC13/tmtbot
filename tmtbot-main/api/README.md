# TMT Bot Flask Application

A comprehensive Flask web application for TMT Bot, providing market intelligence and analysis services for TMT, Healthcare, and Energy sectors.

## Features

- **Landing Page**: Modern, responsive homepage with feature showcase
- **User Authentication**: Login and registration system
- **Dashboard**: User dashboard with subscription status and reports
- **Reports**: Access to market intelligence reports
- **Features & Pricing**: Detailed feature and pricing pages
- **Sample Reports**: Preview of available market analysis
- **Error Handling**: Custom 404 and 500 error pages

## Installation

1. **Clone the repository** (if applicable)
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

1. **Start the Flask server**:
   ```bash
   python index.py
   ```

2. **Access the application**:
   - Open your browser and go to `http://localhost:5000`
   - The application will be available on all network interfaces

## Available Routes

### Main Pages
- `/` - Landing page
- `/dashboard` - User dashboard (requires login)
- `/features` - Features page
- `/pricing` - Pricing page
- `/reports` - Reports page (requires login)
- `/sample` - Sample report page
- `/client` - Client index page

### Authentication
- `/login` - Login page
- `/register` - Registration page
- `/api/login` - Login API endpoint
- `/api/register` - Registration API endpoint
- `/api/logout` - Logout API endpoint

### API Endpoints
- `/api/auth/user` - Get current user information
- `/api/reports` - Get available reports (filtered by user access)
- `/api/reports/<id>` - Get specific report
- `/api/dashboard/stats` - Get dashboard statistics
- `/api/sector/select` - Select sector for basic users
- `/api/premium/upgrade` - Upgrade user premium status

## Demo Features

The application includes demo functionality:
- **Demo Login**: Use `demo@example.com` / `demo123` for premium access
- **Basic Login**: Use `basic@example.com` / `basic123` for basic access
- **Demo Registration**: Quick registration with demo data
- **Sample Data**: Pre-populated with sample reports and user data
- **Sector Selection**: Basic users can select TMT or Energy sector
- **Premium Management**: Upgrade user premium status via API

## Project Structure

```
NewPageDesign/
├── index.py              # Main Flask application
├── requirements.txt      # Python dependencies
├── README.md            # This file
└── templates/           # HTML templates
    ├── index.html       # Landing page
    ├── dashboard.html   # User dashboard
    ├── features.html    # Features page
    ├── pricing.html     # Pricing page
    ├── reports.html     # Reports page
    ├── sample.html      # Sample report page
    ├── client_index.html # Client page
    ├── login.html       # Login page
    ├── register.html    # Registration page
    ├── 404.html         # 404 error page
    └── 500.html         # 500 error page
```

## Design Features

- **Responsive Design**: Works on desktop, tablet, and mobile
- **Modern UI**: Clean, professional design with Tailwind CSS
- **Consistent Branding**: TMT Bot color scheme and styling
- **Interactive Elements**: Hover effects and smooth transitions
- **Accessibility**: Proper semantic HTML and ARIA labels

## Security Notes

- The application uses session-based authentication
- In production, implement proper password hashing and database storage
- Change the secret key in `index.py` for production use
- Add CSRF protection and input validation for production

## Development

To run in development mode with auto-reload:
```bash
python index.py
```

The application will start in debug mode with auto-reload enabled.

## License

This project is for demonstration purposes. Please ensure proper licensing for production use. 