'use client';

import { useState } from 'react';
import { reconstructResume, downloadBlob, previewReconstruction, ReconstructionPreview } from '@/lib/api';

interface ReconstructButtonProps {
    file: File;
    jobDescription: string;
    jobPosition: string;
    provider: string;
    model: string;
}

export default function ReconstructButton({
    file,
    jobDescription,
    jobPosition,
    provider,
    model
}: ReconstructButtonProps) {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [showPreview, setShowPreview] = useState(false);
    const [preview, setPreview] = useState<ReconstructionPreview | null>(null);

    const handlePreview = async () => {
        setLoading(true);
        setError(null);

        try {
            const result = await previewReconstruction(
                file,
                jobDescription,
                jobPosition,
                provider,
                model
            );
            setPreview(result);
            setShowPreview(true);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Preview failed');
        } finally {
            setLoading(false);
        }
    };

    const handleDownload = async () => {
        setLoading(true);
        setError(null);

        try {
            const blob = await reconstructResume(
                file,
                jobDescription,
                jobPosition,
                provider,
                model
            );

            const originalName = file.name.replace(/\.[^/.]+$/, '');
            downloadBlob(blob, `${originalName}_reconstructed.docx`);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Download failed');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="mt-6 pt-6 border-t border-[var(--color-border)]">
            <h4 className="font-semibold mb-3 flex items-center gap-2">
                🔧 Resume Reconstruction
            </h4>
            <p className="text-sm text-[var(--color-text-secondary)] mb-4">
                Optimize your resume for this job description. Uses only your existing information - no AI hallucination.
            </p>

            <div className="flex gap-3">
                <button
                    className="btn btn-secondary flex-1"
                    onClick={handlePreview}
                    disabled={loading}
                >
                    {loading && !showPreview ? (
                        <>
                            <div className="spinner"></div>
                            Analyzing...
                        </>
                    ) : (
                        <>👁️ Preview</>
                    )}
                </button>

                <button
                    className="btn btn-primary flex-1"
                    onClick={handleDownload}
                    disabled={loading}
                >
                    {loading && showPreview ? (
                        <>
                            <div className="spinner"></div>
                            Generating...
                        </>
                    ) : (
                        <>📥 Download DOCX</>
                    )}
                </button>
            </div>

            {error && (
                <div className="alert alert-error mt-4">
                    ❌ {error}
                </div>
            )}

            {/* Preview Modal */}
            {showPreview && preview && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
                    <div className="bg-[var(--color-surface)] rounded-xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
                        {/* Header */}
                        <div className="flex justify-between items-center p-4 border-b border-[var(--color-border)]">
                            <h3 className="text-lg font-semibold">📄 Reconstructed Resume Preview</h3>
                            <button
                                onClick={() => setShowPreview(false)}
                                className="text-2xl hover:opacity-70"
                            >
                                ×
                            </button>
                        </div>

                        {/* Content */}
                        <div className="flex-1 overflow-y-auto p-4">
                            {/* Summary Stats */}
                            <div className="grid grid-cols-4 gap-3 mb-4">
                                <div className="bg-[var(--color-background)] p-3 rounded-lg text-center">
                                    <p className="text-xs text-[var(--color-text-secondary)]">Skills</p>
                                    <p className="text-xl font-bold">{preview.parsed_resume_summary.skills_count}</p>
                                </div>
                                <div className="bg-[var(--color-background)] p-3 rounded-lg text-center">
                                    <p className="text-xs text-[var(--color-text-secondary)]">Experience</p>
                                    <p className="text-xl font-bold">{preview.parsed_resume_summary.experience_count}</p>
                                </div>
                                <div className="bg-[var(--color-background)] p-3 rounded-lg text-center">
                                    <p className="text-xs text-[var(--color-text-secondary)]">Projects</p>
                                    <p className="text-xl font-bold">{preview.parsed_resume_summary.projects_count}</p>
                                </div>
                                <div className="bg-[var(--color-background)] p-3 rounded-lg text-center">
                                    <p className="text-xs text-[var(--color-text-secondary)]">Matched</p>
                                    <p className="text-xl font-bold text-[var(--color-success)]">
                                        {preview.gap_analysis.matched_skills.length}
                                    </p>
                                </div>
                            </div>

                            {/* Matched Skills */}
                            {preview.gap_analysis.matched_skills.length > 0 && (
                                <div className="mb-4">
                                    <p className="text-sm font-medium mb-2">✅ JD-Matched Skills:</p>
                                    <div className="flex flex-wrap gap-2">
                                        {preview.gap_analysis.matched_skills.slice(0, 10).map((skill, idx) => (
                                            <span key={idx} className="badge badge-success">{skill}</span>
                                        ))}
                                        {preview.gap_analysis.matched_skills.length > 10 && (
                                            <span className="badge">+{preview.gap_analysis.matched_skills.length - 10} more</span>
                                        )}
                                    </div>
                                </div>
                            )}

                            {/* Validation Warnings */}
                            {preview.validation.warnings.length > 0 && (
                                <div className="alert alert-warning mb-4">
                                    <p className="font-medium mb-1">⚠️ Validation Warnings:</p>
                                    <ul className="list-disc list-inside text-sm">
                                        {preview.validation.warnings.map((warn, idx) => (
                                            <li key={idx}>{warn}</li>
                                        ))}
                                    </ul>
                                </div>
                            )}

                            {/* Resume Preview */}
                            <div className="bg-white text-black p-6 rounded-lg border shadow-inner font-mono text-sm whitespace-pre-wrap">
                                {preview.reconstructed_text}
                            </div>
                        </div>

                        {/* Footer */}
                        <div className="p-4 border-t border-[var(--color-border)] flex gap-3">
                            <button
                                className="btn btn-secondary flex-1"
                                onClick={() => setShowPreview(false)}
                            >
                                Close
                            </button>
                            <button
                                className="btn btn-primary flex-1"
                                onClick={() => {
                                    setShowPreview(false);
                                    handleDownload();
                                }}
                                disabled={loading}
                            >
                                📥 Download DOCX
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
