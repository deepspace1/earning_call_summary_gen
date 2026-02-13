from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import os

def create_submission_pdf():
    doc = SimpleDocTemplate("L2_Assignment_Submission.pdf", pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
    styles = getSampleStyleSheet()
    
    # Custom Styles
    title_style = styles["Title"]
    heading_style = styles["Heading2"]
    normal_style = styles["Normal"]
    code_style = ParagraphStyle('Code', parent=styles['Normal'], fontName='Courier', fontSize=9, leading=12)

    story = []

    # Title
    story.append(Paragraph("L2 Assignment Submission: Research Tool Implementation", title_style))
    story.append(Spacer(1, 12))
    story.append(Paragraph("<b>Project:</b> CallMosaic AI", normal_style))
    story.append(Spacer(1, 24))

    # 1. Project Overview
    story.append(Paragraph("Project Overview", heading_style))
    story.append(Paragraph("This document serves as the formal submission for the L2 Assignment. The project implements a minimal research portal slice focused on providing structured, analyst-usable outputs from unstructured research materials.", normal_style))
    story.append(Spacer(1, 12))
    story.append(Paragraph("<b>Selected Tool Implementation:</b> Option B: Earnings Call / Management Commentary Summary", normal_style))
    story.append(Paragraph("The implemented tool processes an uploaded earnings call transcript or management commentary and extracts key insights, sentiment, and forward-looking guidance, structuring them for immediate analyst review.", normal_style))
    story.append(Spacer(1, 12))

    # 2. Project Access
    story.append(Paragraph("1. Project Access and Source Code", heading_style))
    story.append(Paragraph("The complete source code and detailed setup instructions are available.", normal_style))
    story.append(Spacer(1, 6))
    story.append(Paragraph("<b>GitHub Repository Link:</b> [Insert your GitHub link here]", normal_style))
    story.append(Paragraph("<b>Live Deployment Link:</b> [Insert your deployment link here]", normal_style))
    story.append(Spacer(1, 6))
    story.append(Paragraph("<b>Note on Keys and Limitations:</b>", normal_style))
    story.append(Paragraph("• The deployment uses an active, rate-limited Groq API key.", normal_style))
    story.append(Paragraph("• File size limited to 10MB.", normal_style))
    story.append(Spacer(1, 12))

    # 3. Implementation Details
    story.append(Paragraph("2. Implementation Details and Justification (Option B)", heading_style))
    story.append(Paragraph("<b>Core Logic:</b>", normal_style))
    story.append(Paragraph("The system utilizes <b>Groq (meta-llama/llama-4-maverick-17b-128e-instruct)</b> in a structured output mode. It features a custom backend with <b>PyMuPDF</b> for extraction, <b>Tesseract OCR</b> for scanned documents, and a smart chunking strategy to handle token limits.", normal_style))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("<b>Judgment Calls and Handling:</b>", normal_style))
    
    # QA Pairs
    qa_pairs = [
        ("How do you assess management tone?", "Tone is assessed by instructing the LLM to analyze the overall language, direct statements regarding performance/outlook, and the use of qualifying phrases. The output is constrained to categories: Optimistic, Neutral, Cautious, Pessimistic."),
        ("When guidance is vague, how specific should your summary be?", "The prompt instructs the model to 'Forward Guidance & Outlook'. If purely qualitative, the output reflects that. If numbers are present, they are extracted."),
        ("How do you avoid hallucinating information?", "The System Prompt explicitly states: 'STRICT RULES: Use ONLY information present in transcript. Do NOT fabricate numbers. If something is not mentioned, state Not mentioned.'"),
        ("What if the transcript doesn't have all sections?", "The model is instructed to return 'N/A' or 'Not mentioned' for missing sections, ensuring no data is invented to fill the void.")
    ]
    
    for q, a in qa_pairs:
        story.append(Paragraph(f"<b>Q: {q}</b>", normal_style))
        story.append(Paragraph(f"A: {a}", normal_style))
        story.append(Spacer(1, 6))

    story.append(PageBreak())

    # 4. Visual Summary
    story.append(Paragraph("3. Visual Summary of Key Functionality", heading_style))
    
    def add_image_if_exists(path, caption):
        if os.path.exists(path):
            try:
                img = RLImage(path, width=400, height=300, kind='proportional')
                story.append(img)
                story.append(Paragraph(f"<b>{caption}</b>", normal_style))
                story.append(Spacer(1, 12))
            except Exception as e:
                story.append(Paragraph(f"[Error loading image: {caption}]", normal_style))
        else:
            story.append(Paragraph(f"[Image Placeholder: {caption}]", normal_style))
            story.append(Spacer(1, 12))

    add_image_if_exists("images/step_1_upload_template.png", "Figure 1: Document Upload Interface")
    add_image_if_exists("images/step_3_dashboard_template.png", "Figure 2: The Structured Research Output")
    add_image_if_exists("images/step_4_report_template.png", "Figure 3: Export Feature")

    # 5. Output Structure
    story.append(Paragraph("4. Output Structure and Quality", heading_style))
    story.append(Paragraph("The final output is presented in a clean, easily readable JSON-structured format on the frontend and exported as a professional PDF. It prioritizes data extraction reliability and analyst usability.", normal_style))

    doc.build(story)
    print("PDF generated successfully.")

if __name__ == "__main__":
    create_submission_pdf()
