"""
Analysis Router
API endpoints for CV analysis
"""

from concurrent.futures import ThreadPoolExecutor
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
from services.ai_providers import get_ai_response
from services.cv_processor import extract_text, get_analysis_prompt, parse_json_response
from services.resume_parser import parse_resume
from services.session_cache import generate_session_id, store_session

router = APIRouter(prefix="/api/analysis", tags=["analysis"])

# Background thread pool for non-blocking cache warming
_cache_executor = ThreadPoolExecutor(max_workers=2)


def _cache_parsed_resume(cv_text: str, provider: str, model: str,
                         file_bytes: bytes, job_description: str, job_position: str):
    """Background task: parse resume and store in cache (non-blocking)."""
    try:
        parsed_resume = parse_resume(cv_text, provider, model)
        session_id = generate_session_id(file_bytes, job_description)
        store_session(
            session_id=session_id,
            cv_text=cv_text,
            parsed_resume=parsed_resume,
            file_bytes=file_bytes,
            job_description=job_description,
            job_position=job_position,
        )
        print(f"[Cache] Session stored in background: {session_id}")
    except Exception as cache_err:
        print(f"[Cache] Background parse failed (non-critical): {cache_err}")


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
    
    Also parses and caches the resume so that subsequent
    DOCX/PDF generation skips the parse step (saves ~1 AI call).
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
        
        # Generate prompt and get AI response (AI call 1: analysis)
        prompt = get_analysis_prompt(cv_text, job_description, job_position)
        response = get_ai_response(prompt, provider, model)
        
        # Parse response
        result = parse_json_response(response)
        
        if not result:
            raise HTTPException(status_code=500, detail="Failed to parse AI response.")
        
        # Parse resume in BACKGROUND (non-blocking) for cache warming.
        # The user gets analysis results immediately. By the time they
        # click Generate DOCX/PDF, the cache will likely be ready.
        session_id = generate_session_id(file_bytes, job_description)
        _cache_executor.submit(
            _cache_parsed_resume,
            cv_text, provider, model,
            file_bytes, job_description, job_position
        )
        
        # Add file info
        result["filename"] = file.filename
        result["file_type"] = file_type
        
        return {
            "success": True,
            "analysis": result,
            "session_id": session_id,
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
