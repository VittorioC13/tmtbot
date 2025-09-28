from flask import Flask, render_template, request, jsonify, redirect, url_for, session, send_from_directory, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import json
import os
import glob 
from pathlib import Path
import re
from dataclasses import dataclass, asdict
from typing import List, Union
from pymongo import MongoClient, ASCENDING
from functools import lru_cache
from pymongo.server_api import ServerApi
import certifi
from dotenv import load_dotenv
import httpx
import openai
from bson import ObjectId
from hashlib import md5
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, DateField
from wtforms.validators import DataRequired
from typing import Optional

load_dotenv('../.env')
OPENAI_API_KEY = os.environ.get("OPENAI_API")
API2D_BASE_URL = "https://oa.api2d.net"  # API2D endpoint
if not OPENAI_API_KEY:
#    raise RuntimeError("Missing OPENAI_API_KEY env var")
    pass

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


MONGODB_URI="mongodb+srv://lingcheng783:Ling050707@cluster0.6fvatcq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
#MONGODB_URI = os.environ.get("MONGODB_URI")
MONGODB_STANDARD_URI="mongodb://user:pass@host1:27017,host2:27017,host3:27017/?replicaSet=atlas-XXXX-shard-0&authSource=admin&tls=true&retryWrites=true&w=majority"
MONGO_DB_NAME = os.environ.get("MONGO_DB_NAME", "tmtbot")   # optional; defaults to "tmtbot" if not set


app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'
app.conversations = None
app.messages = None

if not MONGODB_URI:
    raise RuntimeError("MONGODB_URI not set. Add it to your .env or environment.")

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://postgres.raxegckgsveacgflvwbd:wdsjkdmmhaq@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
}

# Initialize SQLAlchemy
db = SQLAlchemy(app)


@lru_cache(maxsize=1)
def get_mongo():
    client = MongoClient(
        MONGODB_URI,
        server_api=ServerApi('1'),
        tls=False,
        tlsAllowInvalidCertificates=True,
        serverSelectionTimeoutMS=15000,
        connectTimeoutMS=15000,
        socketTimeoutMS=20000,
    )
    #client.admin.command("ping")   # fail fast if unreachable
    return client

def init_mongo():
    client = get_mongo()                 # this pings; will raise if unreachable
    mongo_db = client[MONGO_DB_NAME]
    app.conversations = mongo_db["conversations"]
    app.messages      = mongo_db["messages"]

@app.before_request
def _ensure_mongo():
    # init if missing or if a previous init failed and left None
    if getattr(app, "conversations", None) is None or getattr(app, "messages", None) is None:
        try:
            init_mongo()
        except Exception as e:
            # log and surface a clear 500 rather than AttributeError later
            app.logger.exception("Mongo init failed")
            return "MongoDB initialization failed. Check connectivity/URI/whitelist.", 500




# Database initialization
def init_db():
    """Initialize the database with only User table"""
    with app.app_context():
        # Create only the User table
        db.create_all()
        print("Database initialized - only User table created")
        print("Using existing users from your database")




# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

#
# ---------- Mid-level structure ----------
#
@dataclass
class table:
    header: List[str]
    rows: List[List[str]]


Element = Union[Paragraph, Bullet, Link, BoldLine, Underline, table]


@dataclass
class SubSection:
    title: str
    body: List[Element]

@dataclass
class Section:
    number: int
    title: str
    subs: List[SubSection]




TABLE_ROW_PAT = re.compile(r'^\s*\|.*\|\s*$')
TABLE_SEP_PAT = re.compile(r'^\s*\|?\s*:?-{3,}\s*(\|\s*:?-{3,}\s*)+\|?\s*$')
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


def _split_table_row(line: str) -> List[str]:
    s = line.strip()
    if s.startswith('|'): s = s[1:]
    if s.endswith('|'): s = s[:-1]
    return [c.strip() for c in s.split('|')]

def render_table(lines: List[str]):
    """
    GitHub-style tables:
      | A | B |
      | --- | --- |
      | a1 | b1 |
    Separator line is optional; if present, treat first line as header.
    If not present, first line still becomes header, remaining lines are rows.
    """
    if not lines:
        return table(header=[], rows=[])
    header = _split_table_row(lines[0])
    rows: List[List[str]] = []

    j = 1
    if j < len(lines) and TABLE_SEP_PAT.match(lines[j]):
        j += 1  # skip separator

    for k in range(j, len(lines)):
        if TABLE_SEP_PAT.match(lines[k]):  # ignore stray separators
            continue
        rows.append(_split_table_row(lines[k]))

    # Optional: apply inline bold to cells (comment in if you need it)
    # header = _flatten_inline_cells(header)
    # rows   = [_flatten_inline_cells(r) for r in rows]

    return table(header=header, rows=rows)

