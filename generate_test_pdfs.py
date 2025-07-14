from fpdf import FPDF
from datetime import datetime, timedelta
import os

def create_test_pdf(filename, title, content):
    """Create a test PDF with given filename, title, and content"""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, title, ln=True, align='C')
    pdf.ln(10)
    pdf.set_font('Arial', '', 12)
    
    # Add content in paragraphs
    for paragraph in content:
        pdf.multi_cell(0, 10, paragraph)
        pdf.ln(5)
    
    # Add footer
    pdf.set_font('Arial', 'I', 10)
    pdf.cell(0, 10, f'Generated on {datetime.now().strftime("%Y-%m-%d %H:%M")}', ln=True, align='C')
    
    pdf.output(filename)
    print(f"Created: {filename}")

def main():
    """Generate test PDF files for daily briefs"""
    
    # Ensure daily_briefs directory exists
    briefs_dir = 'daily_briefs'
    os.makedirs(briefs_dir, exist_ok=True)
    
    # Test content for different dates
    test_briefs = [
        {
            'filename': f'{briefs_dir}/brief_2025-06-15.pdf',
            'title': 'TMT Daily Brief - January 15, 2024',
            'content': [
                'Recent TMT M&A Activity:',
                '- Microsoft acquires AI startup for $2.5B',
                '- Google Cloud expands enterprise solutions',
                '- Fintech sector shows strong growth with 15% YoY increase',
                '',
                'Market Dynamics & Sentiment:',
                '- Overall TMT sector sentiment remains positive',
                '- Software subsector leads with 25% growth',
                '- AI/ML companies continue to attract significant investment',
                '',
                'Banking Pipeline:',
                '- 12 active M&A deals in due diligence',
                '- 5 IPOs expected in Q2 2024',
                '- Strong pipeline in fintech and cybersecurity sectors'
            ]
        },
        {
            'filename': f'{briefs_dir}/brief_2024-02-14.pdf',
            'title': 'TMT Daily Brief - January 14, 2024',
            'content': [
                'Recent TMT M&A Activity:',
                '- Apple acquires mobile gaming studio for $1.8B',
                '- Amazon Web Services expands cloud infrastructure',
                '- Cybersecurity M&A activity increases 30% YoY',
                '',
                'Market Dynamics & Sentiment:',
                '- Cloud computing sector shows robust growth',
                '- Enterprise software valuations remain elevated',
                '- Investor appetite for SaaS companies strong',
                '',
                'Banking Pipeline:',
                '- 8 new mandates secured this week',
                '- 3 IPOs in preparation phase',
                '- Focus on healthcare technology deals'
            ]
        },
        {
            'filename': f'{briefs_dir}/brief_2024-10-13.pdf',
            'title': 'TMT Daily Brief - January 13, 2024',
            'content': [
                'Recent TMT M&A Activity:',
                '- Meta acquires VR technology company for $3.2B',
                '- Salesforce expands CRM capabilities',
                '- Digital payments sector consolidation continues',
                '',
                'Market Dynamics & Sentiment:',
                '- VR/AR sector gaining momentum',
                '- Enterprise software multiples at 15x EBITDA',
                '- Strong demand for cybersecurity solutions',
                '',
                'Banking Pipeline:',
                '- 15 active deals in various stages',
                '- 4 IPOs expected in Q1 2024',
                '- Growing interest in AI/ML startups'
            ]
        },
        {
            'filename': f'{briefs_dir}/brief_2025-07-30.pdf',
            'title': 'TMT Daily Brief - January 12, 2024',
            'content': [
                'Recent TMT M&A Activity:',
                '- Oracle acquires cloud database startup for $1.5B',
                '- Netflix expands content production capabilities',
                '- E-commerce platform consolidation accelerates',
                '',
                'Market Dynamics & Sentiment:',
                '- Streaming services show strong subscriber growth',
                '- Cloud infrastructure spending up 40% YoY',
                '- Digital transformation driving M&A activity',
                '',
                'Banking Pipeline:',
                '- 20+ deals in active pipeline',
                '- 6 IPOs in preparation',
                '- Focus on B2B SaaS companies'
            ]
        },
        {
            'filename': f'{briefs_dir}/brief_2025-08-11.pdf',
            'title': 'TMT Daily Brief - January 11, 2024',
            'content': [
                'Recent TMT M&A Activity:',
                '- Adobe acquires design software company for $2.1B',
                '- Zoom expands video conferencing portfolio',
                '- Cybersecurity acquisitions reach record levels',
                '',
                'Market Dynamics & Sentiment:',
                '- Remote work tools continue strong performance',
                '- Cybersecurity valuations at all-time highs',
                '- Enterprise software demand remains robust',
                '',
                'Banking Pipeline:',
                '- 18 deals in due diligence phase',
                '- 7 IPOs expected in Q2',
                '- Strong activity in fintech sector'
            ]
        }
    ]
    
    print("Generating test PDF files for daily briefs...")
    
    for brief in test_briefs:
        create_test_pdf(brief['filename'], brief['title'], brief['content'])
    
    print(f"\nGenerated {len(test_briefs)} test PDF files in {briefs_dir}/")
    print("Files created:")
    for brief in test_briefs:
        print(f"  - {brief['filename']}")

if __name__ == "__main__":
    main() 