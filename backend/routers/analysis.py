"""
Analysis Router
API endpoints for CV analysis
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
from services.ai_providers import get_ai_response
from services.cv_processor import extract_text, get_analysis_prompt, parse_json_response

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


@router.post("")
async def analyze_cv(
    file: UploadFile = File(...),
    job_description: str = Form(...),
    job_position: str = Form(...),
    provider: str = Form(...),
    model: str = Form(...)
):
    """
    Analyze a CV against a job description.
    
    Returns ATS analysis including:
    - JD Match percentage
    - Missing keywords
    - Key strengths
    - Recommendations
    - Profile summary
    - Breakdown scores (Experience, Skills, Education)
    """
    try:
        # Read file
        file_bytes = await file.read()
        file_type = file.filename.split('.')[-1].lower()
        
        if file_type not in ["pdf", "docx"]:
            raise HTTPException(status_code=400, detail="Unsupported file type. Use PDF or DOCX.")
        
        # Extract text
        cv_text = extract_text(file_bytes, file_type)
        
        if not cv_text.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from file.")
        
        # Generate prompt and get AI response
        prompt = get_analysis_prompt(cv_text, job_description, job_position)
        response = get_ai_response(prompt, provider, model)
        
        # Parse response
        result = parse_json_response(response)
        
        if not result:
            raise HTTPException(status_code=500, detail="Failed to parse AI response.")
        
        # Add file info
        result["filename"] = file.filename
        result["file_type"] = file_type
        
        return {
            "success": True,
            "analysis": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_details = {
            "error": str(e),
            "type": type(e).__name__,
            "traceback": traceback.format_exc()
        }
        print(f"ERROR in /api/analysis: {error_details}")
        raise HTTPException(status_code=500, detail=str(e))
