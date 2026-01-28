"""
Resume Parser Service
Extracts structured data from resume text using AI
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import json
from services.ai_providers import get_ai_response


@dataclass
class ExperienceEntry:
    """Work experience entry"""
    company: str
    job_title: str
    duration: str
    location: str = ""
    responsibilities: List[str] = field(default_factory=list)


@dataclass
class ProjectEntry:
    """Project entry"""
    name: str
    description: str
    technologies: List[str] = field(default_factory=list)
    highlights: List[str] = field(default_factory=list)


@dataclass
class EducationEntry:
    """Education entry"""
    institution: str
    degree: str
    field_of_study: str = ""
    graduation_date: str = ""
    gpa: str = ""


@dataclass
class ParsedResume:
    """Structured resume data - READ ONLY during reconstruction"""
    name: str = ""
    email: str = ""
    phone: str = ""
    linkedin: str = ""
    location: str = ""
    summary: str = ""
    skills: List[str] = field(default_factory=list)
    experience: List[ExperienceEntry] = field(default_factory=list)
    projects: List[ProjectEntry] = field(default_factory=list)
    education: List[EducationEntry] = field(default_factory=list)
    certifications: List[str] = field(default_factory=list)
    languages: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "linkedin": self.linkedin,
            "location": self.location,
            "summary": self.summary,
            "skills": self.skills,
            "experience": [
                {
                    "company": exp.company,
                    "job_title": exp.job_title,
                    "duration": exp.duration,
                    "location": exp.location,
                    "responsibilities": exp.responsibilities
                }
                for exp in self.experience
            ],
            "projects": [
                {
                    "name": proj.name,
                    "description": proj.description,
                    "technologies": proj.technologies,
                    "highlights": proj.highlights
                }
                for proj in self.projects
            ],
            "education": [
                {
                    "institution": edu.institution,
                    "degree": edu.degree,
                    "field_of_study": edu.field_of_study,
                    "graduation_date": edu.graduation_date,
                    "gpa": edu.gpa
                }
                for edu in self.education
            ],
            "certifications": self.certifications,
            "languages": self.languages
        }


def get_parsing_prompt(resume_text: str) -> str:
    """Generate prompt to parse resume into structured data"""
    return f'''You are an expert resume parser. Extract ALL information from the following resume into a structured JSON format.

**IMPORTANT**: Extract ONLY what is explicitly stated. Do NOT infer, guess, or add information.

**Resume Text:**
{resume_text}

**Return ONLY valid JSON in this exact format:**
{{
    "name": "Full Name",
    "email": "email@example.com",
    "phone": "+1234567890",
    "linkedin": "linkedin.com/in/username or empty string",
    "location": "City, Country or empty string",
    "summary": "Professional summary if present, empty string if not",
    "skills": ["Skill1", "Skill2", "Skill3"],
    "experience": [
        {{
            "company": "Company Name",
            "job_title": "Job Title",
            "duration": "Jan 2020 - Present",
            "location": "City, Country",
            "responsibilities": ["Responsibility 1", "Responsibility 2"]
        }}
    ],
    "projects": [
        {{
            "name": "Project Name",
            "description": "Brief description",
            "technologies": ["Tech1", "Tech2"],
            "highlights": ["Achievement 1", "Achievement 2"]
        }}
    ],
    "education": [
        {{
            "institution": "University Name",
            "degree": "Bachelor's/Master's etc",
            "field_of_study": "Computer Science",
            "graduation_date": "2020",
            "gpa": "3.8 or empty string"
        }}
    ],
    "certifications": ["Cert1", "Cert2"],
    "languages": ["English", "Spanish"]
}}

Return ONLY the JSON, no explanation or markdown formatting.'''


def parse_json_safely(response: str) -> Optional[Dict[str, Any]]:
    """Parse JSON from AI response, handling markdown code blocks"""
    try:
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        if response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]
        response = response.strip()
        return json.loads(response)
    except json.JSONDecodeError:
        return None


def parse_resume(resume_text: str, provider: str, model: str) -> ParsedResume:
    """
    Parse resume text into structured data using AI.
    
    Args:
        resume_text: Raw text extracted from resume
        provider: AI provider (Ollama, Gemini, OpenAI, Claude)
        model: Model name
        
    Returns:
        ParsedResume object with structured data
    """
    prompt = get_parsing_prompt(resume_text)
    response = get_ai_response(prompt, provider, model)
    
    data = parse_json_safely(response)
    if not data:
        raise Exception("Failed to parse resume into structured format")
    
    # Build ParsedResume object
    parsed = ParsedResume(
        name=data.get("name", ""),
        email=data.get("email", ""),
        phone=data.get("phone", ""),
        linkedin=data.get("linkedin", ""),
        location=data.get("location", ""),
        summary=data.get("summary", ""),
        skills=data.get("skills", []),
        certifications=data.get("certifications", []),
        languages=data.get("languages", [])
    )
    
    # Parse experience entries
    for exp in data.get("experience", []):
        parsed.experience.append(ExperienceEntry(
            company=exp.get("company", ""),
            job_title=exp.get("job_title", ""),
            duration=exp.get("duration", ""),
            location=exp.get("location", ""),
            responsibilities=exp.get("responsibilities", [])
        ))
    
    # Parse project entries
    for proj in data.get("projects", []):
        parsed.projects.append(ProjectEntry(
            name=proj.get("name", ""),
            description=proj.get("description", ""),
            technologies=proj.get("technologies", []),
            highlights=proj.get("highlights", [])
        ))
    
    # Parse education entries
    for edu in data.get("education", []):
        parsed.education.append(EducationEntry(
            institution=edu.get("institution", ""),
            degree=edu.get("degree", ""),
            field_of_study=edu.get("field_of_study", ""),
            graduation_date=edu.get("graduation_date", ""),
            gpa=edu.get("gpa", "")
        ))
    
    return parsed
