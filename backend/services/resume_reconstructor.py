"""
Resume Reconstructor Service
Core engine for JD-tailored Resume Enhancement - ADDS missing skills intelligently
"""

from typing import Dict, Any, Tuple
import json
from services.ai_providers import get_ai_response
from services.resume_parser import ParsedResume
from services.gap_analyzer import GapAnalysis, analyze_gaps


def get_enhancement_prompt(
    parsed_resume: ParsedResume,
    job_description: str,
    job_position: str,
    gap_analysis: GapAnalysis
) -> str:
    """Generate the enhancement prompt that FORCES JD-tailored output."""
    resume_json = json.dumps(parsed_resume.to_dict(), indent=2)
    
    missing_skills = ", ".join(gap_analysis.missing_keywords) if gap_analysis.missing_keywords else "None"
    matched_skills = ", ".join(gap_analysis.matched_skills) if gap_analysis.matched_skills else "None"
    priority_skills = ", ".join(gap_analysis.priority_skills) if gap_analysis.priority_skills else "None"
    
    return f'''You are a Resume Enhancement AI. Your ONLY job is to output a COMPLETE enhanced resume.

CRITICAL REQUIREMENTS:
1. You MUST add these MISSING SKILLS to the Skills section: {missing_skills}
2. You MUST rewrite the Professional Summary to target "{job_position}"
3. You MUST rewrite experience bullet points using JD keywords
4. You MUST enhance project descriptions to highlight JD-relevant technologies
5. You MUST keep ALL original content - never remove anything
6. You MUST use the EXACT output format shown below with === SECTION === markers

ORIGINAL RESUME DATA:
{resume_json}

TARGET POSITION: {job_position}

JOB DESCRIPTION:
{job_description}

ALREADY MATCHED SKILLS: {matched_skills}
MISSING SKILLS TO ADD: {missing_skills}
PRIORITY SKILLS: {priority_skills}

OUTPUT THE COMPLETE ENHANCED RESUME IN THIS EXACT FORMAT:

=== HEADER ===
{parsed_resume.name}
{parsed_resume.email} | {parsed_resume.phone} | {parsed_resume.linkedin or ''} | {parsed_resume.location or ''}

=== PROFESSIONAL SUMMARY ===
[Write 2-3 NEW sentences targeting {job_position}. Mention key matching skills from JD. Sound professional and confident.]

=== SKILLS ===
Programming Languages: [include original + add missing ones like {missing_skills}]
Frameworks & Libraries: [include original + add JD-required ones]
AI & ML: [include original + add JD-required ones]
Tools & Technologies: [include original + add JD-required ones]
Databases: [list if applicable]
Other: [any remaining skills]

=== PROFESSIONAL EXPERIENCE ===
[For EACH job entry, output:]
[Job Title] | [Company Name]
[Duration] | [Location]
* [Rewritten bullet with JD keywords and action verbs]
* [Rewritten bullet with quantified achievements]

=== PROJECTS ===
[For EACH project, output:]
[Project Name]
Technologies: [original technologies + add JD-relevant ones where applicable]
* [Enhanced description highlighting JD-relevant aspects]

=== EDUCATION ===
[Degree] in [Field]
[Institution] | [Graduation Date] | [GPA if available]

=== CERTIFICATIONS ===
* [List each certification]

=== LANGUAGES ===
[List all languages]

IMPORTANT: Start your response with === HEADER === and include ALL sections. Do NOT add any text before === HEADER === or after the last section.'''


def reconstruct_resume_fast(
    parsed_resume: ParsedResume,
    job_description: str,
    job_position: str,
    provider: str,
    model: str
) -> Tuple[GapAnalysis, str]:
    """
    Fast reconstruction pipeline:
    1. Gap analysis (AI call 1)
    2. Enhancement with gap results (AI call 2)
    
    Returns (gap_analysis, reconstructed_text) tuple.
    """
    print("[PDF Pipeline] Step 1: Running gap analysis...")
    gap_analysis = analyze_gaps(
        parsed_resume, job_description, job_position, provider, model
    )
    print(f"[PDF Pipeline] Gap analysis done. Missing: {gap_analysis.missing_keywords[:5]}...")
    
    print("[PDF Pipeline] Step 2: Running reconstruction with JD tailoring...")
    prompt = get_enhancement_prompt(
        parsed_resume, job_description, job_position, gap_analysis
    )
    response = get_ai_response(prompt, provider, model)
    
    # Clean up response
    reconstructed = response.strip()
    
    # Remove any markdown code blocks
    if reconstructed.startswith("```"):
        lines = reconstructed.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        reconstructed = "\n".join(lines)
    
    # Ensure we start from === HEADER === if there's extra text before it
    header_idx = reconstructed.find("=== HEADER ===")
    if header_idx == -1:
        header_idx = reconstructed.find("===HEADER===")
    if header_idx > 0:
        reconstructed = reconstructed[header_idx:]
    
    # Debug: print what sections were found
    section_names = [line.strip() for line in reconstructed.split('\n') if '===' in line]
    print(f"[PDF Pipeline] Sections found in AI output: {section_names}")
    print(f"[PDF Pipeline] Reconstructed text length: {len(reconstructed)} chars")
    
    return gap_analysis, reconstructed


def reconstruct_resume(
    parsed_resume: ParsedResume,
    job_description: str,
    job_position: str,
    gap_analysis: GapAnalysis,
    provider: str,
    model: str
) -> str:
    """
    Reconstruct resume (used by DOCX/preview endpoints).
    """
    prompt = get_enhancement_prompt(
        parsed_resume, job_description, job_position, gap_analysis
    )
    
    response = get_ai_response(prompt, provider, model)
    reconstructed = response.strip()
    
    if reconstructed.startswith("```"):
        lines = reconstructed.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        reconstructed = "\n".join(lines)
    
    # Ensure we start from === HEADER ===
    header_idx = reconstructed.find("=== HEADER ===")
    if header_idx == -1:
        header_idx = reconstructed.find("===HEADER===")
    if header_idx > 0:
        reconstructed = reconstructed[header_idx:]
    
    return reconstructed


def validate_reconstruction(
    original: ParsedResume,
    reconstructed_text: str
) -> Dict[str, Any]:
    """Validate that reconstructed resume contains enhanced content."""
    validation = {
        "valid": True,
        "warnings": [],
        "original_name": original.name,
        "original_email": original.email,
        "original_skills_count": len(original.skills),
        "original_experience_count": len(original.experience)
    }
    
    if original.name and original.name.lower() not in reconstructed_text.lower():
        validation["warnings"].append("Original name may not be present in output")
    
    if original.email and original.email.lower() not in reconstructed_text.lower():
        validation["warnings"].append("Original email may not be present in output")
    
    if "skills" not in reconstructed_text.lower():
        validation["warnings"].append("Skills section may be missing")
    
    if validation["warnings"]:
        validation["valid"] = False
    
    return validation