#
# ---------- Public API ----------
#
def parse(raw: str) -> List[Section]:
    lines = [ln.rstrip() for ln in raw.splitlines()]
    sections: List[Section] = []
    cur_sec: Optional[Section] = None
    cur_sub: Optional[SubSection] = None

    def flush_sub():
        nonlocal cur_sec, cur_sub
        if cur_sub and cur_sub.body and cur_sec:
            cur_sec.subs.append(cur_sub)
        cur_sub = None

    def flush_sec():
        nonlocal cur_sec
        if cur_sec:
            sections.append(cur_sec)
        cur_sec = None

    i, n = 0, len(lines)
    while i < n:
        ln = lines[i]
        if not ln.strip():
            i += 1
            continue

        # SECTION
        m = sec_pat.match(ln)
        if m:
            flush_sub(); flush_sec()
            cur_sec = Section(int(m.group(1)), m.group(2), subs=[])
            i += 1
            continue

        # Bold line "@@@"
        m = BoldLine_pat.match(ln)
        if m:
            flush_sub()
            cur_sub = SubSection(m.group('b_lbl'), body=[])
            i += 1
            continue

        # Underlined header "@@@@"
        m = Underline_pat.match(ln)
        if m:
            flush_sub()
            cur_sub = SubSection(m.group('u_lbl'), body=[])
            i += 1
            continue

        # SUBSECTION (**Title:** or #### Title)
        m = sub_pat.match(ln)
        if m:
            flush_sub()
            title = m.group(1) or m.group(2)
            cur_sub = SubSection(title, body=[])
            i += 1
            continue

        # TABLE BLOCK
        if is_table_line(ln):
            j = i
            tbl_lines: List[str] = []
            while j < n and is_table_line(lines[j]):
                tbl_lines.append(lines[j])
                j += 1
            if not cur_sub:
                if not cur_sec:
                    cur_sec = Section(0, "", subs=[])
                cur_sub = SubSection("", body=[])
            cur_sub.body.append(render_table(tbl_lines))
            i = j
            continue

        # Bullet?
        m = bullet_pat.match(ln)
        if m:
            label = (m.group(1) or "").strip().rstrip(":")
            text  = (m.group(2) or "").strip()
            if not cur_sub:
                if not cur_sec:
                    cur_sec = Section(0, "", subs=[])
                cur_sub = SubSection("", body=[])
            cur_sub.body.append(Bullet(label=label, text=text))
            i += 1
            continue

        # Inline links (needs nonlocal so we can create cur_sub)
        had_link = False
        def _replace_link(match):
            nonlocal cur_sub, cur_sec, had_link
            had_link = True
            if not cur_sub:
                if not cur_sec:
                    cur_sec = Section(0, "", subs=[])
                cur_sub = SubSection("", body=[])
            cur_sub.body.append(Link(match.group("title"), match.group("url")))
            return match.group("title")

        ln_clean = link_pat.sub(_replace_link, ln)

        # Paragraph / generic body
        if not cur_sub:
            if not cur_sec:
                cur_sec = Section(0, "", subs=[])
            cur_sub = SubSection("", body=[])
        if ln_clean.strip():
            cur_sub.body.append(Paragraph(text=ln_clean.strip()))

        i += 1

    flush_sub(); flush_sec()
    return sections



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
        case "generic":
            return isinstance(obj, generic)
        case "inline_bold":
            return isinstance(obj, inline_bold)
        case "table":
            return isinstance(obj, table)
        case _:
            return False

# Define RAW_DIR constant
RAW_DIR = (Path(__file__).resolve().parent           # api/
        / 'static' / 'assets' / 'raw').resolve()

#Define CONTEXT_DIR constant
CONTEXT_DIR = (Path(__file__).resolve().parent           # api/
        / 'static' / 'assets' / 'context').resolve()

#Define BRIEFS_DIR constant
BRIEFS_DIR = (Path(__file__).resolve().parent           # api/
        / 'static' / 'assets' / 'briefs').resolve()

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

