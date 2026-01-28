'use client';

import { useState } from 'react';
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
  // Model selection state
  const [selectedProvider, setSelectedProvider] = useState('');
  const [selectedModel, setSelectedModel] = useState('');

  // Form state
  const [selectedPosition, setSelectedPosition] = useState(JOB_POSITIONS[0]);
  const [customPosition, setCustomPosition] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  // Analysis state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);

  const jobPosition = selectedPosition === "Other (Custom)" ? customPosition : selectedPosition;

  const handleAnalyze = async () => {
    if (!selectedFile || !jobDescription.trim() || !jobPosition.trim()) {
      setError('Please fill in all required fields');
      return;
    }

    setLoading(true);
    setError(null);
    setAnalysisResult(null);

    try {
      const result = await analyzeCV(
        selectedFile,
        jobDescription,
        jobPosition,
        selectedProvider,
        selectedModel
      );
      setAnalysisResult(result.analysis);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-layout">
      <Sidebar
        selectedProvider={selectedProvider}
        selectedModel={selectedModel}
        onProviderChange={setSelectedProvider}
        onModelChange={setSelectedModel}
      />

      <main className="main-content">
        <div className="mb-8">
          <h1 className="text-2xl font-bold mb-2">Smart ATS System</h1>
          <p className="text-[var(--color-text-secondary)]">
            Analyze your resume against job descriptions with AI-powered insights
          </p>
        </div>

        {/* Job Position Selection */}
        <div className="card mb-6">
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div>
              <label className="label">Job Position</label>
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
            <label className="label">Job Description</label>
            <textarea
              className="textarea"
              placeholder="Paste the job description here..."
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
            />
          </div>
        </div>

        {/* File Upload */}
        <FileUpload
          onFileSelect={setSelectedFile}
          selectedFile={selectedFile}
        />

        {/* Analyze Button */}
        <button
          className="btn btn-primary w-full mb-6"
          onClick={handleAnalyze}
          disabled={loading || !selectedFile || !jobDescription.trim() || !selectedProvider}
        >
          {loading ? (
            <>
              <div className="spinner"></div>
              Analyzing...
            </>
          ) : (
            <>
              🔍 Analyze Resume
            </>
          )}
        </button>

        {/* Error Display */}
        {error && (
          <div className="alert alert-error mb-6">
            ❌ {error}
          </div>
        )}

        {/* Analysis Results */}
        {analysisResult && (
          <AnalysisResults
            result={analysisResult}
            file={selectedFile}
            jobDescription={jobDescription}
            jobPosition={jobPosition}
            provider={selectedProvider}
            model={selectedModel}
          />
        )}

        {/* Footer */}
        <div className="text-center text-sm text-[var(--color-text-secondary)] mt-8 pt-6 border-t border-[var(--color-border)]">
          💼 Smart ATS System | Powered by {selectedProvider || 'AI'} {selectedModel && `(${selectedModel})`}
        </div>
      </main>
    </div>
  );
}
