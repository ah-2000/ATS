"""
Reconstruction Router
API endpoints for resume reconstruction

OPTIMIZED: Uses session cache to skip redundant AI calls.
- With cache hit: 1 AI call (reconstruct only) instead of 3
- Without cache: falls back to full pipeline (parse + gap + reconstruct)
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
from typing import Optional
from io import BytesIO

from services.cv_processor import extract_text
from services.resume_parser import parse_resume
from services.gap_analyzer import analyze_gaps
from services.resume_reconstructor import (
    reconstruct_resume, validate_reconstruction,
    reconstruct_resume_fast
)
from services.template_handler import create_styled_docx, get_default_template_info
from services.pdf_template_generator import create_resume_pdf
from services.session_cache import get_session, generate_session_id

router = APIRouter(prefix="/api/reconstruct", tags=["reconstruction"])


@router.post("")
async def reconstruct_cv(
    file: UploadFile = File(...),
    job_description: str = Form(...),
    job_position: str = Form(...),
    provider: str = Form(...),
    model: str = Form(...),
    session_id: str = Form("")
):
    """
    Reconstruct a CV for a specific job description → downloadable DOCX.
    
    OPTIMIZED: If session_id is provided and cache hit, skips parsing
    (saves 1 AI call). Also uses fast pipeline (gap+reconstruct combined).
    """
    try:
        # Read file
        file_bytes = await file.read()
        file_type = file.filename.split('.')[-1].lower()
        
        if file_type not in ["pdf", "docx"]:
            raise HTTPException(status_code=400, detail="Unsupported file type. Use PDF or DOCX.")
        
        # Try cache first
        cached = None
        if session_id:
            cached = get_session(session_id)
        if not cached:
            # Try auto-generating session_id from content
            auto_id = generate_session_id(file_bytes, job_description)
            cached = get_session(auto_id)
        
        if cached:
            print(f"[DOCX] Cache HIT — skipping parse (saving ~1 AI call)")
            parsed_resume = cached.parsed_resume
        else:
            print(f"[DOCX] Cache MISS — running full pipeline")
            cv_text = extract_text(file_bytes, file_type)
            if not cv_text.strip():
                raise HTTPException(status_code=400, detail="Could not extract text from file.")
            parsed_resume = parse_resume(cv_text, provider, model)
        
        # Use fast pipeline: gap + reconstruct in 1 AI call (instead of 2)
        gap_analysis, reconstructed_text = reconstruct_resume_fast(
            parsed_resume, job_description, job_position, provider, model
        )
        
        # Validate
        validation = validate_reconstruction(parsed_resume, reconstructed_text)
        
        # Generate DOCX
        docx_buffer = create_styled_docx(reconstructed_text)
        
        original_name = file.filename.rsplit('.', 1)[0]
        output_filename = f"{original_name}_reconstructed.docx"
        
        return StreamingResponse(
            docx_buffer,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={
                "Content-Disposition": f'attachment; filename="{output_filename}"'
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/preview")
async def preview_reconstruction(
    file: UploadFile = File(...),
    job_description: str = Form(...),
    job_position: str = Form(...),
    provider: str = Form(...),
    model: str = Form(...),
    session_id: str = Form("")
):
    """
    Preview the reconstructed resume as text.
    Uses cache when available to skip parsing.
    """
    try:
        file_bytes = await file.read()
        file_type = file.filename.split('.')[-1].lower()
        
        if file_type not in ["pdf", "docx"]:
            raise HTTPException(status_code=400, detail="Unsupported file type. Use PDF or DOCX.")
        
        # Try cache
        cached = None
        if session_id:
            cached = get_session(session_id)
        if not cached:
            auto_id = generate_session_id(file_bytes, job_description)
            cached = get_session(auto_id)
        
        if cached:
            print(f"[Preview] Cache HIT — skipping parse")
            parsed_resume = cached.parsed_resume
            cv_text = cached.cv_text
        else:
            print(f"[Preview] Cache MISS — full pipeline")
            cv_text = extract_text(file_bytes, file_type)
            if not cv_text.strip():
                raise HTTPException(status_code=400, detail="Could not extract text from file.")
            parsed_resume = parse_resume(cv_text, provider, model)
        
        # Fast pipeline: gap + reconstruct combined
        gap_analysis, reconstructed_text = reconstruct_resume_fast(
            parsed_resume, job_description, job_position, provider, model
        )
        
        validation = validate_reconstruction(parsed_resume, reconstructed_text)
        
        return {
            "success": True,
            "reconstructed_text": reconstructed_text,
            "validation": validation,
            "gap_analysis": gap_analysis.to_dict(),
            "parsed_resume_summary": {
                "name": parsed_resume.name,
                "skills_count": len(parsed_resume.skills),
                "experience_count": len(parsed_resume.experience),
                "projects_count": len(parsed_resume.projects)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/template")
async def get_template_info():
    """Get information about the resume template being used."""
    return get_default_template_info()


@router.post("/pdf")
async def generate_pdf_resume(
    file: UploadFile = File(...),
    job_description: str = Form(...),
    job_position: str = Form(...),
    provider: str = Form(...),
    model: str = Form(...),
    session_id: str = Form("")
):
    """
    Generate a professionally styled PDF resume tailored to the job description.
    
    OPTIMIZED: With cache hit → 1 AI call (reconstruct only).
    Without cache → 2 AI calls (parse + reconstruct).
    """
    try:
        file_bytes = await file.read()
        file_type = file.filename.split('.')[-1].lower()
        
        if file_type not in ["pdf", "docx"]:
            raise HTTPException(status_code=400, detail="Unsupported file type. Use PDF or DOCX.")
        
        # Try cache
        cached = None
        if session_id:
            cached = get_session(session_id)
        if not cached:
            auto_id = generate_session_id(file_bytes, job_description)
            cached = get_session(auto_id)
        
        if cached:
            print(f"[PDF] Cache HIT — skipping parse (saving ~1 AI call)")
            parsed_resume = cached.parsed_resume
        else:
            print(f"[PDF] Cache MISS — running parse first")
            cv_text = extract_text(file_bytes, file_type)
            if not cv_text.strip():
                raise HTTPException(status_code=400, detail="Could not extract text from file.")
            parsed_resume = parse_resume(cv_text, provider, model)
        
        # Gap analysis + Reconstruction in ONE AI call
        gap_analysis, reconstructed_text = reconstruct_resume_fast(
            parsed_resume, job_description, job_position, provider, model
        )
        
        # Generate PDF
        pdf_buffer = create_resume_pdf(
            reconstructed_text,
            parsed_resume,
            gap_analysis,
            job_position,
            job_description
        )
        
        original_name = file.filename.rsplit('.', 1)[0]
        output_filename = f"{original_name}_upgraded.pdf"
        
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{output_filename}"'
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"PDF Generation Error: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