def load_raw_text(filename: str, encoding: str = "utf-8") -> str:
    """
    Return the full text of one raw report found in RAW_DIR.

    Parameters
    ----------
    filename : str
        The exact basename, e.g. "<sector>_Brief_2025-07-11_raw.txt".
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

def load_context_text(context_filename: str, encoding: str = "utf-8") -> str:
    # Your existing load_raw_text reads only from RAW_DIR; context lives elsewhere.
    safe_name = Path(context_filename).name
    file_path = CONTEXT_DIR / safe_name
    if not file_path.is_file():
        raise FileNotFoundError(f"No context file named {safe_name!r} in {CONTEXT_DIR}")
    return file_path.read_text(encoding=encoding)


# Add check_type function to Jinja environment
app.jinja_env.globals['check_type'] = check_type

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
        """Check if basic user can change their sector (resets every Monday)"""
        if self.premium_status != 'basic' or not self.sector_changed_at:
            return True  # Premium users or first-time selection

        today_utc = datetime.utcnow().date()
        last_change = self.sector_changed_at.date()

        # If same day, no change
        if today_utc == last_change:
            return False

        # Find most recent Monday before or equal to today
        last_monday = today_utc - timedelta(days=today_utc.weekday())

        # User can change if last change was before this Monday
        return last_change < last_monday

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
    briefs_folder = os.path.join(app.static_folder, 'assets', 'briefs')

    if briefs_folder:
        # Get all PDF files in the briefs folder
        pdf_files = glob.glob(briefs_folder +'/*.pdf')
        
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
                elif len(parts) == 4:
                    region = parts[0]
                    sector = parts[1]
                    date_str = parts[3]
                    title = f"{region} {sector} Brief - {date_str}"
                    report_id = len(reports) + 1

                    reports.append({
                        'id': report_id,
                        'title': title,
                        'date': date_str,
                        'sector': sector,
                        'region': region,
                        'filename': filename,
                        'summary': f'Latest {region} {sector} sector analysis and market insights.',
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

@app.route('/ai-chat-select', methods=['GET', 'POST'])
@login_required
def ai_chat_select():
    """AI Chat selection page"""
    form = AIChatSelectionForm()
    
    # Handle region parameter from URL
    region = request.args.get('region', 'global')
    if request.method == 'GET':
        form.region.data = region
    
    if form.validate_on_submit():
        sector = form.sector.data
        date = form.date.data.strftime('%Y-%m-%d')
        region = form.region.data
        
        # Check if user has access to AI chat
        if current_user.has_valid_premium and (current_user.premium_status == 'premium' or current_user.premium_status == 'max'):
            # Check if report exists before allowing access
            if region and region != 'global':
                raw_filename = f"{region}_{sector}_Brief_{date}_raw.txt"
            else:
                raw_filename = f"{sector}_Brief_{date}_raw.txt"
            try:
                safe_name = Path(raw_filename).name
                file_path = RAW_DIR / safe_name
                if not file_path.is_file():
                    flash(f'No report available for {sector} sector on {date} in {region} region. Please select a date with an available report.', 'error')
                    return redirect(url_for('ai_chat_select'))
            except Exception:
                flash(f'Unable to verify report availability for {sector} sector on {date} in {region} region. Please try again.', 'error')
                return redirect(url_for('ai_chat_select'))
            
            return redirect(url_for('LLM_chat', sector=sector, date=date, region=region))
        else:
            flash('AI Chat is only available for Premium and Max plan users. Please upgrade your subscription to access this feature.', 'error')
            return redirect(url_for('ai_chat_select'))
    
    return render_template('ai_chat_select.html', form=form)

@app.route('/favicon.ico')
def favicon():
    """Serve favicon.ico from assets/pictures folder"""
    try:
        # Serve favicon.ico from the assets/pictures folder
        return send_from_directory(os.path.join(app.static_folder, 'assets', 'pictures'), 'favicon.ico')
    except Exception as e:
        print(f"Favicon error: {e}")
        # If favicon file doesn't exist, return no content
        return '', 204

@app.route('/features')
def features():
    """Features page"""
    return render_template('features.html')

@app.route('/pricing')
def pricing():
    """Pricing page"""
    return render_template('pricing.html')


@app.route('/sample')
def sample():
    """Sample report page"""
    return render_template('sample.html')

@app.route('/client')
def client():
    """Client index page"""
    return render_template('client_index.html')

@app.route('/contacts')
def contacts():
    """Contacts Page"""
    return render_template('contacts.html')

@app.route('/reports')
@login_required
def reports():
    """Reports page"""
    return render_template('reports.html', user=current_user)

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
    return redirect('/')

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
                'premium_expires_at': current_user.premium_expires_at.strftime('%Y-%m-%d') if current_user.premium_expires_at else None,
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
        
        # Create new user with no premium status
        user = User(
            username=username, 
            password=password,
            premium_status='none',
            premium_expires_at=None
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

@app.route('/payment')
@login_required
def payment_page():
    """Payment page"""
    return render_template('payment.html')

@app.route('/api/verify-payment', methods=['POST'])
@login_required
def verify_payment():
    """Verify payment endpoint"""
    data = request.get_json()
    plan = data.get('plan')
    price = data.get('price')
    payment_method = data.get('paymentMethod')
    
    if not plan or not price or not payment_method:
        return jsonify({'success': False, 'error': 'Missing payment information'}), 400
    
    try:
        # Update user's premium status based on the plan
        if plan == 'basic':
            current_user.premium_status = 'basic'
        elif plan == 'premium':
            current_user.premium_status = 'premium'
        elif plan == 'max':
            current_user.premium_status = 'max'
        
        # Set expiration date (30 days from now)
        current_user.premium_expires_at = datetime.utcnow() + timedelta(days=30)
        
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': f'Payment verified! Your {plan} plan is now active for 30 days.'
        })
    except Exception as e:
        db.session.rollback()
        print(f"Payment verification error: {e}")
        return jsonify({'success': False, 'error': 'Database error'}), 500

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
    
    if sector not in ['TMT', 'Energy', 'Healthcare', 'Consumer', 'Industry']:
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


# Render brief on webpage with sector and date parameters
@app.route('/api/briefRenderTest/<sector>/<date>')
@app.route('/api/briefRenderTest/<sector>/<date>/<region>')
def renderTest(sector, date, region = None):
    try:
        # Construct the raw filename based on sector and date
        if region:
            raw_filename = f"{region}_{sector}_Brief_{date}_raw.txt"
            raw_path = RAW_DIR / raw_filename
        else:
            raw_filename = f"{sector}_Brief_{date}_raw.txt"
            raw_path = RAW_DIR / raw_filename
        
        if not raw_path.exists():
            return f"No raw brief found for {sector} sector on {date}.", 404
        
        raw = load_raw_text(raw_filename)
        structured = parse(raw)
    except Exception as e:
        app.logger.exception("Error parsing raw brief")   # logs full traceback
        return "Error parsing raw brief", 500
    #conv = get_or_create_conversation(current_user.id, sector, date)
    #history = fetch_history_for_ui(conv["_id"], limit=200)
    return render_template("renderTest.html", sections=structured, date=date, sector=sector, term_definitions=TERM_DEFINITIONS)

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

@app.route('/demo/assets/briefs/<filename>')
def serve_demo_brief_report(filename):
    """Serve brief report files for demo purposes - no authentication required"""
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




def build_system_prompt(sector: str, date: str, region: str | None = None) -> str:
    """
    System prompt for SOURCE-ONLY daily recap + light inference.
    Focus: "what happened today" + simple numeric reasoning strictly from SOURCES.
    """
    if region:
        raw_filename = f"{region}_{sector}_Brief_{date}_raw.txt"
        context_filename = f"{region}_{sector}_context_{date}.txt"
    else:
        raw_filename = f"{sector}_Brief_{date}_raw.txt"
        context_filename = f"{sector}_context_{date}.txt"

    raw = load_raw_text(raw_filename)
    context = load_context_text(context_filename)

    manual = f"""
    ROLE & HARD GROUNDING (MANDATORY)
    - Answer using the SOURCES below (REPORT + CONTEXT) paired with your existing knowledge on finance and the stock market.
    - Treat “today” as “events described in SOURCES”.
    - When asked about information on companies, refer to the "Company info for companies mentioned in news" section in context block
    - If a requested fact is missing, AND you can not work it out with existing information, state that you cannot answer that question and why(and stop; do not invent data).

    ANSWERING PRIORITY
    1) Prefer REPORT for recap; use CONTEXT only for details or numbers not shown in REPORT.
    2) Keep answers concise, number-first, and professional (banker brief tone).
    3) Use a small table when listing multiple items or rationales.

    ALLOWED MATH & INFERENCES (LIGHT ONLY)
    - You may compute from numbers **present in SOURCES**: +/- deltas, % change, simple ratios, rank comparisons (higher/lower), and direction-of-change.
    - You may state immediate implications that are **explicitly supported** by SOURCES (e.g., “premium vs unaffected,” “above/below peer avg,” “trend up/down”).
    - Do **not** project beyond the given period; no forecasts, no unstated comps.
    - Tag any qualitative bridge as **Inference** and still anchor to the exact quoted numbers with citations.

    MISSING / CONFLICTING DATA
    - If multiple values conflict, pick the value in REPORT; if absent there, pick the most recent in CONTEXT and note **(latest in CONTEXT)**.
    - If a value is unavailable, respond: **Not in SOURCES**.

    FORMATTING RULES
    - Use ** ** for inline bold.
    - Tables:
    | A | B |
    | --- | --- |
    | a1 | b1 |
    - Keep outputs compact (< ~500–800 tokens unless asked for more).

    ===============================================================================
    RECAP (DEFAULT FOR “WHAT HAPPENED TODAY?”)
    INSTRUCTIONS
    - Return 3–6 bullets. Each bullet must contain **at least one number** (size, multiple, premium, growth, guidance change, etc.) and a short “why it matters” clause. **[cite]**
    - Order by materiality (deal size, sector impact). **[cite]**
    - If useful, include one small rationale table.

    OUTPUT SKELETON
    **{region} {sector} Daily — {date}**
    - **Item**: number(s) + concise significance. **[cite]**
    - Brief summary on deals, listing key details like "Buyer", "EV", "Multiples", "Date announced" **[cite]**
    - Rational & Implications (as a table)
    | **Rationale Type** | **Details** |
    | --- | --- |
    | Strategic | … |
    | Financial | … |
    | Market | … |

    **Interview prep:**
    **Summary:** 1 line on deals happened today.
    **So what:** 1 line on sector implication.

    **Talking points:**
    - (as a list) Example: Attractive entry: 10x vs sector 12x.

    **(Repeat for deal 2 if exists)**

    ===============================================================================
    FACT LOOKUP (WHEN ASKED A DIRECT QUESTION)
    INSTRUCTIONS
    - Answer with the exact figure(s) from SOURCES in one tight sentence. **[cite]**
    - If missing: **Not in SOURCES**.

    EXAMPLE
    - “Implied EV/EBITDA was **~17x**. **[cite]**”
    - “Premium to unaffected was **~25%**. **[cite]**”
    
    - When asked "What information do you have on **company name**?"
        - Look at the "Company info for companies mentioned in news" sections in context for information

    ===============================================================================
    LIGHT INFERENCE Q&A (WHEN ASKED FOR SIMPLE REASONING)
    INSTRUCTIONS
    - Do minimal, explicit math only from given numbers, and label the bridge as **Inference**.
    - Show the computed value inline (e.g., “+18% YoY based on 120 vs 102”). **[cite]**
    - Keep to 2–4 short bullets.

    ===============================================================================
    PREDICTIONS (WHEN ASKED QUESTIONS LIKE "If inflation stays sticky, what happens to equities?")
    OUTPUT SKELETON
    - **Fact(s):** <quoted numbers>. **[cite]**
    - **Inference:** (You may decide how long it should be, depending on the complexity of the question, as long as you follow the formatting guidelines)
    - **Supportive evidence:** (You may use cases from your existing knowledge base to support your claim)

    ===============================================================================
    SOURCES (READ-ONLY)
    REPORT (summarized daily brief):
    {raw}

    CONTEXT (articles used to write the report):
    {context}
    """
    
    return manual.replace("{SECTOR}", sector.upper()).replace("{DATE}", date)


def get_or_create_conversation(user_id: int, sector: str, date: str, region):
    if region:
        slug = f"{region}_{sector}_Brief_{date}"
    else:
        slug = f"{sector}_Brief_{date}"
    conv = app.conversations.find_one({
        "user_id": str(user_id),
        "report_id": slug,
        "status": "open"
    })
    if conv:
        return conv

    # Check if this is a demo conversation (no sector/date files)
    is_demo = False
    try:
        safe_name = Path(slug + "_raw.txt").name
        file_path = RAW_DIR / safe_name
        if not file_path.is_file():
            is_demo = True
    except Exception:
        is_demo = True

    if is_demo:
        # Demo conversation with generic TMT system prompt
        system_prompt = """You are a specialized AI assistant for Technology, Media & Telecommunications (TMT) industry insights. 
        
