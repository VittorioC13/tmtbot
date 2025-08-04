from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
import requests
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
class Paragraph:  text: str            # ← keep it simple: ONE string
@dataclass
class Bullet:     label: str; text: str
@dataclass
class Link:       label: str; url: str
@dataclass
class Underline:  text: str
@dataclass
class BoldLine:   text: str

Element = Union[Paragraph, Bullet, Link, BoldLine, Underline]

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
# ---------- Public API ----------
#
def parse(raw: str) -> List[Section]:
    """
    Main entry point.  Returns a list[Section] ready for Jinja OR json.dumps().
    """
    lines = [ln.rstrip() for ln in raw.splitlines()]
    sec_pat   = re.compile(r'^###\s*(\d+)\.\s+(.*)$')            # "### 1. …"
    sub_pat = re.compile(
        r'^(?:'                     # start alternation
        r'\*\*(.+?)\*\*:?\s*$'      #  branch-A  **Title:**   →  group-1
        r'|'                        #  OR
        r'####\s+(.+?)\s*$'         #  branch-B  #### Title   →  group-2
        r')'
    )
    body_pat  = re.compile(r'^[A-Za-z0-9\-\s\.:,;]*$')           # Catch generic body content (Deal 1 etc.)
    link_pat  = re.compile(r'\*\*(?P<title>.+?)\*\*\s*\(\s*\[Link\]\((?P<url>https?://[^\s)]+)\)\s*\)')  # [label](url)x
    bullet_pat = re.compile(
        r'^\s*'            # optional indent / spaces or tabs
        r'[\*\-\•]'        # the bullet marker: *, -, or •
        r'\s+\*\*(.+?)\*\*'  # space(s) then **Label** (capture 1)
        r'\s*(.*)$'        # optional space then the rest of the line (capture 2)
    )
    BoldLine_pat = re.compile(r'^@{3}\s+(?P<b_lbl>.+?)\s*$')                    # @@@ text
    Underline_pat = re.compile(r'^@{4}\s+(?P<u_lbl>.+?)\s*$')   # "@@@@ Heading"

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


    for ln in lines:
        if not ln.strip():                      # blank → paragraph boundary
            continue

        #Bold line 
        if (m := BoldLine_pat.match(ln)):
            flush_sub()
            cur_sub = SubSection(m.group('b_lbl'), body=[])
            continue

        # UNDERLINED header "@@@@ " → start new subsection
        if (m := Underline_pat.match(ln)):
            flush_sub()
            cur_sub = SubSection(m.group('u_lbl'), body=[])
            continue

        # SECTION
        if (m := sec_pat.match(ln)):
            flush_sub(); flush_sec()
            cur_sec = Section(int(m.group(1)), m.group(2), subs=[])
            continue

        # SUBSECTION (title is specifically given)
        if (m := sub_pat.match(ln)):
            flush_sub()
            # whichever branch matched, exactly one of the two groups is not None
            title = m.group(1) or m.group(2)
            cur_sub = SubSection(title, body=[])
            continue


        # Bullet?
        if (m := bullet_pat.match(ln)):
            label = m.group(1).strip()
            text = m.group(2).strip()
            if label.endswith(":"):
                label = label[:-1]
            # Create a default subsection if none exists
            if not cur_sub and cur_sec:
                cur_sub = SubSection("", body=[])
            if cur_sub:
                cur_sub.body.append(Bullet(label=label, text=text))   # Clean the bullet content
            continue

        # Generic "body" or unnamed subsections (not a **Deal X:**)
        if (m := body_pat.match(ln)):
            if cur_sub:
                cur_sub.body.append(Paragraph(text=ln.strip()))  # Store text in list
            else:
                # If there's no valid subsection yet, create a default one
                cur_sub = SubSection("", body=[Paragraph(text=ln.strip())])
            continue

        # If no subsection, create a default one
        if not cur_sub and cur_sec:
            cur_sub = SubSection("", body=[])


        had_link = False                     # track whether we saw at least one link

        def _replace_link(match):
            nonlocal had_link
            had_link = True
            if cur_sub:
                cur_sub.body.append(Link(match.group("title"), match.group("url")))
            return match.group("title")      # keep anchor text

        ln_clean = link_pat.sub(_replace_link, ln)

        # Only append the cleaned line if it wasn't replaced by a link
        if link_pat.search(ln) is None and cur_sub:
            # Replace any technical terms in the paragraph
            cur_sub.body.append(Paragraph(ln_clean))
        elif link_pat.search(ln) is None and cur_sec and ln.strip():
            # If no subsection exists but we have content, create a default subsection
            cur_sub = SubSection("", body=[Paragraph(ln_clean)])

    flush_sub(); flush_sec()
    return sections


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
        case "Underline":
            return isinstance(obj, Underline)
        case "BoldLine":
            return isinstance(obj, BoldLine)
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
    premium_status = db.Column(db.String(20), default='none')  # none, basic, premium, max
    premium_expires_at = db.Column(db.DateTime, nullable=True)
    selected_sector = db.Column(db.String(10), nullable=True)  # 'TMT', 'Energy', or 'Healthcare'
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
            User.premium_status.in_(['premium', 'max']),
            User.premium_expires_at.isnot(None),
            User.premium_expires_at < datetime.utcnow()
        ).all()
        
        for user in expired_users:
            user.premium_status = 'none'
            print(f"❌ User {user.username} subscription expired")
        
        if expired_users:
            db.session.commit()
            print(f"✅ Updated {len(expired_users)} expired subscriptions")
        
    except Exception as e:
        print(f"❌ Error checking expired subscriptions: {e}")
        db.session.rollback()

