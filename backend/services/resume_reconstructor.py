"""
Resume Reconstructor Service
Core engine for JD-tailored Resume Enhancement - ADDS missing skills intelligently
"""

from typing import Dict, Any
import json
from services.ai_providers import get_ai_response
from services.resume_parser import ParsedResume
from services.gap_analyzer import GapAnalysis


# ============================================
# SYSTEM PROMPT FOR RESUME ENHANCEMENT
# ============================================

ENHANCEMENT_SYSTEM_PROMPT = '''You are an expert Resume Enhancement Engine.

Your job is to CREATE AN UPGRADED VERSION of the user's resume that is PERFECTLY TAILORED to the Job Description (JD).

🎯 YOUR MISSION:
Take the user's original resume and JD analysis, then OUTPUT a complete enhanced resume with:
1. ALL original content preserved and improved
2. MISSING SKILLS intelligently added into the Skills section
3. EXPERIENCE bullets rewritten to highlight JD-relevant achievements
4. PROJECTS enhanced to emphasize technologies matching the JD
5. A PROFESSIONAL SUMMARY crafted specifically for this job

✅ WHAT YOU MUST DO:

**FOR SKILLS SECTION:**
- Keep all original skills
- ADD all missing skills from the gap analysis INTO the skills section
- Organize skills by category (Programming Languages, Frameworks, Tools, Databases, Cloud, etc.)
- Prioritize JD-required skills first

**FOR EXPERIENCE SECTION:**
- Keep all original job entries
- REWRITE bullet points to use strong action verbs
- Emphasize achievements that align with JD requirements
- Add quantifiable metrics where implied (e.g., "improved performance" → "improved performance by optimizing processes")

**FOR PROJECTS SECTION:**
- Keep all original projects
- Highlight technologies that match JD requirements
- Add any missing JD technologies if the project work implies their use

**FOR SUMMARY:**
- Write a NEW 2-3 sentence professional summary
- Mention the target job role
- Highlight key skills that match the JD
- Sound confident and professional

📝 IMPORTANT RULES:
1. NEVER remove original content - only enhance it
2. ADD all missing skills from gap analysis to the Skills section
3. Make the resume sound professional and ATS-optimized
4. Use industry-standard terminology from the JD
5. Keep formatting clean and organized'''


def get_template_structure() -> str:
    """Returns the reference template structure"""
    return '''
OUTPUT FORMAT (follow exactly):

=== HEADER ===
[Full Name]
[Email] | [Phone] | [LinkedIn] | [Location]

=== PROFESSIONAL SUMMARY ===
[2-3 powerful sentences targeting the specific job role, mentioning key matching skills]

=== SKILLS ===
**Programming Languages:** [list including any missing ones from JD]
**Frameworks & Libraries:** [list including any missing ones from JD]
**Tools & Technologies:** [list including any missing ones from JD]
**Databases:** [list if applicable]
**Cloud & DevOps:** [list if applicable]
**Other:** [any remaining skills]

=== PROFESSIONAL EXPERIENCE ===
[Job Title] | [Company Name]
[Duration] | [Location]
• [Strong action verb] [achievement with JD-relevant keywords]
• [Strong action verb] [quantified result if possible]
• [Strong action verb] [technical achievement]

=== PROJECTS ===
[Project Name]
Technologies: [List including JD-relevant ones if implied]
• [Enhanced description emphasizing JD-aligned achievements]

=== EDUCATION ===
[Degree] in [Field]
[Institution] | [Graduation Date]

=== CERTIFICATIONS ===
[List all certifications]
'''


def get_enhancement_prompt(
    parsed_resume: ParsedResume,
    job_description: str,
    job_position: str,
    gap_analysis: GapAnalysis
) -> str:
    """Generate the complete enhancement prompt"""
    
    resume_json = json.dumps(parsed_resume.to_dict(), indent=2)
    
    # Format gap analysis clearly
    missing_skills = ", ".join(gap_analysis.missing_keywords) if gap_analysis.missing_keywords else "None"
    matched_skills = ", ".join(gap_analysis.matched_skills) if gap_analysis.matched_skills else "None"
    priority_skills = ", ".join(gap_analysis.priority_skills) if gap_analysis.priority_skills else "None"
    recommendations = "\n".join([f"- {r}" for r in gap_analysis.improvement_recommendations]) if gap_analysis.improvement_recommendations else "None"
    
    template = get_template_structure()
    
    return f'''{ENHANCEMENT_SYSTEM_PROMPT}

📋 ORIGINAL RESUME DATA:
{resume_json}

🎯 TARGET JOB:
Position: {job_position}

Job Description:
{job_description}

📊 GAP ANALYSIS RESULTS:

**Skills Already in Resume (Keep and Highlight):**
{matched_skills}

**MISSING SKILLS (MUST ADD TO SKILLS SECTION):**
{missing_skills}

**Priority Skills for this JD:**
{priority_skills}

**Improvement Recommendations to Apply:**
{recommendations}

{template}

⚡ ACTION REQUIRED:
1. ADD all missing skills ({missing_skills}) to the appropriate categories in the Skills section
2. REWRITE the Professional Summary for the "{job_position}" role
3. ENHANCE experience bullets with JD-aligned language
4. EMPHASIZE matching technologies in Projects
5. OUTPUT the complete enhanced resume in the format above

BEGIN ENHANCED RESUME:'''


def reconstruct_resume(
    parsed_resume: ParsedResume,
    job_description: str,
    job_position: str,
    gap_analysis: GapAnalysis,
    provider: str,
    model: str
) -> str:
    """
    Reconstruct and ENHANCE resume with missing skills integrated.
    
    Args:
        parsed_resume: Structured resume data
        job_description: Target job description
        job_position: Target job position
        gap_analysis: Gap analysis with missing skills
        provider: AI provider
        model: Model name
        
    Returns:
        Enhanced resume text with missing skills added
    """
    prompt = get_enhancement_prompt(
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
    Validate that reconstructed resume contains enhanced content.
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
    
    # Check if name is present
    if original.name and original.name.lower() not in reconstructed_text.lower():
        validation["warnings"].append("Original name may not be present in output")
    
    # Check if email is present
    if original.email and original.email.lower() not in reconstructed_text.lower():
        validation["warnings"].append("Original email may not be present in output")
    
    # Check if skills section exists
    if "skills" not in reconstructed_text.lower():
        validation["warnings"].append("Skills section may be missing")
    
    if validation["warnings"]:
        validation["valid"] = False
    
    return validation