Your expertise covers:
- Market analysis and sector trends
- M&A activity and deal insights  
- Valuation analysis and multiples
- Investment preparation and pitch angles
- Industry news and developments

Provide detailed, professional responses with:
- Relevant data and statistics when available
- Clear explanations of complex concepts
- Practical insights for investors and professionals
- Professional tone with industry terminology

Keep responses focused on TMT sector relevance."""
        
        # Use demo slug for demo conversations
        slug = f"Demo_Chat_{user_id}"
    else:
        # Real sector conversation with report-specific system prompt
        system_prompt = build_system_prompt(sector, date, region)

    conv = {
        "user_id": str(user_id),
        "report_id": slug,
        "title": f"Q&A: {slug}" if not is_demo else f"Demo Chat: TMT AI Assistant",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "message_count": 0,
        "running_summary": "",
        "system_prompt": system_prompt,                    # store once
        "system_hash": md5(system_prompt.encode()).hexdigest(),
        "status": "open"
    }
    conv["_id"] = app.conversations.insert_one(conv).inserted_id
    # Remove this redundant greeting message
    # greeting_message = f"""Hello! I'm your TMT Bot for {sector} sector analysis. I can help you understand market trends, analyze reports, and answer questions about Energy developments. What would you like to know?"""
    # append_message(conv["_id"], user_id, "assistant", greeting_message)
    
    # Add greeting message for new conversations
    if is_demo:
        greeting_content = "Hello! I'm TMT Bot. I can help you understand market trends, analyze reports, and answer questions about TMT developments. What would you like to know?"
    else:
        greeting_content = f"Hello! I'm your AI assistant for {sector} sector analysis. I can help you understand market trends, analyze reports, and answer questions about {sector} developments. What would you like to know?"
    
    append_message(conv["_id"], user_id, "assistant", greeting_content)
    
    return conv

