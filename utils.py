import re

def clean_text(text: str) -> str:
    """
    Cleans the extracted text by removing page numbers, 
    repeated headers, and excessive whitespace.
    """
    # Remove potential page numbers (e.g., "Page 1 of 10", "1")
    # This is a basic regex, might need tuning based on specific PDF formats
    text = re.sub(r'Page \d+ of \d+', '', text)
    text = re.sub(r'\n\s*\d+\s*\n', '\n', text) 
    
    # Remove multiple newlines and extra spaces
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    
    return text.strip()

def count_tokens(text: str) -> int:
    """
    Rough estimation of tokens (words / 0.75).
    """
    return int(len(text.split()) / 0.75)

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO

def create_pdf_report(summary_data: dict) -> BytesIO:
    """
    Generates a PDF report from the summary data using ReportLab.
    Returns a BytesIO object containing the PDF.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='SectionHeader', fontSize=12, leading=14, spaceAfter=6, textColor=colors.HexColor("#003366"), fontName='Helvetica-Bold'))
    styles.add(ParagraphStyle(name='NormalCustom', fontSize=10, leading=12, spaceAfter=10))
    
    story = []
    
    # Title
    story.append(Paragraph("Earnings Call Summary", styles['Title']))
    story.append(Spacer(1, 12))
    
    # Helper to add section
    def add_section(title, content):
        story.append(Paragraph(title, styles['SectionHeader']))
        if isinstance(content, list):
            for item in content:
                story.append(Paragraph(f"• {item}", styles['NormalCustom']))
        else:
            story.append(Paragraph(str(content), styles['NormalCustom']))
        story.append(Spacer(1, 12))

    # Iterate through keys in order
    keys_order = [
        "Management Tone",
        "Executive One-Page Summary Paragraph", # Moved up for visibility
        "Business Performance Overview",
        "Revenue and Margin Discussion",
        "Cost & Operational Commentary",
        "Key Positives",
        "Key Risks / Challenges",
        "Forward Guidance & Outlook",
        "Strategic / Growth Initiatives",
        "Capital Allocation / Capex Commentary",
        "Q&A Insights"
    ]
    
    for key in keys_order:
        if key in summary_data:
            add_section(key, summary_data[key])
            
    doc.build(story)
    buffer.seek(0)
    return buffer
