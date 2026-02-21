"""
PDF Template Generator Service
Generates professional PDF resumes using reportlab with AI-enhanced content.
Fully parses ALL sections from AI output for complete, JD-tailored PDFs.
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
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.lib.units import inch

from services.resume_parser import ParsedResume
from services.gap_analyzer import GapAnalysis


def get_styles():
    """Get custom styles for the resume PDF"""
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name='ResumeTitle',
        parent=styles['Heading1'],
        fontSize=20,
        alignment=TA_CENTER,
        spaceAfter=2,
        spaceBefore=0,
        textColor=colors.HexColor('#1a1a6c'),
        fontName='Helvetica-Bold',
        leading=24
    ))

    styles.add(ParagraphStyle(
        name='SectionHeading',
        parent=styles['Heading2'],
        fontSize=11,
        spaceBefore=10,
        spaceAfter=4,
        textColor=colors.HexColor('#1a1a6c'),
        fontName='Helvetica-Bold',
        borderPadding=0,
        leading=14
    ))

    styles.add(ParagraphStyle(
        name='ResumeNormal',
        parent=styles['Normal'],
        fontSize=9.5,
        spaceAfter=3,
        fontName='Helvetica',
        leading=13,
        alignment=TA_JUSTIFY
    ))

    styles.add(ParagraphStyle(
        name='ContactInfo',
        parent=styles['Normal'],
        fontSize=9,
        alignment=TA_CENTER,
        spaceAfter=2,
        textColor=colors.HexColor('#444444'),
        fontName='Helvetica',
        leading=12
    ))

    styles.add(ParagraphStyle(
        name='JobTitle',
        parent=styles['Normal'],
        fontSize=10,
        fontName='Helvetica-Bold',
        spaceAfter=1,
        spaceBefore=6,
        leading=13
    ))

    styles.add(ParagraphStyle(
        name='Company',
        parent=styles['Normal'],
        fontSize=9,
        fontName='Helvetica-Oblique',
        textColor=colors.HexColor('#555555'),
        spaceAfter=2,
        leading=12
    ))

    styles.add(ParagraphStyle(
        name='BulletPoint',
        parent=styles['Normal'],
        fontSize=9,
        leftIndent=15,
        spaceAfter=2,
        fontName='Helvetica',
        leading=12
    ))

    styles.add(ParagraphStyle(
        name='SkillCategory',
        parent=styles['Normal'],
        fontSize=9.5,
        spaceAfter=2,
        fontName='Helvetica',
        leading=13
    ))

    return styles


def md_to_rl(text: str) -> str:
    """Convert markdown-style formatting to reportlab XML tags.
    Handles **bold**, *italic*, and cleans special chars for reportlab.
    """
    if not text:
        return ""
    # Escape XML special chars first (except for tags we'll add)
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;").replace(">", "&gt;")
    # Convert **bold** to <b>bold</b>
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    # Convert *italic* to <i>italic</i>
    text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
    return text


def parse_reconstructed_text(text: str) -> Dict[str, Any]:
    """
    Robustly parse AI-reconstructed text into sections.
    Handles multiple format variants the AI might produce.
    """
    sections = {
        'header': '',
        'contact': '',
        'summary': '',
        'skills': '',
        'experience': '',
        'projects': '',
        'education': '',
        'certifications': '',
        'languages': ''
    }

    lines = text.strip().split('\n')
    current_section = None
    current_content = []

    section_map = {
        'header': 'header',
        'professional summary': 'summary',
        'summary': 'summary',
        'objective': 'summary',
        'career objective': 'summary',
        'skills': 'skills',
        'technical skills': 'skills',
        'skills & competencies': 'skills',
        'skills &amp; competencies': 'skills',
        'skills and competencies': 'skills',
        'core competencies': 'skills',
        'professional experience': 'experience',
        'experience': 'experience',
        'work experience': 'experience',
        'projects': 'projects',
        'key projects': 'projects',
        'education': 'education',
        'academic background': 'education',
        'certifications': 'certifications',
        'certificates': 'certifications',
        'certification': 'certifications',
        'languages': 'languages',
        'additional information': 'languages'
    }

    for line in lines:
        line_stripped = line.strip()

        # Detect section headers in multiple formats
        is_section = False
        section_name = ''

        # Format: === SECTION ===
        if line_stripped.startswith('===') and '===' in line_stripped[3:]:
            section_name = line_stripped.replace('=', '').strip().lower()
            is_section = True
        # Format: --- SECTION ---
        elif line_stripped.startswith('---') and '---' in line_stripped[3:]:
            section_name = line_stripped.replace('-', '').strip().lower()
            is_section = True
        # Format: ## SECTION or ### SECTION
        elif line_stripped.startswith('##'):
            section_name = line_stripped.lstrip('#').strip().lower()
            is_section = True
        # Format: **SECTION** (bold markdown heading)
        elif line_stripped.startswith('**') and line_stripped.endswith('**') and len(line_stripped) > 4:
            potential = line_stripped.strip('*').strip().lower()
            if potential in section_map:
                section_name = potential
                is_section = True
        # Format: ALL CAPS line that matches a known section
        elif line_stripped.isupper() and len(line_stripped) > 3:
            potential = line_stripped.lower()
            if potential in section_map:
                section_name = potential
                is_section = True

        if is_section and section_name:
            # Save previous section
            if current_section:
                sections[current_section] = '\n'.join(current_content).strip()
            current_section = section_map.get(section_name, None)
            current_content = []
            if current_section:
                print(f"[PDF Parser] Found section: '{section_name}' -> '{current_section}'")
        elif current_section:
            current_content.append(line)

    # Save last section
    if current_section and current_content:
        sections[current_section] = '\n'.join(current_content).strip()

    # Debug: print which sections have content
    found = {k: len(v) for k, v in sections.items() if v}
    print(f"[PDF Parser] Sections with content: {found}")
    empty = [k for k, v in sections.items() if not v]
    print(f"[PDF Parser] Empty sections: {empty}")

    return sections


def parse_experience_section(text: str) -> List[Dict[str, Any]]:
    """Parse experience section into structured entries."""
    entries = []
    if not text.strip():
        return entries

    lines = text.strip().split('\n')
    current_entry = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Bullet point
        if line.startswith(('•', '-', '*', '–')):
            bullet_text = line.lstrip('•-*– ').strip()
            if bullet_text and current_entry:
                current_entry['bullets'].append(bullet_text)
        elif '|' in line:
            # Could be "Job Title | Company" or "Duration | Location"
            parts = [p.strip() for p in line.split('|')]
            if current_entry and current_entry.get('title_line') and not current_entry.get('detail_line'):
                # This is the duration/location line
                current_entry['detail_line'] = line
            else:
                # New job entry - title/company line
                if current_entry:
                    entries.append(current_entry)
                current_entry = {
                    'title_line': line,
                    'detail_line': '',
                    'bullets': []
                }
        elif not current_entry:
            # First non-bullet line - treat as title
            current_entry = {
                'title_line': line,
                'detail_line': '',
                'bullets': []
            }
        elif current_entry and not current_entry.get('detail_line'):
            current_entry['detail_line'] = line
        else:
            # Additional text line, treat as bullet
            if current_entry:
                current_entry['bullets'].append(line)

    if current_entry:
        entries.append(current_entry)

    return entries


def parse_projects_section(text: str) -> List[Dict[str, Any]]:
    """Parse projects section into structured entries."""
    entries = []
    if not text.strip():
        return entries

    lines = text.strip().split('\n')
    current_entry = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if line.startswith(('•', '-', '*', '–')):
            bullet_text = line.lstrip('•-*– ').strip()
            if bullet_text and current_entry:
                current_entry['bullets'].append(bullet_text)
        elif line.lower().startswith('technologies:') or line.lower().startswith('tech stack:'):
            if current_entry:
                current_entry['technologies'] = line.split(':', 1)[1].strip()
        elif '|' not in line and not line.startswith(('•', '-', '*')):
            # Project name
            if current_entry:
                entries.append(current_entry)
            current_entry = {
                'name': line,
                'technologies': '',
                'bullets': []
            }
        elif '|' in line and current_entry:
            # Could be tech line with |
            current_entry['bullets'].append(line)
        else:
            if not current_entry:
                current_entry = {
                    'name': line,
                    'technologies': '',
                    'bullets': []
                }

    if current_entry:
        entries.append(current_entry)

    return entries


def parse_education_section(text: str) -> List[Dict[str, Any]]:
    """Parse education section from AI text."""
    entries = []
    if not text.strip():
        return entries

    lines = text.strip().split('\n')
    current_entry = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if line.startswith(('•', '-', '*', '–')):
            bullet_text = line.lstrip('•-*– ').strip()
            if bullet_text and current_entry:
                current_entry['details'].append(bullet_text)
        elif '|' in line:
            if current_entry and not current_entry.get('subtitle'):
                current_entry['subtitle'] = line
            else:
                if current_entry:
                    entries.append(current_entry)
                current_entry = {'title': line, 'subtitle': '', 'details': []}
        else:
            if current_entry and not current_entry.get('subtitle'):
                current_entry['subtitle'] = line
            elif not current_entry:
                current_entry = {'title': line, 'subtitle': '', 'details': []}
            else:
                if current_entry:
                    entries.append(current_entry)
                current_entry = {'title': line, 'subtitle': '', 'details': []}

    if current_entry:
        entries.append(current_entry)

    return entries


def parse_skills_section(text: str) -> List[Dict[str, str]]:
    """Parse skills section into categories. Returns list of {category, skills}."""
    categories = []
    if not text.strip():
        return categories

    lines = text.strip().split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Remove markdown bold markers
        line = line.replace('**', '')

        # Try to split by colon for "Category: skill1, skill2"
        if ':' in line:
            parts = line.split(':', 1)
            cat_name = parts[0].strip().lstrip('•-* ')
            skills_str = parts[1].strip()
            if cat_name and skills_str:
                categories.append({'category': cat_name, 'skills': skills_str})
            elif skills_str:
                categories.append({'category': '', 'skills': skills_str})
        else:
            # No category, just a list of skills
            clean = line.lstrip('•-* ')
            if clean:
                categories.append({'category': '', 'skills': clean})

    return categories


def parse_certifications_section(text: str) -> List[str]:
    """Parse certifications from text."""
    certs = []
    if not text.strip():
        return certs
    for line in text.strip().split('\n'):
        line = line.strip().lstrip('•-*– ')
        if line:
            certs.append(line)
    return certs


def create_resume_pdf(
    reconstructed_text: str,
    parsed_resume: ParsedResume,
    gap_analysis: GapAnalysis,
    job_position: str,
    job_description: str
) -> BytesIO:
    """
    Create a professionally styled PDF resume using AI-enhanced content.
    ALL sections are sourced from the reconstructed text (JD-tailored),
    with fallback to parsed_resume data if a section is missing.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.55 * inch,
        leftMargin=0.55 * inch,
        topMargin=0.45 * inch,
        bottomMargin=0.45 * inch
    )

    styles = get_styles()
    story = []

    # Parse the AI-reconstructed text into sections
    print(f"[PDF Gen] Reconstructed text preview (first 300 chars): {reconstructed_text[:300]}")
    sections = parse_reconstructed_text(reconstructed_text)

    # ========== HEADER (Name) ==========
    name = parsed_resume.name or "Your Name"
    if sections['header']:
        header_lines = [l.strip() for l in sections['header'].split('\n') if l.strip()]
        if header_lines:
            # First non-empty line is the name
            name = header_lines[0].replace('**', '')
            # Check if there's contact info in header
            if len(header_lines) > 1:
                sections['contact'] = header_lines[1]

    story.append(Paragraph(md_to_rl(name), styles['ResumeTitle']))

    # Contact info: prefer from header, fallback to parsed
    contact_line = ""
    if sections.get('contact'):
        contact_line = sections['contact'].replace('**', '')
    else:
        contact_parts = []
        if parsed_resume.email:
            contact_parts.append(parsed_resume.email)
        if parsed_resume.phone:
            contact_parts.append(parsed_resume.phone)
        if parsed_resume.linkedin:
            contact_parts.append(parsed_resume.linkedin)
        if parsed_resume.location:
            contact_parts.append(parsed_resume.location)
        contact_line = "  |  ".join(contact_parts)

    if contact_line:
        story.append(Paragraph(md_to_rl(contact_line), styles['ContactInfo']))

    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#1a1a6c')))
    story.append(Spacer(1, 4))

    # ========== PROFESSIONAL SUMMARY ==========
    summary_text = sections['summary'].strip() if sections['summary'] else parsed_resume.summary
    if summary_text:
        story.append(Paragraph("PROFESSIONAL SUMMARY", styles['SectionHeading']))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#cccccc')))
        summary_text = ' '.join(summary_text.split())
        story.append(Paragraph(md_to_rl(summary_text), styles['ResumeNormal']))
        story.append(Spacer(1, 4))

    # ========== SKILLS (AI-Enhanced) ==========
    skill_categories = parse_skills_section(sections['skills']) if sections['skills'] else []

    if skill_categories:
        story.append(Paragraph("SKILLS &amp; COMPETENCIES", styles['SectionHeading']))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#cccccc')))
        for cat in skill_categories:
            if cat['category']:
                text = f"<b>{md_to_rl(cat['category'])}:</b> {md_to_rl(cat['skills'])}"
            else:
                text = md_to_rl(cat['skills'])
            story.append(Paragraph(text, styles['SkillCategory']))
        story.append(Spacer(1, 4))
    elif parsed_resume.skills:
        story.append(Paragraph("SKILLS &amp; COMPETENCIES", styles['SectionHeading']))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#cccccc')))
        story.append(Paragraph(md_to_rl(", ".join(parsed_resume.skills)), styles['ResumeNormal']))
        story.append(Spacer(1, 4))

    # ========== PROFESSIONAL EXPERIENCE (AI-Enhanced) ==========
    exp_entries = parse_experience_section(sections['experience']) if sections['experience'] else []

    if exp_entries:
        story.append(Paragraph("PROFESSIONAL EXPERIENCE", styles['SectionHeading']))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#cccccc')))
        for entry in exp_entries:
            story.append(Paragraph(f"<b>{md_to_rl(entry['title_line'])}</b>", styles['JobTitle']))
            if entry.get('detail_line'):
                story.append(Paragraph(md_to_rl(entry['detail_line']), styles['Company']))
            if entry['bullets']:
                bullets = []
                for b in entry['bullets']:
                    bullets.append(ListItem(Paragraph(md_to_rl(b), styles['BulletPoint'])))
                story.append(ListFlowable(bullets, bulletType='bullet', start='\u2022', leftIndent=15, bulletFontSize=7))
            story.append(Spacer(1, 3))
    elif parsed_resume.experience:
        story.append(Paragraph("PROFESSIONAL EXPERIENCE", styles['SectionHeading']))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#cccccc')))
        for exp in parsed_resume.experience:
            title_line = f"<b>{md_to_rl(exp.job_title)}</b>  |  {md_to_rl(exp.company)}"
            story.append(Paragraph(title_line, styles['JobTitle']))
            detail_parts = []
            if exp.duration:
                detail_parts.append(exp.duration)
            if exp.location:
                detail_parts.append(exp.location)
            if detail_parts:
                story.append(Paragraph(md_to_rl(" | ".join(detail_parts)), styles['Company']))
            if exp.responsibilities:
                bullets = [ListItem(Paragraph(md_to_rl(r), styles['BulletPoint'])) for r in exp.responsibilities]
                story.append(ListFlowable(bullets, bulletType='bullet', start='\u2022', leftIndent=15, bulletFontSize=7))
            story.append(Spacer(1, 3))

    # ========== PROJECTS (AI-Enhanced) ==========
    proj_entries = parse_projects_section(sections['projects']) if sections['projects'] else []

    if proj_entries:
        story.append(Paragraph("PROJECTS", styles['SectionHeading']))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#cccccc')))
        for proj in proj_entries:
            proj_name = proj['name'].replace('**', '')
            story.append(Paragraph(f"<b>{md_to_rl(proj_name)}</b>", styles['JobTitle']))
            if proj.get('technologies'):
                story.append(Paragraph(f"<i>Technologies: {md_to_rl(proj['technologies'])}</i>", styles['Company']))
            if proj['bullets']:
                bullets = [ListItem(Paragraph(md_to_rl(b), styles['BulletPoint'])) for b in proj['bullets']]
                story.append(ListFlowable(bullets, bulletType='bullet', start='\u2022', leftIndent=15, bulletFontSize=7))
            story.append(Spacer(1, 3))
    elif parsed_resume.projects:
        story.append(Paragraph("PROJECTS", styles['SectionHeading']))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#cccccc')))
        for proj in parsed_resume.projects:
            story.append(Paragraph(f"<b>{md_to_rl(proj.name)}</b>", styles['JobTitle']))
            if proj.technologies:
                story.append(Paragraph(f"<i>Technologies: {md_to_rl(', '.join(proj.technologies))}</i>", styles['Company']))
            bullets = []
            if proj.description:
                bullets.append(ListItem(Paragraph(md_to_rl(proj.description), styles['BulletPoint'])))
            for h in proj.highlights:
                bullets.append(ListItem(Paragraph(md_to_rl(h), styles['BulletPoint'])))
            if bullets:
                story.append(ListFlowable(bullets, bulletType='bullet', start='\u2022', leftIndent=15, bulletFontSize=7))
            story.append(Spacer(1, 3))

    # ========== EDUCATION (from AI text, fallback to parsed) ==========
    edu_entries = parse_education_section(sections['education']) if sections['education'] else []

    if edu_entries:
        story.append(Paragraph("EDUCATION", styles['SectionHeading']))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#cccccc')))
        for edu in edu_entries:
            story.append(Paragraph(f"<b>{md_to_rl(edu['title'])}</b>", styles['JobTitle']))
            if edu.get('subtitle'):
                story.append(Paragraph(md_to_rl(edu['subtitle']), styles['Company']))
            for detail in edu.get('details', []):
                story.append(Paragraph(f"  {md_to_rl(detail)}", styles['BulletPoint']))
            story.append(Spacer(1, 3))
    elif parsed_resume.education:
        story.append(Paragraph("EDUCATION", styles['SectionHeading']))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#cccccc')))
        for edu in parsed_resume.education:
            degree_text = edu.degree
            if edu.field_of_study:
                degree_text += f" in {edu.field_of_study}"
            story.append(Paragraph(f"<b>{md_to_rl(degree_text)}</b>", styles['JobTitle']))
            edu_details = []
            if edu.institution:
                edu_details.append(edu.institution)
            if edu.graduation_date:
                edu_details.append(edu.graduation_date)
            if edu.gpa:
                edu_details.append(f"GPA: {edu.gpa}")
            if edu_details:
                story.append(Paragraph(md_to_rl(" | ".join(edu_details)), styles['Company']))
            story.append(Spacer(1, 3))

    # ========== CERTIFICATIONS (from AI text, fallback to parsed) ==========
    certs_from_text = parse_certifications_section(sections['certifications']) if sections['certifications'] else []

    if certs_from_text:
        story.append(Paragraph("CERTIFICATIONS", styles['SectionHeading']))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#cccccc')))
        for cert in certs_from_text:
            story.append(Paragraph(f"\u2022  {md_to_rl(cert)}", styles['ResumeNormal']))
    elif parsed_resume.certifications:
        story.append(Paragraph("CERTIFICATIONS", styles['SectionHeading']))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#cccccc')))
        for cert in parsed_resume.certifications:
            story.append(Paragraph(f"\u2022  {md_to_rl(cert)}", styles['ResumeNormal']))

    # ========== LANGUAGES ==========
    languages_text = sections.get('languages', '').strip()
    if languages_text:
        story.append(Paragraph("LANGUAGES", styles['SectionHeading']))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#cccccc')))
        # Clean bullet points
        lang_items = []
        for line in languages_text.split('\n'):
            line = line.strip().lstrip('•-*– ')
            if line:
                lang_items.append(line)
        if lang_items:
            story.append(Paragraph(md_to_rl(", ".join(lang_items)), styles['ResumeNormal']))
    elif parsed_resume.languages:
        story.append(Paragraph("LANGUAGES", styles['SectionHeading']))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#cccccc')))
        story.append(Paragraph(md_to_rl(", ".join(parsed_resume.languages)), styles['ResumeNormal']))

    # Build PDF
    doc.build(story)
    buffer.seek(0)

    return buffer
