'use client';

import { useRef, useState } from 'react';
import { Upload, FileCheck, File, X } from 'lucide-react';

interface FileUploadProps {
    onFileSelect: (file: File | null) => void;
    selectedFile: File | null;
    accept?: string;
}

export default function FileUpload({ onFileSelect, selectedFile, accept = ".pdf,.docx" }: FileUploadProps) {
    const [isDragging, setIsDragging] = useState(false);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleDragOver = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            onFileSelect(files[0]);
        }
    };

    const handleClick = () => {
        fileInputRef.current?.click();
    };

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const files = e.target.files;
        if (files && files.length > 0) {
            onFileSelect(files[0]);
        }
    };

    const handleRemove = (e: React.MouseEvent) => {
        e.stopPropagation();
        onFileSelect(null);
        if (fileInputRef.current) fileInputRef.current.value = '';
    };

    return (
        <div className="mb-6">
            <label className="label">
                <Upload size={14} />
                Upload Resume
            </label>

            <div
                className={`file-upload ${isDragging ? 'active' : ''}`}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                onClick={handleClick}
            >
                <input
                    ref={fileInputRef}
                    type="file"
                    accept={accept}
                    onChange={handleFileChange}
                    className="hidden"
                />

                {selectedFile ? (
                    <div className="flex flex-col items-center gap-3 relative" style={{ zIndex: 1 }}>
                        <div
                            className="w-14 h-14 rounded-2xl flex items-center justify-center"
                            style={{ background: 'var(--color-success-bg)' }}
                        >
                            <FileCheck size={28} style={{ color: 'var(--color-success)' }} />
                        </div>
                        <div className="text-center">
                            <p className="font-semibold text-[var(--color-text-primary)] text-sm">
                                {selectedFile.name}
                            </p>
                            <p className="text-xs text-[var(--color-text-secondary)] mt-1">
                                {(selectedFile.size / 1024).toFixed(1)} KB
                            </p>
                        </div>
                        <div className="flex items-center gap-2">
                            <span className="badge badge-success">Ready to analyze</span>
                            <button
                                onClick={handleRemove}
                                className="p-1 rounded-full hover:bg-[var(--color-error-bg)] transition-colors"
                                title="Remove file"
                            >
                                <X size={14} style={{ color: 'var(--color-error)' }} />
                            </button>
                        </div>
                    </div>
                ) : (
                    <div className="flex flex-col items-center gap-3" style={{ zIndex: 1, position: 'relative' }}>
                        <div
                            className="w-14 h-14 rounded-2xl flex items-center justify-center"
                            style={{ background: 'var(--color-primary-glow)' }}
                        >
                            <Upload size={28} style={{ color: 'var(--color-primary)' }} />
                        </div>
                        <div className="text-center">
                            <p className="font-semibold text-[var(--color-text-primary)] text-sm">
                                Drop your resume here or{' '}
                                <span style={{ color: 'var(--color-primary)' }}>browse</span>
                            </p>
                            <p className="text-xs text-[var(--color-text-secondary)] mt-1">
                                Supports PDF and DOCX &middot; Max 10MB
                            </p>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
