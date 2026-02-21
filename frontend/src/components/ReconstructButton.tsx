'use client';

import { useState } from 'react';
import { Eye, Download, FileText, X, CheckCircle2, AlertTriangle, Wrench, BarChart3, Users, FolderKanban, Target } from 'lucide-react';
import { reconstructResume, downloadBlob, previewReconstruction, ReconstructionPreview, generatePDFResume } from '@/lib/api';

interface ReconstructButtonProps {
    file: File;
    jobDescription: string;
    jobPosition: string;
    provider: string;
    model: string;
    sessionId?: string;
}

export default function ReconstructButton({
    file,
    jobDescription,
    jobPosition,
    provider,
    model,
    sessionId
}: ReconstructButtonProps) {
    const [loading, setLoading] = useState(false);
    const [pdfLoading, setPdfLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [showPreview, setShowPreview] = useState(false);
    const [preview, setPreview] = useState<ReconstructionPreview | null>(null);

    const handlePreview = async () => {
        setLoading(true);
        setError(null);
        try {
            const result = await previewReconstruction(file, jobDescription, jobPosition, provider, model, sessionId);
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
            const blob = await reconstructResume(file, jobDescription, jobPosition, provider, model, sessionId);
            const originalName = file.name.replace(/\.[^/.]+$/, '');
            downloadBlob(blob, `${originalName}_reconstructed.docx`);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Download failed');
        } finally {
            setLoading(false);
        }
    };

    const handlePDFDownload = async () => {
        setPdfLoading(true);
        setError(null);
        try {
            const blob = await generatePDFResume(file, jobDescription, jobPosition, provider, model, sessionId);
            const originalName = file.name.replace(/\.[^/.]+$/, '');
            downloadBlob(blob, `${originalName}_upgraded.pdf`);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'PDF generation failed');
        } finally {
            setPdfLoading(false);
        }
    };

    return (
        <div className="mt-5 sm:mt-8 pt-4 sm:pt-6 border-t border-[var(--color-border)]">
            <div className="flex items-center gap-2 mb-2">
                <Wrench size={18} style={{ color: 'var(--color-primary)' }} />
                <h4 className="font-bold text-sm">Resume Reconstruction</h4>
            </div>
            <p className="text-xs text-[var(--color-text-secondary)] mb-3 sm:mb-5 leading-relaxed">
                Optimize your resume for this job description. Uses only your existing information — no AI hallucination.
            </p>

            <div className="flex flex-col sm:flex-row gap-2 sm:gap-3">
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
                        <>
                            <Eye size={16} />
                            Preview
                        </>
                    )}
                </button>

                <button
                    className="btn btn-primary flex-1"
                    onClick={handleDownload}
                    disabled={loading}
                >
                    {loading && showPreview ? (
                        <>
                            <div className="spinner" style={{ borderTopColor: 'white', borderColor: 'rgba(255,255,255,0.3)' }}></div>
                            Generating...
                        </>
                    ) : (
                        <>
                            <Download size={16} />
                            DOCX
                        </>
                    )}
                </button>

                <button
                    className="btn btn-primary flex-1"
                    onClick={handlePDFDownload}
                    disabled={loading || pdfLoading}
                    title="Generate JD-tailored PDF resume"
                >
                    {pdfLoading ? (
                        <>
                            <div className="spinner" style={{ borderTopColor: 'white', borderColor: 'rgba(255,255,255,0.3)' }}></div>
                            PDF...
                        </>
                    ) : (
                        <>
                            <FileText size={16} />
                            PDF
                        </>
                    )}
                </button>
            </div>

            {error && (
                <div className="alert alert-error mt-4 animate-in">
                    <AlertTriangle size={16} style={{ flexShrink: 0 }} />
                    <span>{error}</span>
                </div>
            )}

            {/* Preview Modal */}
            {showPreview && preview && (
                <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-2 sm:p-4">
                    <div
                        className="rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col"
                        style={{
                            backgroundColor: 'var(--color-card)',
                            border: '1px solid var(--color-border)',
                            boxShadow: 'var(--shadow-lg)',
                        }}
                    >
                        {/* Header */}
                        <div className="flex justify-between items-center px-3 sm:px-6 py-3 sm:py-4 border-b border-[var(--color-border)]">
                            <div className="flex items-center gap-2">
                                <FileText size={20} style={{ color: 'var(--color-primary)' }} />
                                <h3 className="text-sm sm:text-base font-bold">Reconstructed Resume Preview</h3>
                            </div>
                            <button
                                onClick={() => setShowPreview(false)}
                                className="p-1.5 rounded-lg hover:bg-[var(--color-surface)] transition-colors"
                            >
                                <X size={18} />
                            </button>
                        </div>

                        {/* Content */}
                        <div className="flex-1 overflow-y-auto px-3 sm:px-6 py-3 sm:py-5">
                            {/* Summary Stats */}
                            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 sm:gap-3 mb-3 sm:mb-5">
                                <div className="stat-card">
                                    <Wrench size={16} style={{ color: 'var(--color-primary)', margin: '0 auto 6px' }} />
                                    <p className="text-[10px] text-[var(--color-text-secondary)] uppercase tracking-wider">Skills</p>
                                    <p className="text-xl font-bold mt-0.5">{preview.parsed_resume_summary.skills_count}</p>
                                </div>
                                <div className="stat-card">
                                    <Users size={16} style={{ color: 'var(--color-primary)', margin: '0 auto 6px' }} />
                                    <p className="text-[10px] text-[var(--color-text-secondary)] uppercase tracking-wider">Experience</p>
                                    <p className="text-xl font-bold mt-0.5">{preview.parsed_resume_summary.experience_count}</p>
                                </div>
                                <div className="stat-card">
                                    <FolderKanban size={16} style={{ color: 'var(--color-primary)', margin: '0 auto 6px' }} />
                                    <p className="text-[10px] text-[var(--color-text-secondary)] uppercase tracking-wider">Projects</p>
                                    <p className="text-xl font-bold mt-0.5">{preview.parsed_resume_summary.projects_count}</p>
                                </div>
                                <div className="stat-card">
                                    <Target size={16} style={{ color: 'var(--color-success)', margin: '0 auto 6px' }} />
                                    <p className="text-[10px] text-[var(--color-text-secondary)] uppercase tracking-wider">Matched</p>
                                    <p className="text-xl font-bold mt-0.5" style={{ color: 'var(--color-success)' }}>
                                        {preview.gap_analysis.matched_skills.length}
                                    </p>
                                </div>
                            </div>

                            {/* Matched Skills */}
                            {preview.gap_analysis.matched_skills.length > 0 && (
                                <div className="mb-5">
                                    <p className="text-xs font-semibold mb-2 flex items-center gap-1.5">
                                        <CheckCircle2 size={14} style={{ color: 'var(--color-success)' }} />
                                        JD-Matched Skills
                                    </p>
                                    <div className="flex flex-wrap gap-2">
                                        {preview.gap_analysis.matched_skills.slice(0, 10).map((skill, idx) => (
                                            <span key={idx} className="badge badge-success">{skill}</span>
                                        ))}
                                        {preview.gap_analysis.matched_skills.length > 10 && (
                                            <span className="badge" style={{ background: 'var(--color-surface)', color: 'var(--color-text-secondary)' }}>
                                                +{preview.gap_analysis.matched_skills.length - 10} more
                                            </span>
                                        )}
                                    </div>
                                </div>
                            )}

                            {/* Validation Warnings */}
                            {preview.validation.warnings.length > 0 && (
                                <div className="alert alert-warning mb-5">
                                    <AlertTriangle size={16} style={{ flexShrink: 0, marginTop: '2px' }} />
                                    <div>
                                        <p className="font-semibold mb-1 text-sm">Validation Warnings</p>
                                        <ul className="list-disc list-inside text-sm space-y-0.5">
                                            {preview.validation.warnings.map((warn, idx) => (
                                                <li key={idx}>{warn}</li>
                                            ))}
                                        </ul>
                                    </div>
                                </div>
                            )}

                            {/* Resume Preview */}
                            <div
                                className="p-6 rounded-xl border font-mono text-sm whitespace-pre-wrap leading-relaxed"
                                style={{
                                    backgroundColor: 'var(--color-background)',
                                    borderColor: 'var(--color-border)',
                                    color: 'var(--color-text-primary)',
                                }}
                            >
                                {preview.reconstructed_text}
                            </div>
                        </div>

                        {/* Footer */}
                        <div className="px-3 sm:px-6 py-3 sm:py-4 border-t border-[var(--color-border)] flex flex-col sm:flex-row gap-2 sm:gap-3">
                            <button
                                className="btn btn-secondary flex-1"
                                onClick={() => setShowPreview(false)}
                            >
                                <X size={16} />
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
                                <Download size={16} />
                                Download DOCX
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
