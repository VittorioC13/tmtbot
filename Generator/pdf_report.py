from fpdf import FPDF
import re
from datetime import datetime
from pathlib import Path

sec_pat    = re.compile(r'^###\s*(\d+)\.\s+(.*)$')                       # "### 1. …"
bold_line_pat = re.compile(r'^@{3}\s+(?P<h3_lbl>.+?)\s*$')                    # @@@ text
underline_pat = re.compile(r'^@{4}\s+(?P<u_lbl>.+?)\s*$')   # "@@@@ Heading"
link_pat   = re.compile(r'\*\*(?P<title>.+?)\*\*\s*\(\s*\[Link\]\((?P<url>https?://[^\s)]+)\)\s*\)') #links
bullet_pat = re.compile(r'^[\*\-\•]\s+\*\*(.+?)\*\*\s*(.*)$')            # "- **Deal Size:** foo"
body_pat   = re.compile(r'^[A-Za-z0-9\-\s\.:,;]*$')                      # generic body
sub_pat = re.compile(r'^(?:\*\*(.+?)\*\*:?\s*$|####\s+(.+?)\s*$)')        # **title:** style)



class PDF(FPDF):
    def __init__(self):
        super().__init__()
        # Set margins (left, top, right) in mm
        self.set_margins(15, 15, 15)
        self.set_auto_page_break(auto=True, margin=15)
        self.title = None
        
    def set_title(self, title):
        self.title = title

    def ensure_space(self, needed: float) -> None:
        """
        Ensure there is at least *needed* vertical space left on the
        current page; otherwise start a new page.
        """
        remaining = self.h - self.b_margin - self.get_y()
        if remaining < needed:
            self.add_page()
        
    def header(self):
        """Enhanced header with better formatting"""
        if self.title:
            # Main title
            self.set_font('Helvetica', 'B', 16)  # Larger, bold font
            self.set_text_color(0, 0, 0)  # Black text
            self.cell(0, 12, self.title, 0, 1, 'C')
            
            # Subtitle
            self.set_font('Helvetica', 'I', 11)
            self.set_text_color(100, 100, 100)  # Dark gray text
            self.cell(0, 6, 'Technology, Media & Telecommunications Sector', 0, 1, 'C')
            
            # Reset text color
            self.set_text_color(0, 0, 0)
            self.ln(8)
        
    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, title):
        """Enhanced chapter title with bold formatting, shading, and better spacing"""
        PRE   = 8    # ln(8) before bar
        BAR   = 12   # height of shaded bar
        POST  = 6    # ln(6) after bar
        self.ensure_space(PRE + BAR + POST)

        title = clean_text_for_pdf(title)
        self.ln(8)  # Add space before title
        
        # Set up the title formatting
        self.set_font('Helvetica', 'B', 14)  # Bold, larger font
        
        # Calculate title dimensions
        title_width = self.get_string_width(title) + 20  # Add padding
        title_height = 12  # Height for the shaded area
        title_x = self.l_margin
        title_y = self.get_y()
        
        # Draw shaded background rectangle
        self.set_fill_color(220, 220, 220)  # Light gray background
        self.rect(title_x, title_y, title_width, title_height, 'F')
        
        # Add the title text on top of the background
        self.set_text_color(0, 0, 0)  # Black text
        self.set_xy(title_x + 5, title_y + 2)  # Position text with padding
        self.cell(title_width - 10, title_height - 4, title, 0, 0, 'L')
        
        # Move to next line after title
        self.set_xy(self.l_margin, title_y + title_height + 4)
        
        # Add a subtle line under the title
        self.set_line_width(0.5)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(6)  # Add space after line

    def subsection_title(self, title: str) -> None:
        """Subsection title with bold formatting, shading, and smaller font than chapter_title.
        If there isn’t enough space on the current page, automatically add a new page.
        """
        title = clean_text_for_pdf(title)

        # ----- 0.  how much vertical room do we need? -----
        TITLE_HEIGHT   = 10            # shaded bar
        PRE_PADDING    = 4             # self.ln(4) before title
        POST_PADDING   = 2             # self.ln(2) after title
        needed_space   = PRE_PADDING + TITLE_HEIGHT + POST_PADDING

        # remaining space to bottom margin
        remaining = self.h - self.b_margin - self.get_y()

        if remaining < needed_space:
            self.add_page()

        # ----- 1.  render the title -----
        self.ln(PRE_PADDING)                     # space before the bar
        self.set_font('Helvetica', 'B', 12)

        title_width  = self.get_string_width(title) + 15  # padding
        title_x      = self.l_margin
        title_y      = self.get_y()

        # shaded rectangle
        self.set_fill_color(240, 240, 240)
        self.rect(title_x, title_y, title_width, TITLE_HEIGHT, 'F')

        # text on top
        self.set_text_color(0, 0, 0)
        self.set_xy(title_x + 3, title_y + 2)
        self.cell(title_width - 6, TITLE_HEIGHT - 4, title, 0, 0, 'L')

        # move cursor below the bar + post-padding
        self.set_xy(self.l_margin, title_y + TITLE_HEIGHT + POST_PADDING)
        self.ln(POST_PADDING)


    def chapter_body(self, body):
        """Enhanced chapter body with better formatting"""
        body = clean_text_for_pdf(body)
        self.set_font('Helvetica', '', 11)
        # Calculate effective width for text
        effective_width = self.w - 2 * self.l_margin
        self.multi_cell(effective_width, 5, body)
        self.ln(3)  # Add space between paragraphs

    def inline_bold_text(self, text):
        """Format text with inline bold headings while maintaining tight flow"""
        text = clean_text_for_pdf(text)
        
        # Split text by common inline headings
        headings = [
            'Key market drivers:', 'Headwinds:', 'Investor sentiment:', 'Actionable insights:',
            'Market drivers:', 'Key drivers:', 'Market sentiment:', 'Key insights:',
            'Trading multiples:', 'Performance analysis:', 'Competitive landscape:',
            'Risk factors:', 'Opportunities:', 'Challenges:', 'Outlook:'
        ]
        
        # Check if text contains any of these headings
        for heading in headings:
            if heading.lower() in text.lower():
                # Split the text at the heading
                parts = text.split(heading, 1)
                if len(parts) == 2:
                    # Add the text before the heading
                    if parts[0].strip():
                        self.chapter_body(parts[0].strip())
                    
                    # Add the heading in bold
                    self.set_font('Helvetica', 'B', 11)
                    self.cell(0, 5, clean_text_for_pdf(heading), 0, 0, 'L')
                    self.set_font('Helvetica', '', 11)  # Reset to normal font
                    
                    # Add the text after the heading
                    if parts[1].strip():
                        self.chapter_body(parts[1].strip())
                    return
        
        # If no headings found, just add as regular text
        self.chapter_body(text)

    def bullet_point(self, text):
        """Enhanced bullet point with better formatting"""
        text = clean_text_for_pdf(text)
        self.set_font('Helvetica', '', 11)
        # Calculate effective width for text
        effective_width = self.w - 2 * self.l_margin - 10
        self.cell(5, 5, '-', 0, 0, 'L')  # Use dash instead of bullet character for compatibility
        self.multi_cell(effective_width, 5, ' ' + text)
        self.ln(2)  # Add space after bullet point

    def deal_date(self, date_text):
        """Display deal date in smaller italic font for easy reading"""
        date_text = clean_text_for_pdf(date_text)
        self.set_font('Helvetica', 'I', 9)  # Smaller italic font
        self.set_text_color(100, 100, 100)  # Dark gray color for subtle appearance
        # Calculate effective width for text
        effective_width = self.w - 2 * self.l_margin
        self.multi_cell(effective_width, 4, date_text)  # Smaller line height
        self.ln(2)  # Add small space after date
        # Reset text color and font
        self.set_text_color(0, 0, 0)  # Reset to black
        self.set_font('Helvetica', '', 11)  # Reset to normal font

    def deal_header(self, deal_number):
        title = f"Deal {deal_number}"
        self.ln(6)
        self.set_fill_color(230, 230, 230)
        self.set_font('Helvetica', 'B', 14)
        self.cell(0, 12, title, 0, 1, 'L', fill=True)
        self.ln(2)

    def draw_hyperlink(self, title, url):
        self.set_text_color(0, 0, 255)
        self.set_font('Helvetica', 'U', 11)
        self.cell(0, 5, clean_text_for_pdf(title), ln=1, link=url)
        self.set_text_color(0, 0, 0)
        self.set_font('Helvetica', '', 11)
    
    def bold_line(self, title: str) -> None:
        """Single bold line (lower-priority header).  No shading."""
        title = clean_text_for_pdf(title)

        PRE   = 3      # space before
        LINE  = 6      # line height
        POST  = 2      # space after
        self.ensure_space(PRE + LINE + POST)

        self.ln(PRE)
        self.set_font('Helvetica', 'B', 11)
        self.set_text_color(0, 0, 0)

        effective_width = self.w - self.l_margin - self.r_margin
        self.multi_cell(effective_width, LINE, title, 0, 'L')
        self.ln(POST)

    def underlined_header(self, title: str) -> None:
        """Lower-priority header: bold text plus underline matching text width."""
        title = clean_text_for_pdf(title)

        PRE, TEXTH, POST = 3, 6, 2
        self.ensure_space(PRE + TEXTH + POST)

        self.ln(PRE)
        self.set_font('Helvetica', 'B', 11)
        
        # Measure text width
        text_width = self.get_string_width(title)
        
        # Starting position
        x_start = self.get_x()
        y_top = self.get_y()

        # Print the text
        self.cell(text_width, TEXTH, title, 0, 1, 'L')

        # Draw the underline exactly under the text
        self.set_line_width(0.4)
        y_rule = y_top + TEXTH - 0.8
        self.line(x_start, y_rule, x_start + text_width, y_rule)

        self.ln(POST)




