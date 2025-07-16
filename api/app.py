from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
import stripe, requests
from stripe import SignatureVerificationError
import os
from datetime import datetime, timedelta
from pathlib import Path
from datetime import date
from parse_report import parse, Paragraph, Bullet, Link, Term
import json


# Stripe configuration
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY', "sk_test_51Ri9SyFSHePhJarRDO1vrS4Ca8T8pRqsvkluFVE8sP4nc5qwiGal62fcWZAU9JeUbatWjzEZ6MQigXxOUvHwmXwJ00vr1eTfnk")
YOUR_DOMAIN = os.environ.get('VERCEL_URL', "https://tmt-api-git-main-xukun-cais-projects.vercel.app")

# Configure Stripe for better SSL handling in development
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')  # Change this to a secure secret key
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)  # Session lasts 7 days
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://postgres.raxegckgsveacgflvwbd:wdsjkdmmhaq@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres')  # PostgreSQL database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
    'pool_timeout': 20,
    'max_overflow': 0
}


def check_type(obj, typ):
    match typ:
        case "Paragraph":
            return isinstance(obj, Paragraph)
        case "Bullet":
            return isinstance(obj, Bullet)
        case "Link":
            return isinstance(obj, Link)
        case "Term":
            return isinstance(obj, Term)
        case _:
            return False
app.jinja_env.globals['check_type'] = check_type


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

RAW_DIR = (Path(__file__).resolve().parent           # api/
        / 'static' / 'assets' / 'raw').resolve()

# Load term definitions
def load_term_definitions():
    """Load term definitions from JSON file"""
    try:
        # Use the correct path relative to the app.py file
        json_path = Path(__file__).parent / 'term_definitions.json'
        with open(json_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: term_definitions.json not found at {json_path}")
        return {}

TERM_DEFINITIONS = load_term_definitions()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Database connection helper for serverless environment
def get_db_connection():
    try:
        # Test the connection
        with db.engine.connect() as conn:
            conn.execute(db.text('SELECT 1'))
        return True
    except Exception as e:
        print(f"Database connection error: {e}")
        return False

# Root route - serves the main webpage
@app.route('/')
def index():
    # Get the latest report for the main display
    reports = scan_assets_folder_PDF()
    latest_report = reports[0] if reports else None
    return render_template('webpage.html', latest_report=latest_report)

def scan_assets_folder_PDF():
    """Scan the static/assets/briefs folder for PDF reports and return them sorted by date"""
    if app.static_folder is None:
        return []
    
    briefs_path = os.path.join(app.static_folder, 'assets', 'briefs')
    reports = []
    
    if os.path.exists(briefs_path):
        for filename in os.listdir(briefs_path):
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


def scan_raw_folder():
    """
    Returns a list of dicts with each raw report:
        {
          "filename": "raw_2025-07-11.txt",
          "date": date(2025, 7, 11)
        }
    Ordered newest first.
    """

    raw_files = sorted(RAW_DIR.glob('raw_*.txt'), reverse=True)

    def _to_record(path: Path):
        try:
            date_str = path.stem.split('_', 1)[1]  # "2025-07-11"
            y, m, d = map(int, date_str.split('-'))
            dt = date(y, m, d)
        except Exception:
            dt = None
        return {"filename": path.name, "date": dt}

    return [_to_record(p) for p in raw_files]


def load_raw_text(filename: str, encoding: str = "utf-8") -> str:
    """
    Return the full text of one raw report found in RAW_DIR.

    Parameters
    ----------
    filename : str
        The exact basename, e.g. "raw_2025-07-11.txt".
        • No sub-paths are allowed; anything like "../../" is stripped.
    encoding : str
        Defaults to "utf-8".  Override only if you know you saved the file
        with a different encoding.

    Raises
    ------
    FileNotFoundError
        If the file does not exist in RAW_DIR.
    """
    # Prevent directory-traversal attempts and ensure we stay in RAW_DIR
    safe_name = Path(filename).name           # drops any "../"
    file_path = RAW_DIR / safe_name

    if not file_path.is_file():
        raise FileNotFoundError(f"No raw brief named {safe_name!r} in {RAW_DIR}")

    return file_path.read_text(encoding=encoding)


# API route to get reports data
@app.route('/api/reports')
def get_reports():
    reports = scan_assets_folder_PDF()
    return jsonify(reports)

# Search API route
@app.route('/api/search')
def search_reports():
    query = request.args.get('q', '').lower()
    show_latest = request.args.get('latest', 'true').lower() == 'true'
    show_archive = request.args.get('archive', 'true').lower() == 'true'
    
    # Get all reports from assets folder
    all_reports = scan_assets_folder_PDF()
    
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
            login_user(user, remember=True)  # Remember user for 7 days
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
        password2 = request.form['password2']
        
        # Check if passwords match
        if password != password2:
            flash('Passwords do not match')
            return redirect(url_for('register'))
        
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
def create_checkout_session():
    # Check if user is authenticated
    if not current_user.is_authenticated:
        print("❌ User not authenticated for payment session")
        return jsonify({'error': 'Authentication required. Please login first.'}), 401
    
    print(f"✅ User authenticated: {current_user.username} (ID: {current_user.id})")
    
    if current_user.is_paid:
        print("❌ User already paid")
        return jsonify({'error': 'Payment already completed'}), 400
    
    try:
        # Get the current domain dynamically (works for local and production)
        current_domain = request.url_root.rstrip('/')
        
        print(f"Creating checkout session for user {current_user.id} with domain: {current_domain}")
        
        # Create checkout session without customer_email to avoid validation issues
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'TMT Daily Brief Premium',
                        'description': 'Access to all TMT Daily Brief reports and premium features',
                    },
                    'unit_amount': 1000,  # $10.00
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f"{current_domain}/success",
            cancel_url=f"{current_domain}/cancel",
            metadata={"user_id": current_user.id},
        )
        
        print(f"✅ Checkout session created: {session.id}")
        return jsonify({'id': session.id})
        
    except Exception as e:
        import traceback
        print(f"❌ Error creating checkout session: {e}")
        print("Full traceback:")
        traceback.print_exc()
        
        # Check if it's an SSL error and provide a helpful message
        if "SSL" in str(e) or "EOF" in str(e):
            return jsonify({'error': 'SSL connection error. Please try again or contact support.'}), 500
        
        return jsonify({'error': f'Payment error: {str(e)}'}), 500

