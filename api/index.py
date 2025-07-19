from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
import stripe, requests
from stripe import SignatureVerificationError
import os
from datetime import datetime, timedelta
from pathlib import Path
from datetime import date
import json

# Parse report functionality moved from parse_report.py
from dataclasses import dataclass, asdict
from typing import List, Union
import re

#
# ---------- Primitive element classes ----------
#
@dataclass
class Paragraph:   text: List[Union[str, 'Term']]  # Paragraph now stores a list of strings and terms
@dataclass
class Bullet:      label: str; text: str
@dataclass
class Link:        label: str; url: str
@dataclass
class Term:        text: str; definition: str  # Technical terms with definitions

Element = Union[Paragraph, Bullet, Link, Term]

#
# ---------- Mid-level structure ----------
#
@dataclass
class SubSection:
    title: str
    body: List[Element]

@dataclass
class Section:
    number: int
    title: str
    subs: List[SubSection]

#
# ---------- Helper function to fetch definitions ----------
#
def fetch_definition(term: str) -> str:
    """
    Simulates an API call to fetch definitions for technical terms.
    In a real scenario, you would replace this with an actual API request.
    """
    # For now, returning a mock definition for demonstration
    mock_definitions = {
        "AI": "Artificial Intelligence, the simulation of human intelligence in machines.",
        "IPO": "Initial Public Offering, a company's first sale of stock to the public."
    }
    return mock_definitions.get(term, "Definition not found.")

#
# ---------- Public API ----------
#
def parse(raw: str) -> List[Section]:
    """
    Main entry point.  Returns a list[Section] ready for Jinja OR json.dumps().
    """
    lines = [ln.rstrip() for ln in raw.splitlines()]
    sec_pat   = re.compile(r'^###\s*(\d+)\.\s+(.*)$')            # "### 1. …"
    sub_pat   = re.compile(r'^\*\*(.+?)\*\*:?\s*$')              # "**Deal 1:**"
    body_pat  = re.compile(r'^[A-Za-z0-9\-\s\.:,;]*$')           # Catch generic body content (Deal 1 etc.)
    link_pat  = re.compile(r'\*\*(?P<title>.+?)\*\*\s*\(\s*\[Link\]\((?P<url>https?://[^\s)]+)\)\s*\)')  # [label](url)
    term_pat  = re.compile(r'\b[A-Z]{2,}\b')                     # crude TODO term
    bullet_pat = re.compile(r'^[\*\-\•]\s+\*\*(.+?)\*\*\s*(.*)$')  # "- **Deal Size:** something"

    sections: List[Section] = []
    cur_sec, cur_sub = None, None

    def flush_sub():
        nonlocal cur_sec, cur_sub
        if cur_sub and cur_sub.body and cur_sec:  # Only append non-empty subsections
            cur_sec.subs.append(cur_sub)
        cur_sub = None

    def flush_sec():
        nonlocal cur_sec
        if cur_sec:
            sections.append(cur_sec)
        cur_sec = None

    def replace_terms_in_paragraph(paragraph_text: str) -> List[Union[str, Term]]:
        """
        Replaces technical terms in a paragraph text with Term objects
        and returns the modified list of elements (strings and Term objects).
        """
        elements = []
        last_pos = 0

        for match in term_pat.finditer(paragraph_text):
            # Append text before the term
            elements.append(paragraph_text[last_pos:match.start()].strip())
            # Create a Term object with definition and append it
            term = match.group(0)
            definition = fetch_definition(term)
            elements.append(Term(text=term, definition=definition))
            last_pos = match.end()

        # Append any remaining text after the last term
        elements.append(paragraph_text[last_pos:].strip())
        return elements

    for ln in lines:
        if not ln.strip():                      # blank → paragraph boundary
            continue

        # SECTION
        if (m := sec_pat.match(ln)):
            flush_sub(); flush_sec()
            cur_sec = Section(int(m.group(1)), m.group(2), subs=[])
            continue

        # SUBSECTION (title is specifically given)
        if (m := sub_pat.match(ln)):
            flush_sub()
            cur_sub = SubSection(m.group(1), body=[])
            continue

        # Generic "body" or unnamed subsections (not a **Deal X:**)
        if (m := body_pat.match(ln)):
            if cur_sub:
                cur_sub.body.append(Paragraph(text=[ln.strip()]))  # Store text in list
            else:
                # If there's no valid subsection yet, create a default one
                cur_sub = SubSection("", body=[Paragraph(text=[ln.strip()])])
            continue

        # If no subsection, create a default one
        if not cur_sub:
            cur_sub = SubSection("", body=[])

        # Bullet?
        if (m := bullet_pat.match(ln)):
            label = m.group(1).strip()
            text = m.group(2).strip()
            if label.endswith(":"):
                label = label[:-1]
            if cur_sub:
                cur_sub.body.append(Bullet(label=label, text=text))   # Clean the bullet content
            continue

        # Links (may be inline inside paragraph)
        def _replace_link(match):
            if cur_sub:
                cur_sub.body.append(Link(match.group("title"), match.group("url")))
            return match.group("title")  # Keep the link text as plain text

        ln_clean = link_pat.sub(_replace_link, ln)

        # Only append the cleaned line if it wasn't replaced by a link
        if link_pat.search(ln) is None and cur_sub:
            # Replace any technical terms in the paragraph
            cur_sub.body.append(Paragraph(text=replace_terms_in_paragraph(ln_clean)))

    flush_sub(); flush_sec()
    return sections


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
    premium_expires_at = db.Column(db.DateTime, nullable=True)
    
    @property
    def has_valid_premium(self):
        """Check if user has valid premium access (paid and not expired)"""
        if not self.is_paid:
            return False
        if not self.premium_expires_at:
            return True  # Legacy users without expiration date
        return self.premium_expires_at > datetime.utcnow()

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

