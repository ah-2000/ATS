/**
 * API Client for Smart ATS Backend
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface ModelStatus {
    [provider: string]: {
        available: boolean;
        models: string[];
    };
}

export interface AnalysisResult {
    "JD Match": string;
    MissingKeywords: string[];
    KeyStrength: string;
    Recommendations: string;
    "Profile Summary": string;
    ExperienceMatch: string;
    SkillsMatch: string;
    EducationMatch: string;
    filename: string;
    file_type: string;
}

/**
 * Get available AI models
 */
export async function getModels(): Promise<ModelStatus> {
    const response = await fetch(`${API_BASE_URL}/api/models`);
    if (!response.ok) {
        throw new Error('Failed to fetch models');
    }
    return response.json();
}

/**
 * Analyze a CV against a job description
 */
export async function analyzeCV(
    file: File,
    jobDescription: string,
    jobPosition: string,
    provider: string,
    model: string
): Promise<{ success: boolean; analysis: AnalysisResult }> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('job_description', jobDescription);
    formData.append('job_position', jobPosition);
    formData.append('provider', provider);
    formData.append('model', model);

    const response = await fetch(`${API_BASE_URL}/api/analysis`, {
        method: 'POST',
        body: formData,
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Analysis failed');
    }

    return response.json();
}

// ============================================
// RECONSTRUCTION API
// ============================================

export interface ReconstructionPreview {
    success: boolean;
    reconstructed_text: string;
    validation: {
        valid: boolean;
        warnings: string[];
    };
    gap_analysis: {
        missing_keywords: string[];
        weak_sections: string[];
        improvement_recommendations: string[];
        priority_skills: string[];
        matched_skills: string[];
    };
    parsed_resume_summary: {
        name: string;
        skills_count: number;
        experience_count: number;
        projects_count: number;
    };
}

/**
 * Preview reconstructed resume (returns text, not file)
 */
export async function previewReconstruction(
    file: File,
    jobDescription: string,
    jobPosition: string,
    provider: string,
    model: string
): Promise<ReconstructionPreview> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('job_description', jobDescription);
    formData.append('job_position', jobPosition);
    formData.append('provider', provider);
    formData.append('model', model);

    const response = await fetch(`${API_BASE_URL}/api/reconstruct/preview`, {
        method: 'POST',
        body: formData,
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Reconstruction preview failed');
    }

    return response.json();
}

/**
 * Reconstruct and download resume as DOCX
 */
export async function reconstructResume(
    file: File,
    jobDescription: string,
    jobPosition: string,
    provider: string,
    model: string
): Promise<Blob> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('job_description', jobDescription);
    formData.append('job_position', jobPosition);
    formData.append('provider', provider);
    formData.append('model', model);

    const response = await fetch(`${API_BASE_URL}/api/reconstruct`, {
        method: 'POST',
        body: formData,
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Reconstruction failed');
    }

    return response.blob();
}

/**
 * Download blob as file
 */
export function downloadBlob(blob: Blob, filename: string) {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
}
