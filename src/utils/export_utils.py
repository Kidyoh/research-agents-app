import io
import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, ListFlowable, ListItem
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import markdown2
from datetime import datetime
import tempfile

def markdown_to_pdf(markdown_text, title="Research Report"):
    """
    Convert markdown report to PDF format
    
    Args:
        markdown_text (str): Report content in markdown
        title (str): Title of the report
        
    Returns:
        bytes: PDF file as bytes
    """
    # Create a BytesIO object to store the PDF
    buffer = io.BytesIO()
    
    # Create the PDF document
    doc = SimpleDocTemplate(buffer, pagesize=letter, 
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=72)
    
    # Get styles
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Title',
                              parent=styles['Heading1'],
                              fontSize=24,
                              leading=30,
                              alignment=1))  # 1 = CENTER
    
    # List to store PDF elements
    elements = []
    
    # Add title
    elements.append(Paragraph(title, styles['Title']))
    elements.append(Spacer(1, 0.25*inch))
    
    # Add date
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    elements.append(Paragraph(f"Generated on: {date_str}", styles["Italic"]))
    elements.append(Spacer(1, 0.25*inch))
    
    # Convert markdown sections to PDF elements
    sections = markdown_text.split("\n## ")
    main_content = sections[0]
    
    # Process main content
    elements.append(Paragraph(main_content, styles["BodyText"]))
    
    # Process each section
    for i, section in enumerate(sections[1:], 1):
        lines = section.split('\n', 1)
        if len(lines) > 1:
            section_title, section_content = lines
            elements.append(Spacer(1, 0.2*inch))
            elements.append(Paragraph(f"## {section_title}", styles["Heading2"]))
            elements.append(Spacer(1, 0.1*inch))
            
            # Handle bullet points
            if "- " in section_content:
                # Split content into paragraphs
                paragraphs = section_content.split('\n\n')
                for para in paragraphs:
                    if para.strip().startswith("- "):
                        # Process bullet points
                        bullet_items = para.split("\n- ")
                        bullet_list = []
                        for item in bullet_items:
                            if item.strip():
                                bullet_list.append(ListItem(Paragraph(item.strip(), styles["BodyText"])))
                        elements.append(ListFlowable(bullet_list))
                    else:
                        # Normal paragraph
                        elements.append(Paragraph(para, styles["BodyText"]))
            else:
                elements.append(Paragraph(section_content, styles["BodyText"]))
    
    # Build PDF
    doc.build(elements)
    
    # Get the PDF data
    pdf_data = buffer.getvalue()
    buffer.close()
    
    return pdf_data

def export_docx(markdown_text, title="Research Report"):
    """
    Convert markdown report to DOCX format (stub function)
    
    In a real implementation, you'd use python-docx library to create a DOCX file
    """
    # This is a placeholder - implementation would require python-docx
    return None

def markdown_to_html(markdown_text):
    """
    Convert markdown to HTML
    
    Args:
        markdown_text: Markdown formatted text
        
    Returns:
        str: HTML formatted text
    """
    return markdown2.markdown(markdown_text, extras=["tables", "cuddled-lists", "footnotes"])