def append_message(conversation_id: ObjectId, user_id: int, role: str, content: str):
    doc = {
        "conversation_id": ObjectId(conversation_id),
        "user_id": str(user_id),
        "role": role,
        "content": content,
        "created_at": datetime.utcnow(),
    }
    app.messages.insert_one(doc)
    app.conversations.update_one(
        {"_id": ObjectId(conversation_id)},
        {"$inc": {"message_count": 1}, "$set": {"updated_at": datetime.utcnow()}}
    )
    return doc

def fetch_last_context(conversation_id: ObjectId, k: int = 8):
    cur = (app.messages.find({"conversation_id": ObjectId(conversation_id)})
           .sort("created_at", -1).limit(k))
    msgs = list(cur)[::-1]  # chronological
    return msgs

def _serialize_msg(doc):
    return {
        "id": str(doc["_id"]),
        "role": doc["role"],
        "content": doc["content"],
        "created_at": doc["created_at"].isoformat() + "Z",
    }


def fetch_history_for_ui(conversation_id: ObjectId, limit: int = 200, before: datetime | None = None):
    q = {"conversation_id": ObjectId(conversation_id), "role": {"$in": ["user", "assistant"]}}
    if before:
        q["created_at"] = {"$lt": before}
    cur = (app.messages.find(q).sort("created_at", 1).limit(limit))  # oldest→newest for display
    return [_serialize_msg(m) for m in cur]

def handle_chat_turn(user_id: int, sector: str, date: str, user_msg: str, region=None):
    conv_key = f"conv:{user_id}:{sector}:{date}:{region or 'global'}"
    conv_id = session.get(conv_key)
    conv = app.conversations.find_one({"_id": ObjectId(conv_id), "status": "open"}) if conv_id else None
    if not conv:
        conv = get_or_create_conversation(user_id, sector, date, region)
        session[conv_key] = str(conv["_id"])

    user_msg = (user_msg or "").strip()
    if not user_msg:
        return fetch_history_for_ui(conv["_id"], limit=200)

    # --- Idempotency: drop exact resubmits of the last user message ---
    last = app.messages.find_one(
        {"conversation_id": ObjectId(conv["_id"])},
        sort=[("created_at", -1)]
    )
    if last and last.get("role") == "user" and last.get("content") == user_msg:
        # Don't re-append or re-answer on exact replay
        return fetch_history_for_ui(conv["_id"], limit=200)
    # ------------------------------------------------------------------

    append_message(conv["_id"], user_id, "user", user_msg)

    last_k = fetch_last_context(conv["_id"], k=12)
    prompt_msgs = [{"role": "system", "content": conv.get("system_prompt", "")}]
    for m in last_k:
        prompt_msgs.append({"role": m["role"], "content": m["content"]})

    try:
        client = openai.Client(
            api_key=OPENAI_API_KEY,
            base_url=API2D_BASE_URL,
            http_client=httpx.Client(timeout=httpx.Timeout(300.0),
                                     limits=httpx.Limits(max_connections=5, max_keepalive_connections=5))
        )
        resp = client.chat.completions.create(model="gpt-4o-mini",
                                              messages=prompt_msgs,
                                              temperature=0.3,
                                              max_tokens=5000)
        assistant_reply = resp.choices[0].message.content.strip()
    except openai.APIConnectionError as e:
        print(f"API2D Connection Error: {e}")
        assistant_reply = "Sorry, I'm having trouble connecting to the AI service. Please check your internet connection and try again."
    except openai.AuthenticationError as e:
        print(f"API2D Authentication Error: {e}")
        assistant_reply = "Sorry, there's an authentication issue with the AI service. Please check your API key."
    except Exception as e:
        print(f"API2D Error: {e}")
        assistant_reply = "Sorry, there was an error processing your request. Please try again."
    append_message(conv["_id"], user_id, "assistant", assistant_reply)

    return fetch_history_for_ui(conv["_id"], limit=200)

class ChatForm(FlaskForm):
    message = StringField("Message", validators=[DataRequired()], render_kw={"placeholder": "Type your question…"})
    submit = SubmitField("Send")

