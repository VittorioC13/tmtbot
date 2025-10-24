from fpdf import FPDF
import re
from datetime import datetime
from pathlib import Path
from typing import List
from dataclasses import dataclass

sec_pat    = re.compile(r'^###\s*(\d+)\.\s+(.*)$')                       # "### 1. …"
bold_line_pat = re.compile(r'^@{3}\s+(?P<h3_lbl>.+?)\s*$')                    # @@@ text
underline_pat = re.compile(r'^@{4}\s+(?P<u_lbl>.+?)\s*$')               # "@@@@ Heading"
link_pat   = re.compile(r'\*\*(?P<title>.+?)\*\*\s*\(\s*\[Link\]\((?P<url>https?://[^\s)]+)\)\s*\)') #links
bullet_pat = re.compile(r'^[\*\-\•]\s+\*\*(.+?)\*\*\s*(.*)$')            # "- **Deal Size:** foo"
body_pat   = re.compile(r'^[A-Za-z0-9\-\s\.:,;]*$')                      # generic body
sub_pat = re.compile(r'^(?:\*\*(.+?)\*\*:?\s*$|####\s+(.+?)\s*$)')        # **title:** style)
TABLE_ROW_PAT = re.compile(r'^\s*\|.*\|\s*$')
TABLE_SEP_PAT = re.compile(r'^\s*\|?\s*:?-{3,}\s*(\|\s*:?-{3,}\s*)+\|?\s*$')

@dataclass
class table:
    header: List[str]
    rows: List[List[str]]

class PDF(FPDF):
    def __init__(self):
        super().__init__()
        # Set margins (left, top, right) in mm
        self.set_margins(15, 15, 15)
        self.set_auto_page_break(auto=True, margin=15)
        self.title = None

    
    def _wrap_line_count(self, text: str, col_width: float, font_size_pt: float = 11.0) -> int:
        """
        Estimate how many wrapped lines MultiCell would use for 'text' in 'col_width'.
        We wrap by words using current font metrics to avoid mid-row page breaks.
        """
        if not text:
            return 1
        # use Helvetica 11pt (matches pdf_table)
        prev_family, prev_style, prev_size = self.font_family, self.font_style, self.font_size_pt
        self.set_font('Helvetica', '', font_size_pt)

        lines = 0
        for raw in text.split('\n'):
            words = raw.split()
            if not words:
                lines += 1
                continue
            cur_w = 0.0
            # small padding inside the cell like MultiCell has
            usable_w = col_width - 4.0
            for i, w in enumerate(words):
                ww = self.get_string_width(((' ' if i else '') + w))
                if cur_w + ww <= usable_w or cur_w == 0.0:
                    cur_w += ww
                else:
                    lines += 1
                    cur_w = self.get_string_width(w)
            lines += 1
        # restore font
        self.set_font(prev_family or 'Helvetica', prev_style or '', prev_size or 11)
        return max(1, lines)
    
    def set_context(self, *, sector: str, region: str):
        self.sector = sector
        self.region = region
        
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
        
    def header(self):  # <-- no args
        if self.title:
            self.set_font('Helvetica', 'B', 16)
            self.set_text_color(0, 0, 0)
            self.cell(0, 12, self.title, 0, 1, 'C')

            if self.sector and self.region:
                self.set_font('Helvetica', 'I', 11)
                self.set_text_color(100, 100, 100)
                self.cell(0, 6, f'{self.region} {self.sector} Sector', 0, 1, 'C')

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

    def pdf_table(self, table_lines: List[str]) -> None:
        """
        Markdown table renderer:
        - centers table within page margins
        - no row splitting across pages (pre-computes row height)
        - header shading sized to row height
        """
        if not table_lines:
            return

        def is_sep_line(s: str) -> bool:
            return bool(TABLE_SEP_PAT.match(s))

        def split_md_row(s: str) -> List[str]:
            s = s.strip()
            if s.startswith('|'):
                s = s[1:]
            if s.endswith('|'):
                s = s[:-1]
            return [clean_text_for_pdf(p.strip()) for p in s.split('|')]

        def parse_alignment(sep: str, n_cols: int) -> List[str]:
            if not sep or not is_sep_line(sep):
                return ['L'] * n_cols
            raw_cols = split_md_row(sep)
            out = []
            for i in range(n_cols):
                token = (raw_cols[i] if i < len(raw_cols) else '').replace('-', ' ').strip()
                left = token.startswith(':')
                right = token.endswith(':')
                out.append('C' if (left and right) else ('R' if right else 'L'))
            return out

        lines = [ln.rstrip() for ln in table_lines if ln.strip()]
        if not lines:
            return

        header_cells: List[str] = []
        sep_line: str | None = None
        first_row = split_md_row(lines[0])

        if len(lines) >= 2 and is_sep_line(lines[1]): #if there are two or more lines, and line 2 is separator
            header_cells = first_row
            sep_line = lines[1]
            data_lines = lines[2:]
        else:
            data_lines = lines

        body_rows: List[List[str]] = [split_md_row(ln) for ln in data_lines] #store the parsed data lines
        n_cols = max(len(header_cells) if header_cells else 0, #get the column number
                     *(len(r) for r in body_rows) if body_rows else [0])
        if n_cols == 0: 
            return

        if header_cells and len(header_cells) < n_cols: #if we have more data column than header column
            header_cells += [''] * (n_cols - len(header_cells)) #full the rest of the header with empty columns
        padded_rows: List[List[str]] = [] #do the same with data rows
        for r in body_rows:
            if len(r) < n_cols:
                r = r + [''] * (n_cols - len(r))
            padded_rows.append(r)

        aligns = parse_alignment(sep_line or '', n_cols)

        # ---- column widths (measure + fit to page) ----
        effective_width = self.w - self.l_margin - self.r_margin
        min_col_w = 18.0
        pad = 4.0  # inner padding accounted for in wrap calc

        prev_family, prev_style, prev_size = self.font_family, self.font_style, self.font_size_pt
        self.set_font('Helvetica', '', 11)

        def measure(s: str) -> float:
            return self.get_string_width(s)

        max_w = [0.0] * n_cols #get the widest column, and use that as the standard column width
        if header_cells:
            for i, t in enumerate(header_cells):
                max_w[i] = max(max_w[i], measure(t))
        for row in padded_rows:
            for i, t in enumerate(row):
                max_w[i] = max(max_w[i], measure(t))

        base = [max(min_col_w, w + pad) for w in max_w]
        total = sum(base)
        if total > effective_width:
            scale = effective_width / total
            base = [max(min_col_w, w * scale) for w in base]
            overflow = sum(base) - effective_width
            if overflow > 0:
                base[-1] = max(min_col_w, base[-1] - overflow)

        col_w = base
        table_w = sum(col_w)

        # center the table
        x_table = self.l_margin + (effective_width - table_w) / 2.0
        self.set_font(prev_family or 'Helvetica', prev_style or '', prev_size or 11)

        line_h = 6.0

        def draw_row(cells: List[str], bold: bool = False, fill: bool = False) -> None:
            # compute row height from wrapped lines across columns
            self.set_font('Helvetica', 'B' if bold else '', 11)
            lines_needed = 1
            for i, txt in enumerate(cells):
                lines_needed = max(lines_needed, self._wrap_line_count(txt, col_w[i]))
            row_h = lines_needed * line_h

            # ensure whole row fits this page (no splitting)
            remaining = self.h - self.b_margin - self.get_y()
            if remaining < row_h:
                self.add_page()  # header will print; we start row at top of new page

            # shaded header background sized to full row height
            y0 = self.get_y()
            x = x_table
            if fill:
                self.set_fill_color(235, 235, 235)
                self.rect(x, y0, table_w, row_h, 'F')

            # draw each cell (bordered, wrapped)
            for i, txt in enumerate(cells):
                align = aligns[i] if i < len(aligns) else 'L'
                w = col_w[i]
                self.set_xy(x, y0)
                # Use MultiCell to wrap; border draws grid per cell
                self.multi_cell(w, line_h, txt, border=1, align=align)
                x += w

            # move cursor to start of next row
            self.set_xy(self.l_margin, y0 + row_h)
            # return to centered x for the next row start
            self.set_x(x_table)

        # set cursor to centered x before rendering
        self.set_x(x_table)

        if header_cells:
            draw_row(header_cells, bold=True, fill=True)
        for row in padded_rows:
            draw_row(row)

        self.set_xy(self.l_margin, self.get_y())
        self.ln(2)
        


