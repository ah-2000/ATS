"""
PDF Template Generator Service
Generates professional PDF resumes using reportlab with AI-enhanced content
"""

from io import BytesIO
from typing import List, Optional, Dict, Any
import re
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
    ListFlowable, ListItem, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.units import inch

from services.resume_parser import ParsedResume
from services.gap_analyzer import GapAnalysis


def get_styles():
    """Get custom styles for the resume PDF"""
    styles = getSampleStyleSheet()
    
    # Title style (Name)
    styles.add(ParagraphStyle(
        name='ResumeTitle',
        parent=styles['Heading1'],
        fontSize=18,
        alignment=TA_LEFT,
        spaceAfter=4,
        textColor=colors.HexColor('#1a1a6c'),
        fontName='Helvetica-Bold'
    ))
    
    # Section heading style
    styles.add(ParagraphStyle(
        name='SectionHeading',
        parent=styles['Heading2'],
        fontSize=11,
        spaceBefore=12,
        spaceAfter=4,
        textColor=colors.HexColor('#1a1a6c'),
        fontName='Helvetica-Bold',
        borderPadding=0
    ))
    
    # Normal text
    styles.add(ParagraphStyle(
        name='ResumeNormal',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=3,
        fontName='Helvetica'
    ))
    
    # Contact info
    styles.add(ParagraphStyle(
        name='ContactInfo',
        parent=styles['Normal'],
        fontSize=9,
        alignment=TA_CENTER,
        spaceAfter=2,
        textColor=colors.HexColor('#444444'),
        fontName='Helvetica'
    ))
    
    # Job title style
    styles.add(ParagraphStyle(
        name='JobTitle',
        parent=styles['Normal'],
        fontSize=10,
        fontName='Helvetica-Bold',
        spaceAfter=2
    ))
    
    # Company/Duration style
    styles.add(ParagraphStyle(
        name='Company',
        parent=styles['Normal'],
        fontSize=9,
        fontName='Helvetica-Oblique',
        textColor=colors.HexColor('#555555'),
        spaceAfter=3
    ))
    
    # Bullet point style
    styles.add(ParagraphStyle(
        name='BulletPoint',
        parent=styles['Normal'],
        fontSize=9,
        leftIndent=15,
        spaceAfter=2,
        fontName='Helvetica'
    ))
    
    # Missing skills highlight
    styles.add(ParagraphStyle(
        name='MissingSkills',
        parent=styles['Normal'],
        fontSize=9,
        spaceAfter=2,
        textColor=colors.HexColor('#cc6600'),
        fontName='Helvetica-Oblique'
    ))
    
    # Recommendation style
    styles.add(ParagraphStyle(
        name='Recommendation',
        parent=styles['Normal'],
        fontSize=9,
        leftIndent=10,
        spaceAfter=2,
        textColor=colors.HexColor('#336699'),
        fontName='Helvetica'
    ))
    
    return styles


def parse_reconstructed_text(text: str) -> Dict[str, Any]:
    """
    Parse the AI-reconstructed text into sections.
    The AI outputs text in a specific format with === SECTION === markers.
    """
    sections = {
        'header': '',
        'contact': '',
        'summary': '',
        'skills': '',
        'experience': [],
        'projects': [],
        'education': [],
        'certifications': [],
        'languages': ''
    }
    
    lines = text.strip().split('\n')
    current_section = None
    current_content = []
    
    for line in lines:
        line_stripped = line.strip()
        
        # Detect section headers
        if line_stripped.startswith('===') and line_stripped.endswith('==='):
            # Save previous section
            if current_section:
                sections[current_section] = '\n'.join(current_content)
            
            # Parse new section
            section_name = line_stripped.replace('=', '').strip().lower()
            section_map = {
                'header': 'header',
                'professional summary': 'summary',
                'summary': 'summary',
                'skills': 'skills',
                'professional experience': 'experience',
                'experience': 'experience',
                'work experience': 'experience',
                'projects': 'projects',
                'key projects': 'projects',
                'education': 'education',
                'certifications': 'certifications',
                'certificates': 'certifications',
                'languages': 'languages'
            }
            current_section = section_map.get(section_name, None)
            current_content = []
        elif current_section:
            current_content.append(line)
    
    # Save last section
    if current_section:
        sections[current_section] = '\n'.join(current_content)
    
    return sections


