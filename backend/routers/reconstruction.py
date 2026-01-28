"""
Reconstruction Router
API endpoints for resume reconstruction
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
from typing import Optional
from io import BytesIO

from services.cv_processor import extract_text
from services.resume_parser import parse_resume
from services.gap_analyzer import analyze_gaps
from services.resume_reconstructor import reconstruct_resume, validate_reconstruction
from services.template_handler import create_styled_docx, get_default_template_info

router = APIRouter(prefix="/api/reconstruct", tags=["reconstruction"])


@router.post("")
async def reconstruct_cv(
    file: UploadFile = File(...),
    job_description: str = Form(...),
    job_position: str = Form(...),
    provider: str = Form(...),
    model: str = Form(...)
):
    """
    Reconstruct a CV for a specific job description.
    
    This endpoint:
    1. Extracts text from the uploaded CV
    2. Parses it into structured data
    3. Analyzes gaps against the job description
    4. Reconstructs the CV with JD-aligned language
    5. Returns a downloadable DOCX file
    
    IMPORTANT: No hallucination - only uses data from the original CV.
    """
    try:
        # Read file
        file_bytes = await file.read()
        file_type = file.filename.split('.')[-1].lower()
        
        if file_type not in ["pdf", "docx"]:
            raise HTTPException(status_code=400, detail="Unsupported file type. Use PDF or DOCX.")
        
        # Step 1: Extract text
        cv_text = extract_text(file_bytes, file_type)
        
        if not cv_text.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from file.")
        
        # Step 2: Parse resume into structured data
        parsed_resume = parse_resume(cv_text, provider, model)
        
        # Step 3: Analyze gaps
        gap_analysis = analyze_gaps(
            parsed_resume,
            job_description,
            job_position,
            provider,
            model
        )
        
        # Step 4: Reconstruct resume
        reconstructed_text = reconstruct_resume(
            parsed_resume,
            job_description,
            job_position,
            gap_analysis,
            provider,
            model
        )
        
        # Step 5: Validate (check for basic consistency)
        validation = validate_reconstruction(parsed_resume, reconstructed_text)
        
        # Step 6: Generate DOCX
        docx_buffer = create_styled_docx(reconstructed_text)
        
        # Generate filename
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
    model: str = Form(...)
):
    """
    Preview the reconstructed resume as text (without generating DOCX).
    Useful for reviewing before downloading.
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
        
        # Parse resume
        parsed_resume = parse_resume(cv_text, provider, model)
        
        # Analyze gaps
        gap_analysis = analyze_gaps(
            parsed_resume,
            job_description,
            job_position,
            provider,
            model
        )
        
        # Reconstruct
        reconstructed_text = reconstruct_resume(
            parsed_resume,
            job_description,
            job_position,
            gap_analysis,
            provider,
            model
        )
        
        # Validate
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
