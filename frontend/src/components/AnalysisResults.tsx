'use client';

import { AnalysisResult } from '@/lib/api';
import { BarChart3, Briefcase, GraduationCap, Wrench, AlertTriangle, Lightbulb, User, Zap, TrendingUp } from 'lucide-react';
import ReconstructButton from './ReconstructButton';

interface AnalysisResultsProps {
    result: AnalysisResult;
    file: File | null;
    jobDescription: string;
    jobPosition: string;
    provider: string;
    model: string;
    sessionId?: string;
}

function extractPercentage(value: string): number {
    const match = value.match(/\d+/);
    return match ? parseInt(match[0], 10) : 0;
}

function getMatchColor(percentage: number): string {
    if (percentage >= 80) return 'var(--color-success)';
    if (percentage >= 60) return '#F59E0B';
    if (percentage >= 40) return '#F97316';
    return 'var(--color-error)';
}

function ScoreRing({ percentage, size = 120, strokeWidth = 8, label }: { percentage: number; size?: number; strokeWidth?: number; label: string }) {
    const radius = (size - strokeWidth) / 2;
    const circumference = 2 * Math.PI * radius;
    const offset = circumference - (percentage / 100) * circumference;
    const color = getMatchColor(percentage);

    return (
        <div className="score-ring" style={{ width: size, height: size }}>
            <svg width={size} height={size}>
                <circle
                    className="score-ring-track"
                    cx={size / 2}
                    cy={size / 2}
                    r={radius}
                    fill="none"
                    strokeWidth={strokeWidth}
                />
                <circle
                    className="score-ring-fill"
                    cx={size / 2}
                    cy={size / 2}
                    r={radius}
                    fill="none"
                    stroke={color}
                    strokeWidth={strokeWidth}
                    strokeLinecap="round"
                    strokeDasharray={circumference}
                    strokeDashoffset={offset}
                />
            </svg>
            <div className="score-ring-label">
                <span className="text-2xl font-bold" style={{ color }}>{percentage}%</span>
                <span className="text-[10px] font-medium text-[var(--color-text-secondary)] uppercase tracking-wider">{label}</span>
            </div>
        </div>
    );
}

function StatCard({ icon: Icon, label, value, percentage }: { icon: React.ElementType; label: string; value: string; percentage: number }) {
    const color = getMatchColor(percentage);
    return (
        <div className="stat-card">
            <div className="flex items-center justify-center mb-2">
                <Icon size={18} style={{ color }} />
            </div>
            <p className="text-xs text-[var(--color-text-secondary)] mb-1 font-medium">{label}</p>
            <p className="text-lg font-bold" style={{ color }}>{value}</p>
            <div className="progress-bar mt-3">
                <div
                    className="progress-bar-fill"
                    style={{ width: `${percentage}%`, backgroundColor: color }}
                ></div>
            </div>
        </div>
    );
}

export default function AnalysisResults({
    result,
    file,
    jobDescription,
    jobPosition,
    provider,
    model,
    sessionId
}: AnalysisResultsProps) {
    const matchPercentage = extractPercentage(result['JD Match']);
    const experienceMatch = extractPercentage(result.ExperienceMatch);
    const skillsMatch = extractPercentage(result.SkillsMatch);
    const educationMatch = extractPercentage(result.EducationMatch);

    return (
        <div className="card mb-6">
            {/* Header */}
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 sm:gap-0 mb-4 sm:mb-6">
                <div className="flex items-center gap-2">
                    <BarChart3 size={20} style={{ color: 'var(--color-primary)' }} />
                    <h3 className="text-lg font-bold">Analysis Results</h3>
                </div>
                <span className="text-xs font-medium text-[var(--color-text-secondary)] bg-[var(--color-background)] px-3 py-1.5 rounded-full border border-[var(--color-border)]">
                    {result.filename}
                </span>
            </div>

            {/* Overall Match — Score Ring */}
            <div className="flex items-center justify-center mb-5 sm:mb-8 py-2 sm:py-4">
                <ScoreRing percentage={matchPercentage} size={140} strokeWidth={10} label="JD Match" />
            </div>

            {/* Score Breakdown Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 sm:gap-4 mb-5 sm:mb-8">
                <StatCard icon={Briefcase} label="Experience" value={result.ExperienceMatch} percentage={experienceMatch} />
                <StatCard icon={Wrench} label="Skills" value={result.SkillsMatch} percentage={skillsMatch} />
                <StatCard icon={GraduationCap} label="Education" value={result.EducationMatch} percentage={educationMatch} />
            </div>

            {/* Missing Keywords & Strengths */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6 mb-4 sm:mb-6">
                <div className="glass-card">
                    <h4 className="font-semibold mb-3 flex items-center gap-2 text-sm">
                        <AlertTriangle size={16} style={{ color: 'var(--color-error)' }} />
                        Missing Keywords
                    </h4>
                    {result.MissingKeywords && result.MissingKeywords.length > 0 ? (
                        <div className="flex flex-wrap gap-2">
                            {result.MissingKeywords.map((keyword, idx) => (
                                <span key={idx} className="badge badge-error">{keyword}</span>
                            ))}
                        </div>
                    ) : (
                        <p className="text-sm flex items-center gap-1.5" style={{ color: 'var(--color-success)' }}>
                            <TrendingUp size={14} />
                            No critical keywords missing!
                        </p>
                    )}
                </div>

                <div className="glass-card">
                    <h4 className="font-semibold mb-3 flex items-center gap-2 text-sm">
                        <Zap size={16} style={{ color: 'var(--color-warning)' }} />
                        Key Strength
                    </h4>
                    <p className="text-sm text-[var(--color-text-secondary)] leading-relaxed">
                        {result.KeyStrength}
                    </p>
                </div>
            </div>

            {/* Recommendations */}
            <div className="glass-card mb-4 sm:mb-6">
                <h4 className="font-semibold mb-3 flex items-center gap-2 text-sm">
                    <Lightbulb size={16} style={{ color: 'var(--color-primary)' }} />
                    Recommendations
                </h4>
                <p className="text-sm text-[var(--color-text-secondary)] leading-relaxed">
                    {result.Recommendations}
                </p>
            </div>

            {/* Profile Summary */}
            <div className="alert alert-info">
                <User size={18} style={{ flexShrink: 0, marginTop: '2px' }} />
                <div>
                    <h4 className="font-semibold mb-1 text-sm">Profile Summary</h4>
                    <p className="text-sm leading-relaxed">{result['Profile Summary']}</p>
                </div>
            </div>

            {/* Reconstruct Button */}
            {file && (
                <ReconstructButton
                    file={file}
                    jobDescription={jobDescription}
                    jobPosition={jobPosition}
                    provider={provider}
                    model={model}
                    sessionId={sessionId}
                />
            )}
        </div>
    );
}