class AIChatSelectionForm(FlaskForm):
    sector = SelectField("Sector", validators=[DataRequired()], choices=[
        ("", "Choose a sector..."),
        ("TMT", "TMT (Technology, Media & Telecommunications)"),
        ("Healthcare", "Healthcare & Life Sciences"),
        ("Energy", "Energy & Natural Resources"),
        ("Consumer", "Consumer & Retail"),
        ("Industry", "Industrial & Manufacturing")
    ])
    date = DateField("Date", validators=[DataRequired()], format='%Y-%m-%d')
    region = SelectField("Region", validators=[DataRequired()], choices=[
        ("", "Choose a region..."),
        ("US", "United States"),
        ("Europe", "European Union")
    ])
    submit = SubmitField("Start AI Chat")

@app.route('/clear/<sector>/<date>/', methods=['POST'])
@app.route('/clear/<sector>/<date>/<region>/', methods=['POST'])
@login_required
def clear_chat_history(sector, date, region=None):
    """Clear chat history for a specific conversation"""
    try:
        user_id = current_user.id if getattr(current_user, "is_authenticated", False) else 0
        
        # Get the conversation
        conv_key = f"conv:{user_id}:{sector}:{date}:{region or 'global'}"
        conv_id = session.get(conv_key)
        
        if conv_id:
            # Delete all messages for this conversation
            app.messages.delete_many({"conversation_id": ObjectId(conv_id)})
            
            # Clear the session key
            session.pop(conv_key, None)
            return jsonify({"success": True, "message": "Chat history cleared successfully"})
        else:
            # Fallback: try to find conversation in database
            if region and region != 'global':
                slug = f"{region}_{sector}_Brief_{date}"
            else:
                slug = f"{sector}_Brief_{date}"
            conv = app.conversations.find_one({
                "user_id": str(user_id),
                "report_id": slug,
                "status": "open"
            })
            
            if conv:
                # Delete all messages for this conversation
                app.messages.delete_many({"conversation_id": conv["_id"]})
                
                # Store the conversation ID in session for future use
                session[conv_key] = str(conv["_id"])
                
                return jsonify({"success": True, "message": "Chat history cleared successfully"})
            else:
                return jsonify({"success": False, "message": "Conversation not found"}), 404
            
    except Exception as e:
        return jsonify({"success": False, "message": "An error occurred while clearing chat history"}), 500

@app.route('/api/LLM_chat/<sector>/<date>/<region>/send', methods=['POST'])
@app.route('/api/LLM_chat/<sector>/<date>/send', methods=['POST'])
@login_required
def send_chat_message(sector, date, region = None):
    """Send a chat message via AJAX and return the response"""
    import time
    from datetime import datetime
    from flask import Response, stream_with_context
    
    request_start_time = time.time()
    request_id = request.headers.get('X-Request-ID', f"server_{int(time.time() * 1000)}")
    
    try:
        # Parse request data
        user_id = current_user.id if getattr(current_user, "is_authenticated", False) else 0
        data = request.get_json()
        user_msg = data.get('message', '').strip()
        
        if not user_msg:
            return jsonify({"success": False, "message": "Message cannot be empty"}), 400
        
        # Process the chat turn with streaming
        
        def generate_stream():
            try:
                # Get conversation and append user message
                conv_key = f"conv:{user_id}:{sector}:{date}:{region or 'global'}"
                conv_id = session.get(conv_key)
                conv = app.conversations.find_one({"_id": ObjectId(conv_id), "status": "open"}) if conv_id else None
                if not conv:
                    conv = get_or_create_conversation(user_id, sector, date, region)
                    session[conv_key] = str(conv["_id"])

                # Idempotency check
                last = app.messages.find_one(
                    {"conversation_id": ObjectId(conv["_id"])},
                    sort=[("created_at", -1)]
                )
                if last and last.get("role") == "user" and last.get("content") == user_msg:
                    yield f"data: {json.dumps({'type': 'error', 'message': 'Duplicate message detected'})}\n\n"
                    return

                append_message(conv["_id"], user_id, "user", user_msg)

                # Prepare context for AI
                last_k = fetch_last_context(conv["_id"], k=12)
                prompt_msgs = [{"role": "system", "content": conv.get("system_prompt", "")}]
                for m in last_k:
                    prompt_msgs.append({"role": m["role"], "content": m["content"]})

                # Send initial status
                yield f"data: {json.dumps({'type': 'status', 'message': 'Connecting to AI model...'})}\n\n"
                
                try:
                    client = openai.Client(
                        api_key=OPENAI_API_KEY,
                        base_url=API2D_BASE_URL,
                        http_client=httpx.Client(timeout=httpx.Timeout(300.0),
                                                 limits=httpx.Limits(max_connections=5, max_keepalive_connections=5))
                    )
                    
                    # Use streaming API
                    stream = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=prompt_msgs,
                        temperature=0.3,
                        max_tokens=5000,
                        stream=True
                    )
                    
                    assistant_reply = ""
                    
                    # Send status update
                    yield f"data: {json.dumps({'type': 'status', 'message': 'Generating response...'})}\n\n"
                    
                    # Stream the response
                    for chunk in stream:
                        if chunk.choices[0].delta.content is not None:
                            content = chunk.choices[0].delta.content
                            assistant_reply += content
                            yield f"data: {json.dumps({'type': 'content', 'content': content})}\n\n"
                    
                    # Check if response was cut off (only check the final complete response)
                    if assistant_reply.strip() and not assistant_reply.strip().endswith(('.', '!', '?', ':', ';')):
                        print(f"[{request_id}] ⚠️ WARNING: Response appears cut off mid-sentence!")
                    
                    # Check for incomplete tables
                    if assistant_reply.strip() and '|' in assistant_reply and not assistant_reply.strip().endswith('|'):
                        print(f"[{request_id}] ⚠️ WARNING: Response appears to have incomplete table!")
                    
                    # Check for incomplete markdown formatting
                    if assistant_reply.strip():
                        open_bold = assistant_reply.count('**') % 2
                        open_headers = assistant_reply.count('#') - assistant_reply.count('\n#')
                        if open_bold != 0 or open_headers > 0:
                            print(f"[{request_id}] ⚠️ WARNING: Response has incomplete markdown formatting!")
                    
                    # Send completion signal
                    yield f"data: {json.dumps({'type': 'complete', 'full_response': assistant_reply})}\n\n"
                    
                    # Save the complete response to database
                    append_message(conv["_id"], user_id, "assistant", assistant_reply)
                    
                except openai.APIConnectionError as e:
                    error_msg = "Sorry, I'm having trouble connecting to the AI service. Please check your internet connection and try again."
                    yield f"data: {json.dumps({'type': 'error', 'message': error_msg})}\n\n"
                    append_message(conv["_id"], user_id, "assistant", error_msg)
                except openai.AuthenticationError as e:
                    error_msg = "Sorry, there's an authentication issue with the AI service. Please check your API key."
                    yield f"data: {json.dumps({'type': 'error', 'message': error_msg})}\n\n"
                    append_message(conv["_id"], user_id, "assistant", error_msg)
                except openai.RateLimitError as e:
                    error_msg = "Sorry, the AI service is experiencing high demand. Please try again in a moment."
                    yield f"data: {json.dumps({'type': 'error', 'message': error_msg})}\n\n"
                    append_message(conv["_id"], user_id, "assistant", error_msg)
                except openai.APITimeoutError as e:
                    error_msg = "Sorry, the AI service took too long to respond. This may indicate high server load."
                    yield f"data: {json.dumps({'type': 'error', 'message': error_msg})}\n\n"
                    append_message(conv["_id"], user_id, "assistant", error_msg)
                except Exception as e:
                    error_msg = "Sorry, there was an error processing your request. Please try again."
                    yield f"data: {json.dumps({'type': 'error', 'message': error_msg})}\n\n"
                    append_message(conv["_id"], user_id, "assistant", error_msg)
                
            except Exception as e:
                error_msg = f"Streaming error: {str(e)}"
                yield f"data: {json.dumps({'type': 'error', 'message': error_msg})}\n\n"
        
        return Response(stream_with_context(generate_stream()), 
                       mimetype='text/event-stream',
                       headers={
                           'Cache-Control': 'no-cache',
                           'Connection': 'keep-alive',
                           'Access-Control-Allow-Origin': '*',
                           'Access-Control-Allow-Headers': 'Cache-Control'
                       })
        
    except Exception as e:
        return jsonify({"success": False, "message": "An error occurred while processing your message"}), 500





