from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
import stripe, requests
from stripe import SignatureVerificationError
import os
from datetime import datetime

# Stripe configuration
stripe.api_key = "sk_test_51Ri9SyFSHePhJarRDO1vrS4Ca8T8pRqsvkluFVE8sP4nc5qwiGal62fcWZAU9JeUbatWjzEZ6MQigXxOUvHwmXwJ00vr1eTfnk"
YOUR_DOMAIN = "http://127.0.0.1:5000"

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this to a secure secret key
# Use SQLite for local development, PostgreSQL for production
import os
database_url = os.environ.get('DATABASE_URL', 'sqlite:///instance/database.db')
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Initialize Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = None

# User model for authentication
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    is_paid = db.Column(db.Boolean, default=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Root route - serves the main webpage
@app.route('/')
def index():
    # Get the latest report for the main display
    reports = scan_assets_folder()
    latest_report = reports[0] if reports else None
    return render_template('webpage.html', latest_report=latest_report)

def scan_assets_folder():
    """Scan the static/assets folder for PDF reports and return them sorted by date"""
    if app.static_folder is None:
        return []
    
    assets_path = os.path.join(app.static_folder, 'assets')
    reports = []
    
    if os.path.exists(assets_path):
        for filename in os.listdir(assets_path):
            if filename.lower().endswith('.pdf'):
                # Extract date from filename
                # Handle different filename formats
                date_str = None
                if filename.startswith('TMT_Brief_'):
                    # Format: TMT_Brief_2025-07-02.pdf
                    date_str = filename.replace('TMT_Brief_', '').replace('.pdf', '')
                elif filename.startswith('brief_'):
                    # Format: brief_2024-01-11.pdf
                    date_str = filename.replace('brief_', '').replace('.pdf', '')
                
                if date_str:
                    try:
                        # Parse the date
                        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                        display_date = date_obj.strftime('%B %d, %Y')
                        
                        reports.append({
                            "title": "TMT Daily Brief",
                            "date": date_str,
                            "displayDate": display_date,
                            "filename": filename,
                            "isLatest": False  # Will be set below
                        })
                    except ValueError:
                        # Skip files that don't match expected date format
                        continue
    
    # Sort by date (newest first) and mark the latest
    reports.sort(key=lambda x: x['date'], reverse=True)
    if reports:
        reports[0]['isLatest'] = True
    
    return reports

# API route to get reports data
@app.route('/api/reports')
def get_reports():
    reports = scan_assets_folder()
    return jsonify(reports)

# Search API route
@app.route('/api/search')
def search_reports():
    query = request.args.get('q', '').lower()
    show_latest = request.args.get('latest', 'true').lower() == 'true'
    show_archive = request.args.get('archive', 'true').lower() == 'true'
    
    # Get all reports from assets folder
    all_reports = scan_assets_folder()
    
    # Filter reports based on search criteria
    filtered_reports = []
    for report in all_reports:
        matches_search = query == '' or \
            query in report['title'].lower() or \
            query in report['date'] or \
            query in report['displayDate'].lower()
        
        matches_filter = (report['isLatest'] and show_latest) or (not report['isLatest'] and show_archive)
        
        if matches_search and matches_filter:
            filtered_reports.append(report)
    
    return jsonify(filtered_reports)

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            flash('Login successful!')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')

# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
        
        # Create new user
        user = User()
        user.username = username
        user.password = password
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out')
    return redirect(url_for('index'))

# Dashboard route
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

# Stripe checkout session
@app.route('/create-checkout-session', methods=['POST'])
@login_required
def create_checkout_session():
    if current_user.is_paid:
        return jsonify({'error': 'Payment already completed'}), 400
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'TMT Daily Brief Premium',
                    },
                    'unit_amount': 1000,  # $10.00
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=YOUR_DOMAIN + '/success',
            cancel_url=YOUR_DOMAIN + '/cancel',
            metadata={"user_id": current_user.id}
        )
        return jsonify({'id': session.id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Stripe webhook
@app.route('/webhook', methods=['POST'])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    endpoint_secret = 'whsec_29a4674ae173cf9f65a762734b99ddb0f1667cfc1d4b2ff7e789044427d740ca'
    
    print(f"🔔 Webhook received: {request.headers.get('Stripe-Signature', 'No signature')}")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
        print(f"✅ Webhook verified: {event['type']}")
    except ValueError as e:
        print(f"❌ Invalid payload: {e}")
        return '', 400
    except SignatureVerificationError as e:
        print(f"❌ Invalid signature: {e}")
        return '', 400

    # Handle successful payment
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        user_id = session['metadata']['user_id']
        print(f"💰 Payment completed for user_id: {user_id}")
        
        user = User.query.get(user_id)
        if user:
            user.is_paid = True
            db.session.commit()
            print(f"✅ User {user.username} payment status updated to True")
        else:
            print(f"❌ User with id {user_id} not found")

    return '', 200

# Success page
@app.route('/success')
def success():
    # Check if user is authenticated, if not redirect to login
    if not current_user.is_authenticated:
        flash('Please login to access your dashboard')
        return redirect(url_for('login'))
    return render_template('success.html')

# Cancel page
@app.route('/cancel')
def cancel():
    # Check if user is authenticated, if not redirect to login
    if not current_user.is_authenticated:
        flash('Please login to access your dashboard')
        return redirect(url_for('login'))
    return render_template('cancel.html')

# Health check route
@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'message': 'Server is running'})

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('webpage.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('webpage.html'), 500

# Create database tables
with app.app_context():
    db.create_all()

# WSGI entry point for Vercel
app.debug = True

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

