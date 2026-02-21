"""
Session Cache Service
Caches parsed resume data to avoid redundant AI calls during reconstruction.

After analysis, the parsed resume and extracted text are cached.
When generating DOCX/PDF, the cached data is reused — saving 1 full AI call.
"""

import hashlib
import time
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from services.resume_parser import ParsedResume


@dataclass
class CachedSession:
    """Cached data from a previous analysis/parse"""
    cv_text: str
    parsed_resume: ParsedResume
    file_hash: str
    created_at: float
    job_description: str = ""
    job_position: str = ""


# In-memory cache (keyed by session_id)
_cache: Dict[str, CachedSession] = {}

# Cache TTL: 30 minutes
CACHE_TTL = 30 * 60


def _generate_file_hash(file_bytes: bytes) -> str:
    """Generate a hash for file content."""
    return hashlib.md5(file_bytes).hexdigest()


def generate_session_id(file_bytes: bytes, job_description: str) -> str:
    """Generate a unique session ID from file + job description."""
    combined = _generate_file_hash(file_bytes) + hashlib.md5(job_description.encode()).hexdigest()
    return hashlib.md5(combined.encode()).hexdigest()[:16]


def store_session(
    session_id: str,
    cv_text: str,
    parsed_resume: ParsedResume,
    file_bytes: bytes,
    job_description: str = "",
    job_position: str = ""
) -> None:
    """Store parsed data in cache."""
    _cache[session_id] = CachedSession(
        cv_text=cv_text,
        parsed_resume=parsed_resume,
        file_hash=_generate_file_hash(file_bytes),
        created_at=time.time(),
        job_description=job_description,
        job_position=job_position,
    )
    _cleanup_expired()


def get_session(session_id: str) -> Optional[CachedSession]:
    """Retrieve cached session if it exists and is not expired."""
    session = _cache.get(session_id)
    if session is None:
        return None
    if time.time() - session.created_at > CACHE_TTL:
        del _cache[session_id]
        return None
    return session


def _cleanup_expired() -> None:
    """Remove expired entries (runs on each store)."""
    now = time.time()
    expired = [k for k, v in _cache.items() if now - v.created_at > CACHE_TTL]
    for k in expired:
        del _cache[k]
