from fpdf import FPDF
import re
from datetime import datetime
from pathlib import Path

class PDF(FPDF):
    def __init__(self):
        super().__init__()
        # Set margins (left, top, right) in mm
        self.set_margins(15, 15, 15)
        self.set_auto_page_break(auto=True, margin=15)
        self.title = None
        
    def set_title(self, title):
        self.title = title
        
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

    def subsection_title(self, title):
        """Subsection title with bold formatting, shading, and smaller font than chapter_title"""
        title = clean_text_for_pdf(title)
        self.ln(4)  # Add space before title
        
        # Set up the title formatting
        self.set_font('Helvetica', 'B', 12)  # Bold, smaller font than chapter_title
        
        # Calculate title dimensions
        title_width = self.get_string_width(title) + 15  # Add padding
        title_height = 10  # Height for the shaded area
        title_x = self.l_margin
        title_y = self.get_y()
        
        # Draw shaded background rectangle
        self.set_fill_color(240, 240, 240)  # Lighter gray background than chapter_title
        self.rect(title_x, title_y, title_width, title_height, 'F')
        
        # Add the title text on top of the background
        self.set_text_color(0, 0, 0)  # Black text
        self.set_xy(title_x + 3, title_y + 2)  # Position text with padding
        self.cell(title_width - 6, title_height - 4, title, 0, 0, 'L')
        
        # Move to next line after title
        self.set_xy(self.l_margin, title_y + title_height + 2)
        self.ln(2)  # Add space after title

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
        text = text.replace(unicode_char, replacement)
    
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



def process_section_content(content, pdf):
    """Process section content and apply proper formatting"""
    lines = content.strip().split('\n')
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        m_link = link_re.match(line)
        if m_link:
            draw_hyperlink(pdf, m_link['title'].rstrip('* '), m_link['url'])
            i += 1
            continue

        # Add check for empty lines
        if not line.strip():
            i += 1
            continue
            
        # Remove markdown formatting
        line = line.replace('#', '').replace('*', '').strip()
        
        # 1️⃣ Check for bullet points (lines starting with -, •, or *)
        if line.startswith(('-', '•', '*')):
            # This is a bullet point
            content = line[1:].strip()
            if content:
                pdf.bullet_point(content)
        
        # Check if this is a subsection title (ends with colon, not a bullet point)
        elif (line.endswith(':') and 
              not line.startswith(('-', '•', '*')) and
              len(line.split()) <= 8 and  # Reasonable length for a title
              not line.isupper()):  # Not a main section header
            
            # 4️⃣ Check for standalone actionable insights or key takeaways
            if any(phrase in line for phrase in ['Actionable Insights:', 'Key Takeaways:', 'Key Insights:']):
                # Remove the colon for the title
                title = line[:-1].strip()
                pdf.subsection_title(title)
            else:
                # Remove the colon for the title
                title = line[:-1].strip()
                pdf.subsection_title(title)
        
        # Check for specific deal field headings that should be rendered as subsection titles
        elif (line.endswith(':') and 
              any(field in line for field in [
                  'Deal Size:', 'Valuation Multiples:', 'Companies:', 'Date Announced:', 
                  'Rationale:', 'Risk:', 'IPO Rationale:', 'Valuation:', 'Pricing Range:', 'Timing:'
              ])):
            
            # Special handling for Companies followed by Date Announced
            if 'Companies:' in line:
                # Remove the colon for the title
                title = line[:-1].strip()
                pdf.subsection_title(title)
                
                # Check if next line is Date Announced
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if 'Date Announced:' in next_line:
                        # Extract the date value (everything after "Date Announced:")
                        date_value = next_line.split('Date Announced:', 1)[1].strip()
                        if date_value:
                            pdf.deal_date(date_value)
                        i += 1  # Skip the Date Announced line since we've processed it
                    else:
                        # Regular companies content
                        companies_content = line.split('Companies:', 1)[1].strip()
                        if companies_content:
                            pdf.chapter_body(companies_content)
            else:
                # Remove the colon for the title
                title = line[:-1].strip()
                pdf.subsection_title(title)
                
                # Get the content for this field (everything after the colon)
                field_content = line.split(':', 1)[1].strip()
                if field_content:
                    pdf.chapter_body(field_content)
        
        else:
            # 2️⃣ Check for inline headings in regular text
            if any(phrase in line for phrase in [
                'Key market drivers:', 'Headwinds:', 'Investor sentiment:', 'Actionable insights:',
                'Market drivers:', 'Key drivers:', 'Market sentiment:', 'Key insights:',
                'Trading multiples:', 'Performance analysis:', 'Competitive landscape:',
                'Risk factors:', 'Opportunities:', 'Challenges:', 'Outlook:'
            ]):
                # Use inline bold formatting
                pdf.inline_bold_text(line)
            else:
                # Regular text - ensure it's not empty before adding
                if line.strip():
                    pdf.chapter_body(line)
        
        i += 1

def format_brief(analysis: str, briefs_dir: Path) -> Path:
    """
    Render a PDF from the Markdown-style *analysis* string and return
    the full path to the saved file.

    Parameters
    ----------
    analysis    : str      – full report text produced by GPT
    briefs_dir  : Path     – folder where the PDF should be written
    """
    briefs_dir.mkdir(parents=True, exist_ok=True)

    today    = datetime.now().strftime("%Y-%m-%d")
    pdf_path = briefs_dir / f"brief_{today}.pdf"

    pdf = PDF()
    pdf.set_title(f"TMT Sector M&A & Valuation Brief – {today}")
    pdf.add_page()

    # header block
    pdf.set_font("Helvetica", "I", 8)
    pdf.cell(0, 5, f"Generated on {today}", 0, 1, "R")
    pdf.cell(0, 5, "CONFIDENTIAL – FOR INTERNAL USE ONLY", 0, 1, "R")
    pdf.ln(10)

    # split on “1.” … “6.” at line starts
    sections = re.split(r"(?m)(?=^\s*#*\s*[1-6]\.)", analysis)

    for section in sections:
        if not section.strip():
            continue

        header_line = section.strip().split("\n", 1)[0]
        header_line_clean = header_line.replace("#", "").replace("*", "").strip()

        if header_line_clean.startswith(tuple("12345.")):
            # main section
            pdf.chapter_title(header_line_clean)
            remainder = section.split("\n", 1)[1] if "\n" in section else ""
            if remainder.strip():
                process_section_content(remainder, pdf)
            continue

        # subsection or regular block
        lines      = section.strip().split("\n")
        first_line = lines[0].strip()

        is_sub_hdr = (
            first_line.isupper()
            or (first_line.split()[0].rstrip(".").isdigit() and first_line.isupper())
            or (len(first_line.split()) <= 8 and first_line.isupper())
        )

        if is_sub_hdr:
            pdf.chapter_title(first_line.replace("#", "").replace("*", "").strip())
            remainder = "\n".join(lines[1:])
            if remainder.strip():
                process_section_content(remainder, pdf)
        else:
            process_section_content(section, pdf)

    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.output(str(pdf_path))

    return pdf_path