def clean_text_for_pdf(text):
    """Clean text of problematic Unicode characters for PDF generation"""
    if not text:
        return text
    
    # Replace problematic Unicode characters with ASCII equivalents
    replacements = {
        '\u20b9': 'Rs',  # Indian Rupee
        '\u20ac': 'EUR',  # Euro
        '\u00a3': 'GBP',  # Pound Sterling
        '\u00a5': 'JPY',  # Yen
        '\u20bf': 'BTC',  # Bitcoin
        '\u201c': '"',    # Left double quotation mark
        '\u201d': '"',    # Right double quotation mark
        '\u2018': "'",    # Left single quotation mark
        '\u2019': "'",    # Right single quotation mark
        '\u2013': '-',    # En dash
        '\u2014': '--',   # Em dash
        '\u2022': '-',    # Bullet
        '\u2026': '...',  # Ellipsis
    }
    
    for unicode_char, replacement in replacements.items():
        text: str = text.replace(unicode_char, replacement)
    
    # More aggressive cleaning - convert to ASCII and handle errors gracefully
    try:
        # First try to encode as UTF-8 and decode as ASCII
        text = text.encode('utf-8').decode('ascii', errors='ignore')
    except:
        # If that fails, use a more aggressive approach
        text = ''.join(char for char in text if ord(char) < 128)
    
    return text.strip()