@dataclass
class generic:
    content: str

@dataclass
class inline_bold:
    content: str

# include `table` here
message_element = Union[generic, inline_bold, table]

@dataclass
class message:
    role: str
    content: List[message_element]

@dataclass
class line_block:
    lines: List[str]  # raw lines (no trailing \n), may contain inline bold pats

@dataclass
class table_block:
    lines: List[str]  # contiguous lines of a table

block = Union[line_block, table_block]


INLINE_BOLD_PAT = re.compile(r'^(.*?)(?:\*\*|@@)(.+?)(?:\*\*|@@)(.*)$')

def is_table_line(line: str) -> bool:
    return bool(TABLE_ROW_PAT.match(line)) or bool(TABLE_SEP_PAT.match(line))

def parse_LLM_message(history: List[dict]):
    result: List[message_element] = []

    for item in history:
        role = item["role"]
        raw_content = item["content"] if isinstance(item["content"], str) else "\n".join(item["content"])
        lines = raw_content.splitlines(keepends = True)

        elements : List[block] = []
        i, n = 0, len(lines)


        while i < n:
            if is_table_line(lines[i]):
                j = i
                table_lines : List[str] = []
                while j < n and is_table_line(lines[j]):
                    table_lines.append(lines[j].rstrip("\n"))
                    j += 1
                elements.append(table_block(table_lines))
                i = j
            else:
                j = i
                generic_lines : List[str] = []
                while j < n and not is_table_line(lines[j]):
                    generic_lines.append(lines[j].rstrip("\n"))
                    j += 1
                elements.append(line_block(generic_lines))
                i = j
        
        tokens : List[message_element]= []
        for e in elements:
            if isinstance(e, line_block):
                for index, line in enumerate(e.lines):
                    tokens.extend(render_generic_line(line))
                    if index < len(e.lines) - 1:
                        tokens.append(generic("\n"))
            else:
                tokens.append(render_table(e.lines))

        result.append(message(role=role, content=tokens))

    return result


def render_generic_line(line: str):
    tokens: List[message_element] = []
    rest = line
    while True:
        m = INLINE_BOLD_PAT.match(rest)
        if not m:
            if rest:
                tokens.append(generic(rest))
            break
        lhs, bold, rhs = m.group(1), m.group(2), m.group(3)
        if lhs:
            tokens.append(generic(lhs))
        tokens.append(inline_bold(bold))
        rest = rhs  # keep scanning RHS for more bolds
    return tokens









# @app.route('/test', methods=['GET', 'POST'])
# def test():
#     print("test Function called")
#     return render_template('pricing.html')