# Root route - serves the main webpage
@app.route('/')
def index():
    # Check if user is logged in and has a valid subscription
    if current_user.is_authenticated and current_user.has_valid_premium:
        # Check if basic user needs to select sector
        if current_user.needs_sector_selection:
            return redirect(url_for('select_sector'))
        
        # Get all reports and find latest TMT and Energy reports
        reports = scan_assets_folder_PDF()
        
        # Find latest TMT, Energy, and Healthcare reports
        latest_tmt = None
        latest_energy = None
        latest_healthcare = None
        
        # Since reports are sorted by date (newest first), the first report of each type is the latest
        for report in reports:
            if report['title'] == "TMT Daily Brief" and latest_tmt is None:
                latest_tmt = report
            elif report['title'] == "Energy Daily Brief" and latest_energy is None:
                latest_energy = report
            elif report['title'] == "Healthcare Daily Brief" and latest_healthcare is None:
                latest_healthcare = report
            # Continue searching until we find all three types or exhaust all reports
            if latest_tmt and latest_energy and latest_healthcare:
                break
        
        return render_template('webpage.html', latest_tmt=latest_tmt, latest_energy=latest_energy, latest_healthcare=latest_healthcare, user_plan=current_user.premium_status)
    else:
        # Show exhibit page for non-subscribers
        return render_template('exhibit.html')

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
                title = "TMT Daily Brief"  # Default title
                
                if filename.startswith('TMT_Brief_'):
                    # Format: TMT_Brief_2025-07-02.pdf
                    date_str = filename.replace('TMT_Brief_', '').replace('.pdf', '')
                    title = "TMT Daily Brief"
                elif filename.startswith('Energy_Brief_'):
                    # Format: Energy_Brief_2025-07-24.pdf
                    date_str = filename.replace('Energy_Brief_', '').replace('.pdf', '')
                    title = "Energy Daily Brief"
                elif filename.startswith('Healthcare_Brief_'):
                    # Format: Healthcare_Brief_2025-08-03.pdf
                    date_str = filename.replace('Healthcare_Brief_', '').replace('.pdf', '')
                    title = "Healthcare Daily Brief"
                elif filename.startswith('brief_'):
                    # Format: brief_2024-01-11.pdf
                    date_str = filename.replace('brief_', '').replace('.pdf', '')
                    title = "TMT Daily Brief"
                
                if date_str:
                    try:
                        # Parse the date
                        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                        display_date = date_obj.strftime('%B %d, %Y')
                        
                        reports.append({
                            "title": title,
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

# Sector selection route
@app.route('/select-sector', methods=['GET', 'POST'])
@login_required
def select_sector():
    # Only basic users should access this page
    if current_user.premium_status not in ['basic', 'none']:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        sector = request.form.get('sector')
        if sector in ['TMT', 'Energy', 'Healthcare']:
            current_user.selected_sector = sector
            current_user.sector_changed_at = datetime.utcnow()
            db.session.commit()
            flash(f'You have selected {sector} sector. You can change this anytime from your dashboard.')
            return redirect(url_for('index'))
        else:
            flash('Please select a valid sector.')
    
    return render_template('select_sector.html')

# Change sector route
@app.route('/change-sector', methods=['GET', 'POST'])
@login_required
def change_sector():
    # Only basic users should access this page
    if current_user.premium_status != 'basic':
        return redirect(url_for('index'))
    
    # Check if user can change sector (once per week)
    if not current_user.can_change_sector:
        days_remaining = 7 - (datetime.utcnow() - current_user.sector_changed_at).days
        flash(f'You can only change your sector once per week. You can change it again in {days_remaining} days.')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        sector = request.form.get('sector')
        if sector in ['TMT', 'Energy', 'Healthcare']:
            current_user.selected_sector = sector
            current_user.sector_changed_at = datetime.utcnow()
            db.session.commit()
            flash(f'Your sector has been changed to {sector}. You can change it again next week.')
            return redirect(url_for('dashboard'))
        else:
            flash('Please select a valid sector.')
    
    return render_template('select_sector.html', is_change=True)

# Dashboard route
@app.route('/dashboard')
@login_required
def dashboard():
    # Calculate days remaining for sector change if applicable
    days_remaining = None
    if current_user.premium_status == 'basic' and current_user.sector_changed_at and not current_user.can_change_sector:
        days_remaining = 7 - (datetime.utcnow() - current_user.sector_changed_at).days
    
    return render_template('dashboard.html', user=current_user, days_remaining=days_remaining)

# WeChat payment redirect
@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    # Check if user is authenticated
    if not current_user.is_authenticated:
        print("❌ User not authenticated for payment session")
        return jsonify({'error': 'Authentication required. Please login first.'}), 401
    
    print(f"✅ User authenticated: {current_user.username} (ID: {current_user.id})")
    
    if current_user.premium_status in ['basic', 'premium', 'max']:
        print("❌ User already has a subscription")
        return jsonify({'error': 'Subscription already active'}), 400
    
    # Redirect to WeChat payment page
    return jsonify({'redirect': url_for('wechat_payment')})

# WeChat payment verification
@app.route('/verify-payment', methods=['POST'])
def verify_payment():
    """Verify WeChat payment and update user status"""
    if not current_user.is_authenticated:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        # Get plan information from request
        data = request.get_json()
        plan = data.get('plan', 'basic')
        price = data.get('price', 28)
        
        # Validate plan
        valid_plans = ['basic', 'premium', 'max']
        if plan not in valid_plans:
            return jsonify({'error': 'Invalid plan selected'}), 400
        
        # Don't update user payment status - require manual verification
        # current_user.premium_status = plan
        # current_user.premium_expires_at = datetime.utcnow() + timedelta(days=30)
        # db.session.commit()
        
        # Customize message based on plan type
        if plan == 'max':
            message = 'Thanks for your payment! Your Max Status would be confirmed after manual verification.'
        else:
            message = 'Thanks for your payment! Your Premium Status would be confirmed after manual verification.'
        
        print(f"✅ User {current_user.username} payment submitted for {plan} plan (¥{price}) - awaiting manual verification")
        return jsonify({'success': True, 'message': message})
        
    except Exception as e:
        print(f"❌ Error processing payment: {e}")
        db.session.rollback()
        return jsonify({'error': 'Payment processing failed'}), 500

# WeChat payment page
@app.route('/wechat-payment')
@login_required
def wechat_payment():
    return render_template('wechat_payment.html')

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




# Render brief on webpage with sector and date parameters
@app.route('/briefRenderTest/<sector>/<date>')
@login_required
def renderTest(sector, date):
    # Check if user has view access (premium/max only)
    if not current_user.has_view_access:
        if current_user.premium_status == 'basic':
            flash('View access requires Premium or Max plan. Basic plan users can only download reports.')
        else:
            flash('Premium access required to view reports. Please upgrade your subscription.')
        return redirect(url_for('dashboard'))
    
    # Validate sector parameter
    valid_sectors = ['TMT', 'Energy', 'Healthcare']
    if sector not in valid_sectors:
        return f"Invalid sector: {sector}. Valid sectors are: {', '.join(valid_sectors)}", 400
    
    # For basic users, check if they can view this specific sector
    if current_user.premium_status == 'basic':
        if current_user.selected_sector != sector:
            flash(f'You can only view {current_user.selected_sector} reports with your Basic plan. Upgrade to Premium for access to all reports.')
            return redirect(url_for('dashboard'))
    
    try:
        # Construct the raw filename based on sector and date
        raw_filename = f"{sector}_Brief_{date}_raw.txt"
        raw_path = RAW_DIR / raw_filename
        
        if not raw_path.exists():
            return f"No raw brief found for {sector} sector on {date}.", 404
        
        raw = load_raw_text(raw_filename)
        structured = parse(raw)
    except Exception as e:
        app.logger.exception("Error parsing raw brief")   # logs full traceback
        return "Error parsing raw brief", 500
    return render_template("renderTest.html", sections=structured, date=date, sector=sector, term_definitions=TERM_DEFINITIONS)

# Protected route for downloading PDF reports
@app.route('/download/<filename>')
@login_required
def download_report(filename):
    # Check if user has valid premium access
    if not current_user.has_valid_premium:
        flash('Premium access required to download reports. Please upgrade your subscription.')
        return redirect(url_for('dashboard'))
    
    # For basic users, check if they can download this specific report
    if current_user.premium_status == 'basic':
        # Check if the filename matches their selected sector
        if current_user.selected_sector == 'TMT' and not filename.startswith('TMT_Brief_'):
            flash('You can only download TMT reports with your Basic plan. Upgrade to Premium for access to all reports.')
            return redirect(url_for('dashboard'))
        elif current_user.selected_sector == 'Energy' and not filename.startswith('Energy_Brief_'):
            flash('You can only download Energy reports with your Basic plan. Upgrade to Premium for access to all reports.')
            return redirect(url_for('dashboard'))
        elif current_user.selected_sector == 'Healthcare' and not filename.startswith('Healthcare_Brief_'):
            flash('You can only download Healthcare reports with your Basic plan. Upgrade to Premium for access to all reports.')
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

# Protected route for viewing PDF reports by filename
@app.route('/view/<filename>')
@login_required
def view_report(filename):
    # Allow all authenticated users with valid premium to view PDFs
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

# Protected route for viewing PDF reports by sector and date
@app.route('/view/<sector>/<date>')
@login_required
def view_report_by_sector(sector, date):
    # Allow all authenticated users with valid premium to view PDFs
    if not current_user.has_valid_premium:
        flash('Premium access required to view reports. Please upgrade your subscription.')
        return redirect(url_for('dashboard'))
    
    # Validate sector
    valid_sectors = ['TMT', 'Energy', 'Healthcare']
    if sector not in valid_sectors:
        flash('Invalid sector')
        return redirect(url_for('index'))
    
    # For basic users, check if they can view this specific sector
    if current_user.premium_status == 'basic':
        if current_user.selected_sector != sector:
            flash(f'You can only view {current_user.selected_sector} reports with your Basic plan. Upgrade to Premium for access to all reports.')
            return redirect(url_for('dashboard'))
    
    # Construct filename based on sector and date
    filename = f"{sector}_Brief_{date}.pdf"
    
    # Validate filename to prevent directory traversal
    if '..' in filename or '/' in filename:
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

def migrate_user_premium_status():
    """Migrate existing users from is_paid to premium_status"""
    try:
        with app.app_context():
            # Get all users
            users = User.query.all()
            migrated_count = 0
            
            for user in users:
                # Check if user has the old is_paid field (this will fail if column doesn't exist)
                try:
                    # Try to access the old is_paid field
                    if hasattr(user, 'is_paid') and user.is_paid:
                        user.premium_status = 'basic'  # Changed from premium to basic
                        migrated_count += 1
                        print(f"✅ Migrated user {user.username} from is_paid=True to premium_status=basic")
                except:
                    # Column doesn't exist, skip
                    pass
            
            if migrated_count > 0:
                db.session.commit()
                print(f"✅ Successfully migrated {migrated_count} users")
            else:
                print("ℹ️ No users to migrate or migration already completed")
                
    except Exception as e:
        print(f"❌ Error during migration: {e}")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        migrate_user_premium_status()  # Run migration
        check_expired_subscriptions() # Call the new function here
    app.run(debug=True, port=5000)