def create_resume_pdf(
    reconstructed_text: str,
    parsed_resume: ParsedResume,
    gap_analysis: GapAnalysis,
    job_position: str,
    job_description: str
) -> BytesIO:
    """
    Create a professionally styled PDF resume with AI-enhanced content.
    
    Args:
        reconstructed_text: AI-reconstructed resume text with JD-aligned language
        parsed_resume: Original structured resume data
        gap_analysis: Gap analysis with missing skills and recommendations
        job_position: Target job position
        job_description: Target job description
        
    Returns:
        BytesIO buffer containing the PDF file
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.6*inch,
        leftMargin=0.6*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )
    
    styles = get_styles()
    story = []
    
    # Parse the AI-reconstructed text
    sections = parse_reconstructed_text(reconstructed_text)
    
    # ========== HEADER (Name) ==========
    name = parsed_resume.name or "Your Name"
    # Try to extract name from reconstructed header if available
    if sections['header']:
        header_lines = [l.strip() for l in sections['header'].split('\n') if l.strip()]
        if header_lines:
            name = header_lines[0]
    
    story.append(Paragraph(name, styles['ResumeTitle']))
    
    # Contact info
    contact_parts = []
    if parsed_resume.email:
        contact_parts.append(parsed_resume.email)
    if parsed_resume.phone:
        contact_parts.append(parsed_resume.phone)
    if parsed_resume.linkedin:
        contact_parts.append(parsed_resume.linkedin)
    if parsed_resume.location:
        contact_parts.append(parsed_resume.location)
    
    if contact_parts:
        contact_line = " | ".join(contact_parts)
        story.append(Paragraph(contact_line, styles['ContactInfo']))
    
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#1a1a6c')))
    story.append(Spacer(1, 6))
    
    # ========== PROFESSIONAL SUMMARY (AI-Enhanced) ==========
    story.append(Paragraph("PROFESSIONAL SUMMARY", styles['SectionHeading']))
    
    summary_text = sections['summary'].strip() if sections['summary'] else parsed_resume.summary
    if summary_text:
        # Clean up the summary
        summary_text = ' '.join(summary_text.split())
        story.append(Paragraph(summary_text, styles['ResumeNormal']))
    else:
        story.append(Paragraph(
            f"Experienced professional targeting {job_position} role with strong skills in the required domains.",
            styles['ResumeNormal']
        ))
    
    story.append(Spacer(1, 6))
    
    # ========== SKILLS (AI-Enhanced + Gap Analysis) ==========
    story.append(Paragraph("SKILLS & COMPETENCIES", styles['SectionHeading']))
    
    # Use AI-reconstructed skills if available
    if sections['skills']:
        skills_text = sections['skills'].strip()
        story.append(Paragraph(skills_text, styles['ResumeNormal']))
    else:
        # Fallback to parsed skills
        all_skills = list(parsed_resume.skills)
        if gap_analysis.matched_skills:
            for skill in gap_analysis.matched_skills:
                if skill not in all_skills:
                    all_skills.append(skill)
        if all_skills:
            story.append(Paragraph(", ".join(all_skills), styles['ResumeNormal']))
    
    story.append(Spacer(1, 6))
    
    # ========== PROFESSIONAL EXPERIENCE (AI-Enhanced) ==========
    if sections['experience'] or parsed_resume.experience:
        story.append(Paragraph("PROFESSIONAL EXPERIENCE", styles['SectionHeading']))
        
        if sections['experience']:
            # Parse AI-enhanced experience
            exp_lines = sections['experience'].strip().split('\n')
            current_job = None
            bullets = []
            
            for line in exp_lines:
                line = line.strip()
                if not line:
                    continue
                
                if line.startswith('•') or line.startswith('-') or line.startswith('*'):
                    bullet_text = line[1:].strip()
                    if bullet_text:
                        bullets.append(ListItem(Paragraph(bullet_text, styles['BulletPoint'])))
                elif '|' in line:
                    # Flush previous bullets
                    if bullets:
                        story.append(ListFlowable(bullets, bulletType='bullet', start='•', leftIndent=15))
                        bullets = []
                    
                    # Job title/company line
                    story.append(Paragraph(f"<b>{line}</b>", styles['JobTitle']))
                else:
                    # Regular line (might be duration or description)
                    if bullets:
                        story.append(ListFlowable(bullets, bulletType='bullet', start='•', leftIndent=15))
                        bullets = []
                    story.append(Paragraph(line, styles['Company']))
            
            # Flush remaining bullets
            if bullets:
                story.append(ListFlowable(bullets, bulletType='bullet', start='•', leftIndent=15))
        else:
            # Use original parsed experience
            for exp in parsed_resume.experience:
                story.append(Paragraph(f"<b>{exp.job_title}</b> | {exp.company}", styles['JobTitle']))
                if exp.duration:
                    story.append(Paragraph(exp.duration, styles['Company']))
                
                if exp.responsibilities:
                    bullets = [ListItem(Paragraph(r, styles['BulletPoint'])) for r in exp.responsibilities]
                    story.append(ListFlowable(bullets, bulletType='bullet', start='•', leftIndent=15))
                
                story.append(Spacer(1, 4))
    
    # ========== PROJECTS (AI-Enhanced) ==========
    if sections['projects'] or parsed_resume.projects:
        story.append(Paragraph("PROJECTS", styles['SectionHeading']))
        
        if sections['projects']:
            proj_lines = sections['projects'].strip().split('\n')
            bullets = []
            
            for line in proj_lines:
                line = line.strip()
                if not line:
                    continue
                
                if line.startswith('•') or line.startswith('-') or line.startswith('*'):
                    bullet_text = line[1:].strip()
                    if bullet_text:
                        bullets.append(ListItem(Paragraph(bullet_text, styles['BulletPoint'])))
                else:
                    if bullets:
                        story.append(ListFlowable(bullets, bulletType='bullet', start='•', leftIndent=15))
                        bullets = []
                    story.append(Paragraph(f"<b>{line}</b>", styles['JobTitle']))
            
            if bullets:
                story.append(ListFlowable(bullets, bulletType='bullet', start='•', leftIndent=15))
        else:
            for proj in parsed_resume.projects:
                story.append(Paragraph(f"<b>{proj.name}</b>", styles['JobTitle']))
                if proj.technologies:
                    story.append(Paragraph(f"Technologies: {', '.join(proj.technologies)}", styles['Company']))
                
                bullets = []
                if proj.description:
                    bullets.append(ListItem(Paragraph(proj.description, styles['BulletPoint'])))
                for h in proj.highlights:
                    bullets.append(ListItem(Paragraph(h, styles['BulletPoint'])))
                
                if bullets:
                    story.append(ListFlowable(bullets, bulletType='bullet', start='•', leftIndent=15))
                story.append(Spacer(1, 4))
    
    # ========== EDUCATION ==========
    if parsed_resume.education:
        story.append(Paragraph("EDUCATION", styles['SectionHeading']))
        
        for edu in parsed_resume.education:
            degree_text = edu.degree
            if edu.field_of_study:
                degree_text += f" in {edu.field_of_study}"
            story.append(Paragraph(f"<b>{degree_text}</b>", styles['JobTitle']))
            
            edu_details = []
            if edu.institution:
                edu_details.append(edu.institution)
            if edu.graduation_date:
                edu_details.append(edu.graduation_date)
            if edu_details:
                story.append(Paragraph(" | ".join(edu_details), styles['Company']))
            
            story.append(Spacer(1, 4))
    
    # ========== CERTIFICATIONS ==========
    if parsed_resume.certifications:
        story.append(Paragraph("CERTIFICATIONS", styles['SectionHeading']))
        
        for cert in parsed_resume.certifications:
            story.append(Paragraph(f"• {cert}", styles['ResumeNormal']))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    
    return buffer
