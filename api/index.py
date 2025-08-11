from flask import Flask, render_template, request, jsonify, redirect, url_for, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import json
import os
import glob
from pathlib import Path

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://postgres.raxegckgsveacgflvwbd:wdsjkdmmhaq@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
}

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database Models
class User(db.Model, UserMixin):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    premium_status = db.Column(db.String(20), default='none')  # none, basic, premium, max
    premium_expires_at = db.Column(db.DateTime, nullable=True)
    selected_sector = db.Column(db.String(10), nullable=True)  # 'TMT' or 'Energy'
    sector_changed_at = db.Column(db.DateTime, nullable=True)  # Track when sector was last changed
    
    @property
    def has_valid_premium(self):
        """Check if user has valid premium access (basic/premium/max and not expired)"""
        if self.premium_status == 'none':
            return False
        if not self.premium_expires_at:
            return True  # Legacy users without expiration date
        return self.premium_expires_at > datetime.utcnow()
    
    @property
    def has_view_access(self):
        """Check if user has access to view reports (premium/max only, not basic)"""
        if self.premium_status in ['premium', 'max']:
            if not self.premium_expires_at:
                return True  # Legacy users without expiration date
            return self.premium_expires_at > datetime.utcnow()
        return False
    
    @property
    def needs_sector_selection(self):
        """Check if basic user needs to select a sector"""
        return self.premium_status == 'basic' and self.selected_sector is None
    
    @property
    def can_change_sector(self):
        """Check if basic user can change their sector (once per week)"""
        if self.premium_status != 'basic' or not self.sector_changed_at:
            return True  # Premium users or first-time selection
        # Check if a week has passed since last change
        week_ago = datetime.utcnow() - timedelta(days=7)
        return self.sector_changed_at < week_ago

# Only User table is needed - other tables removed

