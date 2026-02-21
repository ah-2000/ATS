'use client';

import { useState } from 'react';
import { Search, AlertCircle, Sparkles, BriefcaseBusiness, FileText, ChevronRight } from 'lucide-react';
import Sidebar from '@/components/Sidebar';
import FileUpload from '@/components/FileUpload';
import AnalysisResults from '@/components/AnalysisResults';
import { AnalysisResult, analyzeCV } from '@/lib/api';

const JOB_POSITIONS = [
  "Software Engineer",
  "Data Analyst",
  "Data Engineer",
  "Machine Learning Engineer",
  "Full Stack Developer (MERN)",
  "Full Stack Developer (MEAN)",
  "Frontend Developer",
  "Backend Developer",
  "DevOps Engineer",
  "Cloud Solutions Architect",
  "Artificial Intelligence Engineer",
  "Deep Learning Engineer",
  "Computer Vision Engineer",
  "Big Data Engineer",
  "Network Engineer",
  "Cybersecurity Engineer",
  "IT Support Specialist",
  "Technical Support Specialist",
  "Cybersecurity Analyst",
  "Ethical Hacker/Penetration Tester",
  "Mobile App Developer",
  "Blockchain Developer",
  "Data Scientist",
  "UI/UX Designer",
  "Customer Support",
  "Business Development Manager",
  "Marketing Specialist",
  "Sales Representative",
  "Graphic Designer",
  "Product Manager",
  "Project Manager",
  "Content Writer",
  "Financial Analyst",
  "Human Resources Manager",
  "Other (Custom)",
];

