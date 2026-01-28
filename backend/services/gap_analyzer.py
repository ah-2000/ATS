"""
Gap Analyzer Service
Analyzes gaps between parsed resume and job description
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any
import json
from services.ai_providers import get_ai_response
from services.resume_parser import ParsedResume


@dataclass
class GapAnalysis:
    """Gap analysis results"""
    missing_keywords: List[str] = field(default_factory=list)
    weak_sections: List[str] = field(default_factory=list)
    improvement_recommendations: List[str] = field(default_factory=list)
    priority_skills: List[str] = field(default_factory=list)
    jd_keywords: List[str] = field(default_factory=list)
    matched_skills: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "missing_keywords": self.missing_keywords,
            "weak_sections": self.weak_sections,
            "improvement_recommendations": self.improvement_recommendations,
            "priority_skills": self.priority_skills,
            "jd_keywords": self.jd_keywords,
            "matched_skills": self.matched_skills
        }


def get_gap_analysis_prompt(parsed_resume: ParsedResume, job_description: str, job_position: str) -> str:
    """Generate prompt for gap analysis"""
    resume_json = json.dumps(parsed_resume.to_dict(), indent=2)
    
    return f'''You are an expert ATS (Applicant Tracking System) analyst.

Analyze the gap between this resume and job description for the position: {job_position}

**Parsed Resume Data:**
{resume_json}

**Job Description:**
{job_description}

**Your Task:**
1. Identify keywords from the JD that are PRESENT in the resume (matched)
2. Identify keywords from the JD that are MISSING from the resume
3. Identify which sections of the resume are weak or need improvement
4. Provide specific recommendations for how to optimize the resume
5. List the priority skills the JD is looking for

**IMPORTANT:** 
- "Missing" means truly absent from the resume
- Some skills may be present but weakly worded - these go in weak_sections
- Some skills may be implicit - these are matched, not missing

**Return ONLY valid JSON:**
{{
    "jd_keywords": ["keyword1", "keyword2"],
    "matched_skills": ["skill from resume that matches JD"],
    "missing_keywords": ["truly absent skills"],
    "weak_sections": ["sections that need improvement"],
    "improvement_recommendations": ["specific actionable recommendations"],
    "priority_skills": ["most important skills from JD"]
}}

Return ONLY the JSON, no explanation.'''


def parse_json_safely(response: str) -> Dict[str, Any]:
    """Parse JSON from AI response"""
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
        return {}


def analyze_gaps(
    parsed_resume: ParsedResume,
    job_description: str,
    job_position: str,
    provider: str,
    model: str
) -> GapAnalysis:
    """
    Analyze gaps between resume and job description.
    
    Args:
        parsed_resume: Structured resume data
        job_description: Target job description
        job_position: Target job position
        provider: AI provider
        model: Model name
        
    Returns:
        GapAnalysis object with identified gaps and recommendations
    """
    prompt = get_gap_analysis_prompt(parsed_resume, job_description, job_position)
    response = get_ai_response(prompt, provider, model)
    
    data = parse_json_safely(response)
    
    return GapAnalysis(
        missing_keywords=data.get("missing_keywords", []),
        weak_sections=data.get("weak_sections", []),
        improvement_recommendations=data.get("improvement_recommendations", []),
        priority_skills=data.get("priority_skills", []),
        jd_keywords=data.get("jd_keywords", []),
        matched_skills=data.get("matched_skills", [])
    )
