from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, ListFlowable, ListItem
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT

def create_resume_template(filename):
    doc = SimpleDocTemplate(filename, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    Story = []
    styles = getSampleStyleSheet()

    # Custom Styles
    title_style = styles["Heading1"]
    title_style.alignment = TA_LEFT
    title_style.fontSize = 18
    title_style.spaceAfter = 12
    
    heading_style = styles["Heading2"]
    heading_style.fontSize = 12
    heading_style.spaceBefore = 12
    heading_style.spaceAfter = 6
    heading_style.textColor = colors.black
    heading_style.borderPadding = 0
    # Make headings look like the source (uppercase often used in headers)
    
    normal_style = styles["Normal"]
    normal_style.fontSize = 10
    normal_style.spaceAfter = 2
    
    # NAME
    Story.append(Paragraph("[FULL NAME]", title_style))
    
    # CONTACT
    Story.append(Paragraph("CONTACT", heading_style))
    Story.append(Paragraph("<b>Cell:</b> [Your Phone Number]", normal_style))
    Story.append(Paragraph("<b>Email:</b> [Your Email Address]", normal_style))
    Story.append(Paragraph("<b>LinkedIn:</b> [Your LinkedIn Profile URL]", normal_style))
    Story.append(Spacer(1, 12))

    # CAREER OBJECTIVE
    Story.append(Paragraph("CAREER OBJECTIVE", heading_style))
    Story.append(Paragraph("[Insert a summary of your professional experience, years of expertise, and your primary career goals. Example: 'Applied Machine Learning professional with X years of experience in...']", normal_style))
    Story.append(Spacer(1, 12))

    # SKILLS & TOOLS
    Story.append(Paragraph("SKILLS & TOOLS", heading_style))
    skills_data = [
        "<b>Programming Languages:</b> [e.g., Python, C++]",
        "<b>Frameworks & Libraries:</b> [e.g., TensorFlow, PyTorch, HuggingFace]",
        "<b>Tools & Technologies:</b> [e.g., OpenCV, Docker, Jupyter Notebook]",
        "<b>Deployment & Platforms:</b> [e.g., Flask, FastAPI, AWS]"
    ]
    for skill in skills_data:
        Story.append(Paragraph(skill, normal_style))
    Story.append(Spacer(1, 12))

    # EXPERIENCE
    Story.append(Paragraph("EXPERIENCE", heading_style))
    Story.append(Paragraph("<b>[Company Name]</b>", normal_style))
    Story.append(Paragraph("<i>[Job Title]</i>", normal_style))
    
    experience_bullets = [
        ListItem(Paragraph("[Action verb] [description of responsibility or achievement].", normal_style)),
        ListItem(Paragraph("[Action verb] [description of responsibility or achievement].", normal_style)),
        ListItem(Paragraph("[Action verb] [description of responsibility or achievement].", normal_style))
    ]
    Story.append(ListFlowable(experience_bullets, bulletType='bullet', start='•', leftIndent=20))
    Story.append(Spacer(1, 12))

    # PROJECTS
    Story.append(Paragraph("PROJECTS", heading_style))
    
    # Project 1
    Story.append(Paragraph("<b>[Project Title]</b>", normal_style))
    proj1_bullets = [
        ListItem(Paragraph("[Description of the project, technologies used, and the problem it solved].", normal_style)),
        ListItem(Paragraph("[Key feature or outcome of the project].", normal_style))
    ]
    Story.append(ListFlowable(proj1_bullets, bulletType='bullet', start='•', leftIndent=20))
    Story.append(Spacer(1, 6))

    # Project 2
    Story.append(Paragraph("<b>[Project Title]</b>", normal_style))
    proj2_bullets = [
        ListItem(Paragraph("[Description of the project, technologies used, and the problem it solved].", normal_style))
    ]
    Story.append(ListFlowable(proj2_bullets, bulletType='bullet', start='•', leftIndent=20))
    Story.append(Spacer(1, 12))

    # EDUCATION
    Story.append(Paragraph("EDUCATION", heading_style))
    data_edu = [
        ['COURSE', 'YEAR', 'INSTITUTIONS'],
        ['[Degree/Major]', '[Year]', '[University/College Name]']
    ]
    t_edu = Table(data_edu, colWidths=[150, 80, 230])
    t_edu.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
    ]))
    Story.append(t_edu)
    Story.append(Spacer(1, 12))

    # CERTIFICATIONS
    Story.append(Paragraph("CERTIFICATIONS", heading_style))
    data_cert = [
        ['COURSE', 'YEAR', 'INSTITUTIONS'],
        ['[Certification Name]', '[Date]', '[Issuing Organization]']
    ]
    t_cert = Table(data_cert, colWidths=[150, 80, 230])
    t_cert.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
    ]))
    Story.append(t_cert)

    doc.build(Story)

create_resume_template("templates/Resume_Template.pdf")