export default function Home() {
  const [selectedProvider, setSelectedProvider] = useState('');
  const [selectedModel, setSelectedModel] = useState('');
  const [selectedPosition, setSelectedPosition] = useState(JOB_POSITIONS[0]);
  const [customPosition, setCustomPosition] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [sessionId, setSessionId] = useState<string | undefined>(undefined);

  const jobPosition = selectedPosition === "Other (Custom)" ? customPosition : selectedPosition;

  const handleAnalyze = async () => {
    if (!selectedFile || !jobDescription.trim() || !jobPosition.trim()) {
      setError('Please fill in all required fields');
      return;
    }
    setLoading(true);
    setError(null);
    setAnalysisResult(null);
    setSessionId(undefined);
    try {
      const result = await analyzeCV(selectedFile, jobDescription, jobPosition, selectedProvider, selectedModel);
      setAnalysisResult(result.analysis);
      setSessionId(result.session_id);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed');
    } finally {
      setLoading(false);
    }
  };

  // Steps indicator
  const steps = [
    { label: 'Job Details', done: !!jobDescription.trim() && !!jobPosition.trim() },
    { label: 'Upload CV', done: !!selectedFile },
    { label: 'Analyze', done: !!analysisResult },
  ];

  return (
    <div className="app-layout">
      <Sidebar
        selectedProvider={selectedProvider}
        selectedModel={selectedModel}
        onProviderChange={setSelectedProvider}
        onModelChange={setSelectedModel}
      />

      <main className="main-content">
        {/* Header */}
        <div className="mb-6 sm:mb-8 md:mb-10 animate-in">
          <div className="flex items-center gap-2 sm:gap-3 mb-2 sm:mb-3">
            <div className="p-2.5 rounded-xl" style={{ background: 'var(--color-primary-glow)' }}>
              <Sparkles size={24} style={{ color: 'var(--color-primary)' }} />
            </div>
            <div>
              <h1 className="text-2xl font-bold">Smart ATS System</h1>
              <p className="text-sm text-[var(--color-text-secondary)]">
                AI-powered resume analysis &amp; optimization
              </p>
            </div>
          </div>

          {/* Steps Progress */}
          <div className="flex items-center gap-1.5 sm:gap-2 mt-4 sm:mt-6 flex-wrap">
            {steps.map((step, i) => (
              <div key={i} className="flex items-center gap-2">
                <div className="flex items-center gap-2">
                  <div
                    className="w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold transition-all duration-300"
                    style={{
                      background: step.done ? 'var(--color-primary)' : 'var(--color-border)',
                      color: step.done ? 'white' : 'var(--color-text-secondary)',
                    }}
                  >
                    {step.done ? '✓' : i + 1}
                  </div>
                  <span
                    className="text-xs font-medium transition-colors duration-300"
                    style={{ color: step.done ? 'var(--color-primary)' : 'var(--color-text-secondary)' }}
                  >
                    {step.label}
                  </span>
                </div>
                {i < steps.length - 1 && (
                  <ChevronRight size={14} className="text-[var(--color-border)] mx-1" />
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Step 1: Job Details */}
        <div className="card mb-4 sm:mb-6 animate-in animate-in-delay-1">
          <div className="flex items-center gap-2 mb-3 sm:mb-5">
            <BriefcaseBusiness size={18} style={{ color: 'var(--color-primary)' }} />
            <h3 className="text-base font-semibold">Job Details</h3>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4 mb-3 sm:mb-5">
            <div>
              <label className="label">
                <BriefcaseBusiness size={14} />
                Job Position
              </label>
              <select
                className="select"
                value={selectedPosition}
                onChange={(e) => setSelectedPosition(e.target.value)}
              >
                {JOB_POSITIONS.map(position => (
                  <option key={position} value={position}>{position}</option>
                ))}
              </select>
            </div>

            {selectedPosition === "Other (Custom)" && (
              <div>
                <label className="label">Custom Position</label>
                <input
                  type="text"
                  className="input"
                  placeholder="e.g., QA Engineer"
                  value={customPosition}
                  onChange={(e) => setCustomPosition(e.target.value)}
                />
              </div>
            )}
          </div>

          <div>
            <label className="label">
              <FileText size={14} />
              Job Description
            </label>
            <textarea
              className="textarea"
              placeholder="Paste the full job description here for the best analysis..."
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
            />
          </div>
        </div>

        {/* Step 2: File Upload */}
        <div className="animate-in animate-in-delay-2">
          <FileUpload onFileSelect={setSelectedFile} selectedFile={selectedFile} />
        </div>

        {/* Analyze Button */}
        <div className="animate-in animate-in-delay-3">
          <button
            className="btn btn-primary w-full mb-4 sm:mb-6"
            style={{ padding: 'clamp(0.75rem, 2vw, 1rem)', fontSize: 'clamp(0.8rem, 1.5vw, 0.9375rem)' }}
            onClick={handleAnalyze}
            disabled={loading || !selectedFile || !jobDescription.trim() || !selectedProvider}
          >
            {loading ? (
              <>
                <div className="spinner" style={{ borderTopColor: 'white', borderColor: 'rgba(255,255,255,0.3)' }}></div>
                Analyzing your resume...
              </>
            ) : (
              <>
                <Search size={18} />
                Analyze Resume
              </>
            )}
          </button>
        </div>

        {/* Error */}
        {error && (
          <div className="alert alert-error mb-6 animate-in">
            <AlertCircle size={18} style={{ flexShrink: 0, marginTop: '1px' }} />
            <span>{error}</span>
          </div>
        )}

        {/* Results */}
        {analysisResult && (
          <div className="animate-in">
            <AnalysisResults
              result={analysisResult}
              file={selectedFile}
              jobDescription={jobDescription}
              jobPosition={jobPosition}
              provider={selectedProvider}
              model={selectedModel}
              sessionId={sessionId}
            />
          </div>
        )}

        {/* Footer */}
        <div className="text-center text-xs text-[var(--color-text-secondary)] mt-6 sm:mt-8 md:mt-10 pt-4 sm:pt-5 border-t border-[var(--color-border)]">
          <span style={{ color: 'var(--color-primary)', fontWeight: 600 }}>Smart ATS</span>
          {' '}&middot; Powered by {selectedProvider || 'AI'}
          {selectedModel && <span className="opacity-70"> ({selectedModel})</span>}
        </div>
      </main>
    </div>
  );
}
