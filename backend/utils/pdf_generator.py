import os
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

def generate_pdf_certificate(
    student_name: str,
    event_title: str,
    event_date: str,
    organizer_name: str,
    certificate_number: str
) -> str:
    """Generates a professional PDF certificate and returns the relative static URL."""
    output_dir = os.path.join("backend", "static", "certificates")
    os.makedirs(output_dir, exist_ok=True)
    
    file_name = f"cert_{certificate_number}.pdf"
    file_path = os.path.join(output_dir, file_name)
    
    # Setup document: Landscape Letter format
    doc = SimpleDocTemplate(
        file_path,
        pagesize=landscape(letter),
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Typography Styles
    title_style = ParagraphStyle(
        'CertTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=32,
        leading=38,
        textColor=colors.HexColor('#1E1B4B'),
        alignment=1 # Center
    )
    
    subtitle_style = ParagraphStyle(
        'CertSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=colors.HexColor('#4F46E5'),
        alignment=1
    )
    
    body_style = ParagraphStyle(
        'CertBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=13,
        leading=18,
        textColor=colors.HexColor('#374151'),
        alignment=1
    )
    
    name_style = ParagraphStyle(
        'CertName',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=26,
        leading=30,
        textColor=colors.HexColor('#7C3AED'),
        alignment=1
    )

    meta_style = ParagraphStyle(
        'CertMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor('#6B7280'),
        alignment=1
    )
    
    story = []
    story.append(Spacer(1, 0.4*inch))
    story.append(Paragraph("CAMPUS EVENT PRO", subtitle_style))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph("CERTIFICATE OF PARTICIPATION", title_style))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("THIS IS PROUDLY PRESENTED TO", body_style))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph(student_name.upper(), name_style))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph(f"for actively participating and successfully completing the event", body_style))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph(f"<b>{event_title}</b>", subtitle_style))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph(f"Held on <b>{event_date}</b> | Organised by <b>{organizer_name}</b>", body_style))
    story.append(Spacer(1, 0.5*inch))
    
    # Signature & Verification Table
    footer_table_data = [
        [
            Paragraph("______________________<br/><b>Event Coordinator</b>", body_style),
            Paragraph(f"<b>Certificate ID:</b> {certificate_number}<br/>Verified by Campus Event Pro Engine", meta_style),
            Paragraph("______________________<br/><b>Dean of Student Affairs</b>", body_style)
        ]
    ]
    
    footer_table = Table(footer_table_data, colWidths=[3.0*inch, 4.0*inch, 3.0*inch])
    footer_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    
    story.append(footer_table)
    
    doc.build(story)
    
    return f"/static/certificates/{file_name}"