#Example: 127.0.0.1:5000/api/LLM_chat/TMT/2025-08-20
@app.route('/api/LLM_chat/<sector>/<date>', methods=['GET', 'POST'])
@app.route('/api/LLM_chat/<sector>/<date>/<region>', methods=['GET', 'POST'])
def LLM_chat(sector, date, region=None):
    form = ChatForm()
    user_id = current_user.id if getattr(current_user, "is_authenticated", False) else 0

    # Check if report files exist
    if region and region != 'global':
        raw_filename = f"{region}_{sector}_Brief_{date}_raw.txt"
        context_filename = f"{region}_{sector}_context_{date}.txt"
        pdf_filename = f"{region}_{sector}_Brief_{date}.pdf"
    else:
        raw_filename = f"{sector}_Brief_{date}_raw.txt"
        context_filename = f"{sector}_context_{date}.txt"
        pdf_filename = f"{sector}_Brief_{date}.pdf"
    
    try:
        # Check if raw file exists
        safe_name = Path(raw_filename).name
        file_path = RAW_DIR / safe_name
        if not file_path.is_file():
            flash(f'No report available for {sector} sector on {date} in {region or "global"} region. Please select a date with an available report.', 'error')
            return redirect(url_for('ai_chat_select'))
    except Exception:
        flash(f'Unable to verify report availability for {sector} sector on {date} in {region or "global"} region. Please try again.', 'error')
        return redirect(url_for('ai_chat_select'))
    
    # Check if PDF file exists, if not set pdf_filename to None
    try:
        pdf_safe_name = Path(pdf_filename).name
        pdf_file_path = BRIEFS_DIR / pdf_safe_name
        if not pdf_file_path.is_file():
            pdf_filename = None
    except Exception:
        pdf_filename = None

    # ensure conversation exists
    conv = get_or_create_conversation(user_id, sector, date, region)

    if request.method == 'POST' and form.validate_on_submit():
        msg = (form.message.data or '').strip()
        if msg:
            handle_chat_turn(user_id, sector, date, msg, region)
        # PRG: prevent duplicate on refresh
        return redirect(url_for('LLM_chat', sector=sector, date=date, region=region))
    
    # GET branch: just read and render
    history = fetch_history_for_ui(conv["_id"], limit=200)
    
    return render_template("LLM_chat.html",
                           history=history,
                           sector=sector,
                           date=date,
                           region=region,
                           pdf_filename=pdf_filename,
                           form=form)

# Route to serve PDF files
@app.route('/api/pdf/<sector>/<date>')
@app.route('/api/pdf/<sector>/<date>/<region>')
def serve_pdf(sector, date, region = None):
    if region:
        pdf_filename = f"{region}_{sector}_Brief_{date}.pdf"
    else:
        # If no region specified, try to find a region-specific file
        # Search for common regions: US, Europe, etc.
        possible_regions = ['US', 'Europe']
        pdf_filename = None
        
        for possible_region in possible_regions:
            test_filename = f"{possible_region}_{sector}_Brief_{date}.pdf"
            test_safe_name = Path(test_filename).name
            test_file_path = BRIEFS_DIR / test_safe_name
            
            if test_file_path.is_file():
                pdf_filename = test_filename
                break
        
        # If no region-specific file found, try the original format
        if not pdf_filename:
            pdf_filename = f"{sector}_Brief_{date}.pdf"
        
    safe_name = Path(pdf_filename).name
    file_path = BRIEFS_DIR / safe_name
    
    if not file_path.is_file():
        # Return a more graceful 404 response without logging as error
        return "PDF not found", 404
    
    return send_from_directory(BRIEFS_DIR, safe_name, mimetype='application/pdf')


#use for demo afterwards
@app.route('/api/LLM_Chat_Demo', methods = ['GET'])
def LLM_Chat_Demo():
    history = []

    history = parse_LLM_message(history)
    return render_template("LLM_Chat_Demo.html", history = history)

#Stock Pitch demo
@app.route('/api/LLM_Chat_Pitch_Demo', methods = ['GET'])
def LLM_Pitch_Demo():
    history = []

    history = parse_LLM_message(history)
    return render_template("LLM_Pitch_Demo.html", history = history)

def load_city_config():
    """Load city configuration from JSON file"""
    config_file = os.path.join(app.static_folder, 'data', 'city_config.json')
    with open(config_file, 'r') as f:
        return json.load(f)

@app.route('/map')
def map_page():
    """Map page showing investment banks"""
    # Default to NYC
    city = request.args.get('city', 'nyc')
    
    # Load city configuration from JSON file
    city_config = load_city_config()
    
    # Get city configuration
    config = city_config.get(city, city_config['nyc'])
    
    # Load the banks data for the selected city
    banks_file = os.path.join(app.static_folder, 'data', config['file'])
    with open(banks_file, 'r') as f:
        banks_data = json.load(f)
    
    # Get Google Maps API key from environment
    google_maps_api_key = os.environ.get('GOOGLE_MAP_API', '')
    
    return render_template('map.html', 
                         banks=banks_data, 
                         google_maps_api_key=google_maps_api_key,
                         city_config=city_config,
                         current_city=city,
                         current_config=config)

@app.route('/api/banks/<city>')
def get_banks_for_city(city):
    """API endpoint to get banks data for a specific city"""
    # Load city configuration from JSON file
    city_config = load_city_config()
    
    # Get city configuration
    config = city_config.get(city, city_config['nyc'])
    
    # Load the banks data for the selected city
    banks_file = os.path.join(app.static_folder, 'data', config['file'])
    with open(banks_file, 'r') as f:
        banks_data = json.load(f)
    
    return jsonify({
        'banks': banks_data,
        'config': config
    })


if __name__ == '__main__':
    init_db()
    init_mongo()
    app.run(debug=True, use_reloader=False, host='0.0.0.0', port=5000)

#test for previewW
