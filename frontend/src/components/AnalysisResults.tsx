'use client';

import { AnalysisResult } from '@/lib/api';
import ReconstructButton from './ReconstructButton';

interface AnalysisResultsProps {
    result: AnalysisResult;
    file: File | null;
    jobDescription: string;
    jobPosition: string;
    provider: string;
    model: string;
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

function getMatchEmoji(percentage: number): string {
    if (percentage >= 80) return '🟢';
    if (percentage >= 60) return '🟡';
    if (percentage >= 40) return '🟠';
    return '🔴';
}

export default function AnalysisResults({
    result,
    file,
    jobDescription,
    jobPosition,
    provider,
    model
}: AnalysisResultsProps) {
    const matchPercentage = extractPercentage(result['JD Match']);
    const experienceMatch = extractPercentage(result.ExperienceMatch);
    const skillsMatch = extractPercentage(result.SkillsMatch);
    const educationMatch = extractPercentage(result.EducationMatch);

    return (
        <div className="card mb-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                📊 Analysis Results
                <span className="text-sm font-normal text-[var(--color-text-secondary)]">
                    for {result.filename}
                </span>
            </h3>

            {/* Overall Match */}
            <div className="mb-6">
                <div className="flex items-center justify-between mb-2">
                    <span className="text-2xl font-bold flex items-center gap-2">
                        {getMatchEmoji(matchPercentage)} JD Match: {result['JD Match']}
                    </span>
                </div>
                <div className="progress-bar">
                    <div
                        className="progress-bar-fill"
                        style={{
                            width: `${matchPercentage}%`,
                            backgroundColor: getMatchColor(matchPercentage)
                        }}
                    ></div>
                </div>
            </div>

            {/* Score Breakdown */}
            <div className="grid grid-cols-3 gap-4 mb-6">
                <div className="text-center p-4 bg-[var(--color-background)] rounded-lg border border-[var(--color-border)]">
                    <p className="text-sm text-[var(--color-text-secondary)] mb-1">📊 Experience</p>
                    <p className="text-xl font-bold" style={{ color: getMatchColor(experienceMatch) }}>
                        {result.ExperienceMatch}
                    </p>
                    <div className="progress-bar mt-2">
                        <div
                            className="progress-bar-fill"
                            style={{ width: `${experienceMatch}%`, backgroundColor: getMatchColor(experienceMatch) }}
                        ></div>
                    </div>
                </div>

                <div className="text-center p-4 bg-[var(--color-background)] rounded-lg border border-[var(--color-border)]">
                    <p className="text-sm text-[var(--color-text-secondary)] mb-1">🛠️ Skills</p>
                    <p className="text-xl font-bold" style={{ color: getMatchColor(skillsMatch) }}>
                        {result.SkillsMatch}
                    </p>
                    <div className="progress-bar mt-2">
                        <div
                            className="progress-bar-fill"
                            style={{ width: `${skillsMatch}%`, backgroundColor: getMatchColor(skillsMatch) }}
                        ></div>
                    </div>
                </div>

                <div className="text-center p-4 bg-[var(--color-background)] rounded-lg border border-[var(--color-border)]">
                    <p className="text-sm text-[var(--color-text-secondary)] mb-1">🎓 Education</p>
                    <p className="text-xl font-bold" style={{ color: getMatchColor(educationMatch) }}>
                        {result.EducationMatch}
                    </p>
                    <div className="progress-bar mt-2">
                        <div
                            className="progress-bar-fill"
                            style={{ width: `${educationMatch}%`, backgroundColor: getMatchColor(educationMatch) }}
                        ></div>
                    </div>
                </div>
            </div>

            {/* Missing Keywords */}
            <div className="grid grid-cols-2 gap-6 mb-6">
                <div>
                    <h4 className="font-semibold mb-2 flex items-center gap-1">
                        🔴 Missing Keywords
                    </h4>
                    {result.MissingKeywords && result.MissingKeywords.length > 0 ? (
                        <div className="flex flex-wrap gap-2">
                            {result.MissingKeywords.map((keyword, idx) => (
                                <span key={idx} className="badge badge-error">
                                    {keyword}
                                </span>
                            ))}
                        </div>
                    ) : (
                        <p className="text-sm text-[var(--color-success)]">
                            ✅ No critical keywords missing!
                        </p>
                    )}
                </div>

                <div>
                    <h4 className="font-semibold mb-2 flex items-center gap-1">
                        💪 Key Strength
                    </h4>
                    <p className="text-sm text-[var(--color-text-secondary)]">
                        {result.KeyStrength}
                    </p>
                </div>
            </div>

            {/* Recommendations */}
            <div className="mb-6">
                <h4 className="font-semibold mb-2 flex items-center gap-1">
                    💡 Recommendations
                </h4>
                <p className="text-sm text-[var(--color-text-secondary)]">
                    {result.Recommendations}
                </p>
            </div>

            {/* Profile Summary */}
            <div className="alert alert-info">
                <h4 className="font-semibold mb-1">📝 Profile Summary</h4>
                <p className="text-sm">{result['Profile Summary']}</p>
            </div>

            {/* Reconstruct Button */}
            {file && (
                <ReconstructButton
                    file={file}
                    jobDescription={jobDescription}
                    jobPosition={jobPosition}
                    provider={provider}
                    model={model}
                />
            )}
        </div>
    );
}