def get_available_reports():
    """
    Dynamically scan the briefs folder and return all available reports
    
    Expected filename format: Sector_Brief_YYYY-MM-DD.pdf
    Examples:
    - TMT_Brief_2025-08-04.pdf
    - Healthcare_Brief_2025-08-04.pdf
    - Energy_Brief_2025-08-04.pdf
    
    Files that don't follow this convention will be treated as 'General' sector reports.
    """
    reports = []
    briefs_folder = Path('static/assets/briefs')
    
    if briefs_folder.exists():
        # Get all PDF files in the briefs folder
        pdf_files = glob.glob(str(briefs_folder / '*.pdf'))
        
        for pdf_file in pdf_files:  # Don't sort here, we'll sort by date later
            filename = Path(pdf_file).name
            
            # Parse filename to extract sector and date
            # Expected format: Sector_Brief_YYYY-MM-DD.pdf
            try:
                # Remove .pdf extension
                name_without_ext = filename.replace('.pdf', '')
                
                # Split by underscore
                parts = name_without_ext.split('_')
                
                if len(parts) >= 3 and parts[1] == 'Brief':
                    sector = parts[0]
                    date_str = parts[2]
                    
                    # Create a more readable title
                    title = f"{sector} Brief - {date_str}"
                    
                    # Generate a unique ID based on filename
                    report_id = len(reports) + 1
                    
                    reports.append({
                        'id': report_id,
                        'title': title,
                        'date': date_str,
                        'sector': sector,
                        'filename': filename,
                        'summary': f'Latest {sector} sector analysis and market insights.',
                        'status': 'available'
                    })
                else:
                    # Handle files that don't follow the expected naming convention
                    title = filename.replace('.pdf', '').replace('_', ' ')
                    report_id = len(reports) + 1
                    
                    reports.append({
                        'id': report_id,
                        'title': title,
                        'date': '2025-01-01',  # Default date
                        'sector': 'General',
                        'filename': filename,
                        'summary': 'Market analysis and insights.',
                        'status': 'available'
                    })
                    
            except Exception as e:
                print(f"Error parsing filename {filename}: {e}")
                # Skip files that can't be parsed
                continue
        
        # Sort reports by date (newest first) and then by sector for consistent ordering
        reports.sort(key=lambda x: (x['date'], x['sector']), reverse=True)
        
        # Update IDs to be sequential after sorting
        for i, report in enumerate(reports, 1):
            report['id'] = i
    
    return reports

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@app.route('/')
def index():
    """Main landing page"""
    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard page"""
    return render_template('dashboard.html')

@app.route('/features')
def features():
    """Features page"""
    return render_template('features.html')

@app.route('/pricing')
def pricing():
    """Pricing page"""
    return render_template('pricing.html')

@app.route('/reports')
@login_required
def reports():
    """Reports page"""
    return render_template('reports.html')

@app.route('/sample')
def sample():
    """Sample report page"""
    return render_template('sample.html')

@app.route('/client')
def client():
    """Client index page"""
    return render_template('client_index.html')

# API Routes
@app.route('/api/login', methods=['GET', 'POST'])
def login():
    """Login endpoint"""
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')  # Accept any username, not just email
        password = data.get('password')
        
        try:
            user = User.query.filter_by(username=username).first()
            
            if user and user.password == password:  # Assuming password is stored as plain text or hashed
                login_user(user)
                return jsonify({'success': True, 'redirect': '/dashboard'})
            else:
                return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
        except Exception as e:
            print(f"Login error: {e}")
            return jsonify({'success': False, 'error': 'Database error'}), 500
    
    # GET request - show login form
    return render_template('login.html')

@app.route('/api/logout')
def logout():
    """Logout endpoint"""
    logout_user()
    return jsonify({'success': True, 'redirect': '/'})

@app.route('/api/auth/user')
def get_user():
    """Get current user information"""
    if current_user.is_authenticated:
        return jsonify({
            'authenticated': True,
            'user': {
                'id': current_user.id,
                'username': current_user.username,
                'premium_status': current_user.premium_status,
                'has_valid_premium': current_user.has_valid_premium,
                'has_view_access': current_user.has_view_access,
                'selected_sector': current_user.selected_sector,
                'needs_sector_selection': current_user.needs_sector_selection,
                'can_change_sector': current_user.can_change_sector
            }
        })
    else:
        return jsonify({'authenticated': False}), 401

@app.route('/api/user/subscription')
@login_required
def get_user_subscription():
    """Get user subscription information"""
    if current_user.is_authenticated:
        subscription_data = {
            'planId': current_user.premium_status.capitalize() if current_user.premium_status != 'none' else 'No Plan',
            'status': 'Active' if current_user.has_valid_premium else 'Inactive',
            'expires_at': current_user.premium_expires_at.strftime('%Y-%m-%d') if current_user.premium_expires_at else None,
            'has_valid_premium': current_user.has_valid_premium,
            'has_view_access': current_user.has_view_access,
            'selected_sector': current_user.selected_sector
        }
        return jsonify(subscription_data)
    else:
        return jsonify({'error': 'Unauthorized'}), 401

@app.route('/api/reports')
def get_reports():
    """Get available reports - dynamically scanned from briefs folder"""
    if not current_user.is_authenticated:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Get all available reports dynamically
    actual_reports = get_available_reports()
    
    # Filter based on user access
    if current_user.has_view_access:
        reports_data = actual_reports
    elif current_user.has_valid_premium and current_user.selected_sector:
        reports_data = [r for r in actual_reports if r['sector'] == current_user.selected_sector]
    else:
        return jsonify({'error': 'No access to reports'}), 403
    
    return jsonify({
        'reports': reports_data,
        'total': len(reports_data),
        'user': {
            'username': current_user.username,
            'premium_status': current_user.premium_status,
            'selected_sector': current_user.selected_sector,
            'has_view_access': current_user.has_view_access
        }
    })

@app.route('/api/reports/<int:report_id>')
def get_report(report_id):
    """Get specific report details - dynamically scanned"""
    if not current_user.is_authenticated:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Get all available reports dynamically
    actual_reports = get_available_reports()
    
    # Find the report by ID
    report = next((r for r in actual_reports if r['id'] == report_id), None)
    
    if report:
        # Add content field for compatibility
        report['content'] = f'Detailed analysis of {report["sector"]} sector with comprehensive market insights and trends.'
        return jsonify(report)
    else:
        return jsonify({'error': 'Report not found'}), 404

@app.route('/api/dashboard/stats')
def get_dashboard_stats():
    """Get dashboard statistics"""
    if not current_user.is_authenticated:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Get all available reports dynamically
    all_reports = get_available_reports()
    
    # Calculate reports available based on user access
    if current_user.has_view_access:
        reports_available = len(all_reports)  # All reports available
    elif current_user.has_valid_premium and current_user.selected_sector:
        # Count reports for the user's selected sector
        sector_reports = [r for r in all_reports if r['sector'] == current_user.selected_sector]
        reports_available = len(sector_reports)
    else:
        reports_available = 0
    
    return jsonify({
        'premium_status': current_user.premium_status,
        'has_valid_premium': current_user.has_valid_premium,
        'has_view_access': current_user.has_view_access,
        'selected_sector': current_user.selected_sector,
        'needs_sector_selection': current_user.needs_sector_selection,
        'can_change_sector': current_user.can_change_sector,
        'reports_available': reports_available,
        'premium_expires_at': current_user.premium_expires_at.strftime('%Y-%m-%d') if current_user.premium_expires_at else None
    })

@app.route('/api/dashboard/all')
def get_dashboard_all():
    """Get all dashboard data in a single call - optimized for performance"""
    if not current_user.is_authenticated:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Get all available reports dynamically
    all_reports = get_available_reports()
    
    # Calculate reports available based on user access
    if current_user.has_view_access:
        reports_available = len(all_reports)  # All reports available
    elif current_user.has_valid_premium and current_user.selected_sector:
        # Count reports for the user's selected sector
        sector_reports = [r for r in all_reports if r['sector'] == current_user.selected_sector]
        reports_available = len(sector_reports)
    else:
        reports_available = 0
    
    # Get user data
    user_data = {
        'id': current_user.id,
        'username': current_user.username,
        'premium_status': current_user.premium_status,
        'has_valid_premium': current_user.has_valid_premium,
        'has_view_access': current_user.has_view_access,
        'selected_sector': current_user.selected_sector,
        'needs_sector_selection': current_user.needs_sector_selection,
        'can_change_sector': current_user.can_change_sector,
        'reports_available': reports_available,
        'premium_expires_at': current_user.premium_expires_at.strftime('%Y-%m-%d') if current_user.premium_expires_at else None
    }
    
    # Filter reports based on user access
    if current_user.has_view_access:
        reports_data = all_reports
    elif current_user.has_valid_premium and current_user.selected_sector:
        reports_data = [r for r in all_reports if r['sector'] == current_user.selected_sector]
    else:
        reports_data = []
    
    return jsonify({
        'user': user_data,
        'stats': user_data,  # Same data for compatibility
        'reports': {
            'reports': reports_data,
            'total': len(reports_data),
            'user': {
                'username': current_user.username,
                'premium_status': current_user.premium_status,
                'selected_sector': current_user.selected_sector,
                'has_view_access': current_user.has_view_access
            }
        }
    })

@app.route('/api/register', methods=['POST'])
def register():
    """User registration endpoint"""
    data = request.get_json()
    username = data.get('username')  # Accept any username, not just email
    password = data.get('password')
    name = data.get('name')
    
    if not username or not password or not name:
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400
    
    try:
        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return jsonify({'success': False, 'error': 'Username already registered'}), 400
        
        # Create new user with 7-day premium trial
        user = User(
            username=username, 
            password=password,
            premium_status='premium',
            premium_expires_at=datetime.utcnow() + timedelta(days=7)
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Log in the new user
        login_user(user)
        
        return jsonify({'success': True, 'redirect': '/dashboard'})
    except Exception as e:
        db.session.rollback()
        print(f"Registration error: {e}")
        return jsonify({'success': False, 'error': 'Database error'}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

# Create additional template pages if they don't exist
@app.route('/login')
def login_page():
    """Login page"""
    return render_template('login.html')

@app.route('/register')
def register_page():
    """Register page"""
    return render_template('register.html')

# Additional API endpoints for sector selection and premium management
@app.route('/api/sector/select', methods=['POST'])
@login_required
def select_sector():
    """Select sector for basic users"""
    if not current_user.has_valid_premium:
        return jsonify({'error': 'No premium access'}), 403
    
    if not current_user.can_change_sector:
        return jsonify({'error': 'Cannot change sector yet'}), 403
    
    data = request.get_json()
    sector = data.get('sector')
    
    if sector not in ['TMT', 'Energy']:
        return jsonify({'error': 'Invalid sector'}), 400
    
    try:
        current_user.selected_sector = sector
        current_user.sector_changed_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'success': True, 'sector': sector})
    except Exception as e:
        db.session.rollback()
        print(f"Sector selection error: {e}")
        return jsonify({'error': 'Database error'}), 500

@app.route('/api/premium/upgrade', methods=['POST'])
@login_required
def upgrade_premium():
    """Upgrade user premium status"""
    data = request.get_json()
    premium_type = data.get('premium_type')  # 'basic', 'premium', 'max'
    
    if premium_type not in ['basic', 'premium', 'max']:
        return jsonify({'error': 'Invalid premium type'}), 400
    
    try:
        current_user.premium_status = premium_type
        # Set expiration date (e.g., 30 days from now)
        current_user.premium_expires_at = datetime.utcnow() + timedelta(days=30)
        db.session.commit()
        
        return jsonify({'success': True, 'premium_status': premium_type})
    except Exception as e:
        db.session.rollback()
        print(f"Premium upgrade error: {e}")
        return jsonify({'error': 'Database error'}), 500

# Static file routes for reports
@app.route('/static/assets/exhibit/<filename>')
def serve_sample_report(filename):
    """Serve sample report files"""
    return send_from_directory('static/assets/exhibit', filename)

@app.route('/static/assets/briefs/<filename>')
@login_required
def serve_brief_report(filename):
    """Serve brief report files - requires authentication"""
    return send_from_directory('static/assets/briefs', filename)

@app.route('/api/debug/reports')
def debug_reports():
    """Debug endpoint to see what reports are detected"""
    if not current_user.is_authenticated:
        return jsonify({'error': 'Unauthorized'}), 401
    
    reports = get_available_reports()
    
    # Group reports by sector for easier viewing
    sector_counts = {}
    for report in reports:
        sector = report['sector']
        if sector not in sector_counts:
            sector_counts[sector] = 0
        sector_counts[sector] += 1
    
    return jsonify({
        'total_reports': len(reports),
        'reports': reports,
        'sector_counts': sector_counts,
        'user_access': {
            'has_view_access': current_user.has_view_access,
            'has_valid_premium': current_user.has_valid_premium,
            'selected_sector': current_user.selected_sector,
            'premium_status': current_user.premium_status
        }
    })

# Database initialization
def init_db():
    """Initialize the database with only User table"""
    with app.app_context():
        # Create only the User table
        db.create_all()
        print("Database initialized - only User table created")
        print("Using existing users from your database")

if __name__ == '__main__':
    # Initialize database
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