def is_table_line(line: str) -> bool:
    return bool(TABLE_ROW_PAT.match(line)) or bool(TABLE_SEP_PAT.match(line))



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
            text = f"{label} {value.replace('**', '')}".strip()
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

        if is_table_line(lines[i]):
            j = i
            n = len(lines)
            table_lines : List[str] = []
            while j < n and is_table_line(lines[j]):
                table_lines.append(lines[j].rstrip("\n"))
                j += 1
            pdf.pdf_table(table_lines)
            i = j
            continue

        # → generic body (fallback)
        if body_pat.match(line):
            pdf.chapter_body(line)
        else:                     # anything that slips through
            pdf.chapter_body(line)

        i += 1


def format_brief(analysis: str, briefs_dir: Path, sector, region, TLDR = False) -> Path:
    """
    Render a PDF from the Markdown-style *analysis* string and
    return the full path to the saved file.
    """

    briefs_dir.mkdir(parents=True, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")

    if TLDR:
        file_name = f"{region}_{sector}_TLDR_{today}.pdf"
        file_header = f"{region} {sector} Sector M&A & Valuation TLDR – {today}"
    else:
        file_name = f"{region}_{sector}_Brief_{today}.pdf"
        file_header = f"{region} {sector} Sector M&A & Valuation Brief – {today}"

    pdf_path  = briefs_dir / file_name
    # ----------  create & set up PDF  ----------
    pdf = PDF()
    pdf.set_title(
        clean_text_for_pdf(file_header)
    )
    pdf.set_context(sector=sector, region=region)
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