# Stripe webhook
@app.route('/webhook', methods=['POST'])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    endpoint_secret = os.environ.get('STRIPE_WEBHOOK_SECRET', 'whsec_QDig1ieBZ9f1FpmudVzy4fSAUftKuge3')
    
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
    except:
        print(f"unknown errorc")
        return '', 400

    # Handle successful payment
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        user_id = session['metadata']['user_id']
        print(f"💰 Payment completed for user_id: {user_id}")
        
        try:
            # Ensure database connection is available
            if not get_db_connection():
                print("❌ Database connection failed")
                return '', 500
            
            user = User.query.get(user_id)
            if user:
                user.is_paid = True
                db.session.commit()
                print(f"✅ User {user.username} payment status updated to True")
            else:
                print(f"❌ User with id {user_id} not found")
        except Exception as e:
            print(f"❌ Database error: {e}")
            db.session.rollback()
            return '', 500

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


# Render brief on webpage with date parameter
@app.route('/briefRenderTest/<date>')
def renderTest(date):
    try:
        # Convert date format from YYYY-MM-DD to raw filename
        raw_filename = f"TMT_Brief_{date}_raw.txt"
        raw = load_raw_text(raw_filename)
        structured = parse(raw)
    except Exception as e:
        app.logger.exception("Error parsing raw brief")   # logs full traceback
        return "Error parsing raw brief", 500
    return render_template("renderTest.html", sections=structured, date=date, term_definitions=TERM_DEFINITIONS)


# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('webpage.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('webpage.html'), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)


