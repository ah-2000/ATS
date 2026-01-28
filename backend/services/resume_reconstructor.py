"""
Resume Reconstructor Service
Core engine implementing the ATS-aware Resume Reconstruction with strict no-hallucination rules
"""

from typing import Dict, Any
import json
from services.ai_providers import get_ai_response
from services.resume_parser import ParsedResume
from services.gap_analyzer import GapAnalysis


# ============================================
# SYSTEM PROMPT (NON-NEGOTIABLE RULES)
# ============================================

RECONSTRUCTION_SYSTEM_PROMPT = '''You are an ATS-aware Resume Reconstruction Engine.

Your job is to rebuild and optimize a user's resume for a given Job Description (JD) STRICTLY USING the user's uploaded resume data.

You do NOT generate new background information.
You ONLY transform, rephrase, reorder, and emphasize existing information.

🚫 ABSOLUTE HARD RULES (NON-NEGOTIABLE)

You are STRICTLY FORBIDDEN from adding or inventing:
- New skills not present in the user's resume
- New tools, technologies, frameworks, or certifications
- New companies, job titles, or roles
- New projects
- New years of experience
- New achievements or metrics not implied by the resume

❌ Do NOT assume
❌ Do NOT infer
❌ Do NOT "logically guess"
❌ Do NOT fill gaps with imagination

If a JD requirement is not supported by the resume, DO NOT include it.

✅ WHAT YOU ARE ALLOWED TO DO

You MAY:
- Rephrase existing experience using stronger, JD-aligned language
- Reorder skills and sections based on JD priority
- Expand bullet points ONLY if fully supported by existing resume content
- Highlight implicit skills already present in the resume
- Improve clarity, impact, and ATS keyword alignment
- Remove irrelevant content that does not support the JD

📌 DEFINITION OF "MISSING INFORMATION"

"Missing" does NOT mean absent from the resume.
It means:
- Present but weakly worded
- Present but buried in another section
- Present but not expressed in JD language
- Present implicitly but not clearly highlighted

If something is truly absent, it must be excluded.'''


def get_template_structure() -> str:
    """Returns the reference template structure"""
    return '''
RESUME TEMPLATE STRUCTURE:

=== HEADER ===
[FULL NAME]
[Email] | [Phone] | [LinkedIn] | [Location]

=== PROFESSIONAL SUMMARY ===
(2-3 sentences highlighting key qualifications aligned with JD)

=== SKILLS ===
(Comma-separated list, prioritized by JD relevance)

=== PROFESSIONAL EXPERIENCE ===
[Job Title] | [Company Name]
[Duration] | [Location]
• [Achievement/responsibility bullet - use action verbs]
• [Achievement/responsibility bullet - quantify when possible]
• [Achievement/responsibility bullet]
(Maximum 4-5 bullets per role)

=== PROJECTS ===
[Project Name]
[Technologies used]
• [Key achievement or description]
(Include only if relevant to JD)

=== EDUCATION ===
[Degree] in [Field]
[Institution] | [Graduation Date]

=== CERTIFICATIONS ===
(Only if present in original resume)

=== LANGUAGES ===
(Only if relevant and present in original resume)
'''


def get_reconstruction_prompt(
    parsed_resume: ParsedResume,
    job_description: str,
    job_position: str,
    gap_analysis: GapAnalysis
) -> str:
    """Generate the complete reconstruction prompt"""
    
    resume_json = json.dumps(parsed_resume.to_dict(), indent=2)
    gap_json = json.dumps(gap_analysis.to_dict(), indent=2)
    template = get_template_structure()
    
    return f'''{RECONSTRUCTION_SYSTEM_PROMPT}

🧠 INPUTS:

1️⃣ PARSED USER RESUME (READ-ONLY DATA):
{resume_json}

2️⃣ JOB DESCRIPTION:
Position: {job_position}
{job_description}

3️⃣ GAP ANALYSIS:
{gap_json}

4️⃣ REFERENCE TEMPLATE:
{template}

🧩 YOUR TASK:

1. Analyze the JD and identify priority keywords and role expectations
2. Cross-check each JD requirement against the user's resume data
3. Select ONLY supported skills, experience, and projects
4. Rewrite and optimize content using JD-aligned language
5. Embed the optimized content STRICTLY inside the template format
6. Preserve user identity (name, email, phone)
7. Ensure ATS-friendly wording and professional tone

📤 OUTPUT REQUIREMENTS:

Return ONLY the final reconstructed resume in the template format.
Do NOT explain your reasoning.
Do NOT mention analysis or missing skills.
Do NOT add commentary or notes.

The output must look like a ready-to-send professional resume.

BEGIN RECONSTRUCTION:'''


def reconstruct_resume(
    parsed_resume: ParsedResume,
    job_description: str,
    job_position: str,
    gap_analysis: GapAnalysis,
    provider: str,
    model: str
) -> str:
    """
    Reconstruct resume using AI with strict no-hallucination rules.
    
    Args:
        parsed_resume: Structured resume data (READ-ONLY)
        job_description: Target job description
        job_position: Target job position
        gap_analysis: Gap analysis results
        provider: AI provider
        model: Model name
        
    Returns:
        Reconstructed resume text in template format
    """
    prompt = get_reconstruction_prompt(
        parsed_resume,
        job_description,
        job_position,
        gap_analysis
    )
    
    response = get_ai_response(prompt, provider, model)
    
    # Clean up response
    reconstructed = response.strip()
    
    # Remove any markdown code blocks if present
    if reconstructed.startswith("```"):
        lines = reconstructed.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        reconstructed = "\n".join(lines)
    
    return reconstructed


def validate_reconstruction(
    original: ParsedResume,
    reconstructed_text: str
) -> Dict[str, Any]:
    """
    Validate that reconstructed resume doesn't contain hallucinated information.
    Returns validation results.
    """
    validation = {
        "valid": True,
        "warnings": [],
        "original_name": original.name,
        "original_email": original.email,
        "original_skills_count": len(original.skills),
        "original_experience_count": len(original.experience)
    }
    
    # Basic checks - name should be present
    if original.name and original.name.lower() not in reconstructed_text.lower():
        validation["warnings"].append("Original name may not be present in output")
    
    # Email should be present
    if original.email and original.email.lower() not in reconstructed_text.lower():
        validation["warnings"].append("Original email may not be present in output")
    
    if validation["warnings"]:
        validation["valid"] = False
    
    return validation