def check_expired_subscriptions():
    """Check for expired subscriptions and update them"""
    try:
        # Find users with expired premium access
        expired_users = User.query.filter(
            User.is_paid == True,
            User.premium_expires_at.isnot(None),
            User.premium_expires_at < datetime.utcnow()
        ).all()
        
        for user in expired_users:
            user.is_paid = False
            print(f"❌ User {user.username} premium access expired")
        
        if expired_users:
            db.session.commit()
            print(f"✅ Updated {len(expired_users)} expired subscriptions")
        
    except Exception as e:
        print(f"❌ Error checking expired subscriptions: {e}")
        db.session.rollback()

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
    print("=" * 50)
    print("🔔 WEBHOOK RECEIVED")
    print("=" * 50)
    
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    endpoint_secret = os.environ.get('STRIPE_WEBHOOK_SECRET', 'whsec_QDig1ieBZ9f1FpmudVzy4fSAUftKuge3')
    
    print(f"   Method: {request.method}")
    print(f"   URL: {request.url}")
    print(f"   Headers: {dict(request.headers)}")
    print(f"   Payload length: {len(payload)} bytes")
    print(f"   Signature: {sig_header}")
    print(f"   Endpoint secret: {endpoint_secret[:10]}...")
    
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
                # Set expiration date to 1 month from now
                user.premium_expires_at = datetime.utcnow() + timedelta(days=30)
                db.session.commit()
                print(f"✅ User {user.username} payment status updated to True, expires at {user.premium_expires_at}")
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
    print("=" * 50)
    print("🎉 SUCCESS PAGE ACCESSED")
    print("=" * 50)
    print(f"   User: {current_user.username if current_user.is_authenticated else 'Not authenticated'}")
    print(f"   User ID: {current_user.id if current_user.is_authenticated else 'N/A'}")
    print(f"   is_paid: {current_user.is_paid if current_user.is_authenticated else 'N/A'}")
    print(f"   premium_expires_at: {current_user.premium_expires_at if current_user.is_authenticated else 'N/A'}")
    
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

# Test endpoint to manually trigger payment completion (for debugging)
@app.route('/test-payment-completion/<int:user_id>')
def test_payment_completion(user_id):
    """Test endpoint to manually trigger payment completion for debugging"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Simulate payment completion
        user.is_paid = True
        user.premium_expires_at = datetime.utcnow() + timedelta(days=30)
        print(user.premium_expires_at)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'user': user.username,
            'is_paid': user.is_paid,
            'premium_expires_at': user.premium_expires_at.isoformat() if user.premium_expires_at else None,
            'has_valid_premium': user.has_valid_premium
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Test webhook endpoint
@app.route('/test-webhook', methods=['POST'])
def test_webhook():
    """Simple test endpoint to verify webhook delivery"""
    print("=" * 50)
    print("🧪 TEST WEBHOOK RECEIVED")
    print("=" * 50)
    print(f"   Method: {request.method}")
    print(f"   URL: {request.url}")
    print(f"   Headers: {dict(request.headers)}")
    print(f"   Data: {request.data}")
    return jsonify({'status': 'test webhook received'})


# Render brief on webpage with date parameter
@app.route('/briefRenderTest/<date>')
@login_required
def renderTest(date):
    # Check if user has premium access
    if not current_user.has_valid_premium:
        flash('Premium access required to view reports. Please upgrade your subscription.')
        return redirect(url_for('dashboard'))
    
    try:
        # Convert date format from YYYY-MM-DD to raw filename
        raw_filename = f"TMT_Brief_{date}_raw.txt"
        raw = load_raw_text(raw_filename)
        structured = parse(raw)
    except Exception as e:
        app.logger.exception("Error parsing raw brief")   # logs full traceback
        return "Error parsing raw brief", 500
    return render_template("renderTest.html", sections=structured, date=date, term_definitions=TERM_DEFINITIONS)

# Protected route for downloading PDF reports
@app.route('/download/<filename>')
@login_required
def download_report(filename):
    # Check if user has premium access
    if not current_user.has_valid_premium:
        flash('Premium access required to download reports. Please upgrade your subscription.')
        return redirect(url_for('dashboard'))
    
    # Validate filename to prevent directory traversal
    if not filename.endswith('.pdf') or '..' in filename or '/' in filename:
        flash('Invalid filename')
        return redirect(url_for('index'))
    
    # Check if file exists
    if app.static_folder is None:
        flash('Static folder not configured')
        return redirect(url_for('index'))
    
    file_path = os.path.join(app.static_folder, 'assets', 'briefs', filename)
    if not os.path.exists(file_path):
        flash('Report not found')
        return redirect(url_for('index'))
    
    return send_file(file_path, as_attachment=True)

# Protected route for viewing PDF reports
@app.route('/view/<filename>')
@login_required
def view_report(filename):
    # Check if user has premium access
    if not current_user.has_valid_premium:
        flash('Premium access required to view reports. Please upgrade your subscription.')
        return redirect(url_for('dashboard'))
    
    # Validate filename to prevent directory traversal
    if not filename.endswith('.pdf') or '..' in filename or '/' in filename:
        flash('Invalid filename')
        return redirect(url_for('index'))
    
    # Check if file exists
    if app.static_folder is None:
        flash('Static folder not configured')
        return redirect(url_for('index'))
    
    file_path = os.path.join(app.static_folder, 'assets', 'briefs', filename)
    if not os.path.exists(file_path):
        flash('Report not found')
        return redirect(url_for('index'))
    
    return send_file(file_path)


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
        check_expired_subscriptions() # Call the new function here
    app.run(debug=True, port=5000)