link_re = re.compile(
    r'\*\*(?P<title>.+?)\*\*\s*'
    r'\(\s*\[Link\]\((?P<url>https?://[^\s)]+)\)\s*\)'
)

def draw_hyperlink(pdf: PDF, title: str, url: str) -> None:
    """Render one blue, under-lined clickable link line."""
    pdf.set_text_color(0, 0, 255)
    pdf.set_font('Helvetica', 'U', 11)
    pdf.cell(0, 5, clean_text_for_pdf(title), ln=1, link=url)
    # reset for the rest of the text
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Helvetica', '', 11)



def process_section_content(content: str, pdf: PDF) -> None:
    lines = [ln.rstrip() for ln in content.splitlines()]

    i = 0
    while i < len(lines):
        line = str(lines[i].strip())

        # → markdown hyperlink
        if (m := link_pat.match(line)):
            draw_hyperlink(pdf, m['title'], m['url'])
            i += 1
            continue

        # → empty
        if not line:
            i += 1
            continue

        # → bullet   "- **Deal Size:** $1 bn"
        if (m := bullet_pat.match(line)):
            label, value = m.groups()
            text = f"{label} {value.replace("**", "")}".strip()
            pdf.bullet_point(text)
            i += 1
            continue

        # → subsection   (“**Deal 3:**”  OR  “#### Subsector Breakdown”)
        if (m := sub_pat.match(line)):
            title = m.group(1) or m.group(2)          # whichever group matched
            pdf.subsection_title(title.strip())
            i += 1
            continue

        if (m := bold_line_pat.match(line)):
            pdf.bold_line(line[4:])
            i += 1
            continue

        if (m := underline_pat.match(line)):
            pdf.underlined_header(m.group('u_lbl'))
            i += 1
            continue

        # → generic body (fallback)
        if body_pat.match(line):
            pdf.chapter_body(line)
        else:                     # anything that slips through
            pdf.chapter_body(line)

        i += 1


def format_brief(analysis: str, briefs_dir: Path, sector) -> Path:
    """
    Render a PDF from the Markdown-style *analysis* string and
    return the full path to the saved file.
    """

    briefs_dir.mkdir(parents=True, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    file_header = ""
    match sector:
        case 1:
            file_name = f"TMT_Brief_{today}.pdf"
            file_header = f"TMT Sector M&A & Valuation Brief – {today}"
        case 2:
            file_name = f"Energy_Brief_{today}.pdf"
            file_header = f"Energy Sector M&A & Valuation Brief – {today}"

    pdf_path  = briefs_dir / file_name
    # ----------  create & set up PDF  ----------
    pdf = PDF()
    pdf.set_title(
        clean_text_for_pdf(file_header)
    )
    pdf.add_page()

    # Header block (generated date + confidentiality line)
    pdf.set_font("Helvetica", "I", 8)
    pdf.cell(0, 5, f"Generated on {today}", 0, 1, "R")
    pdf.cell(
        0, 5,
        clean_text_for_pdf("CONFIDENTIAL – FOR INTERNAL USE ONLY"),
        0, 1, "R"
    )
    pdf.ln(10)

    # ----------  split the report into top-level sections  ----------
    analysis  = clean_text_for_pdf(analysis)
    sections  = re.split(r"(?m)(?=^###\s*\d+\.)", analysis)   # uses sec_pat form

    for section in sections:
        if not section.strip():
            continue

        # first non-blank line of this chunk
        first_ln = section.lstrip().split('\n', 1)[0]

        # ► MAIN “### 1.” … “### 6.” headers
        if sec_pat.match(first_ln):
            # strip leading "###" and re-render as chapter title
            pdf.chapter_title(first_ln.replace('###', '').strip())

            body = section.split('\n', 1)[1] if '\n' in section else ''
            if body.strip():
                process_section_content(body, pdf)
            continue   # done with this top-level section

        # ► everything else (sub-sections, body blocks, etc.)
        process_section_content(section, pdf)

    # ----------  finalise ----------
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.output(str(pdf_path))

    return pdf_path