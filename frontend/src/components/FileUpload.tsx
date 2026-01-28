'use client';

import { useRef, useState } from 'react';

interface FileUploadProps {
    onFileSelect: (file: File) => void;
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

    const getFileIcon = (filename: string) => {
        if (filename.endsWith('.pdf')) return '📄';
        if (filename.endsWith('.docx')) return '📝';
        return '📁';
    };

    return (
        <div className="mb-6">
            <label className="label">📂 Upload Resume</label>

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
                    <div className="flex flex-col items-center gap-2">
                        <span className="text-4xl">{getFileIcon(selectedFile.name)}</span>
                        <p className="font-medium text-[var(--color-text-primary)]">
                            {selectedFile.name}
                        </p>
                        <p className="text-sm text-[var(--color-text-secondary)]">
                            {(selectedFile.size / 1024).toFixed(1)} KB
                        </p>
                        <span className="badge badge-success">Ready to analyze</span>
                    </div>
                ) : (
                    <div className="flex flex-col items-center gap-2">
                        <span className="text-4xl">📤</span>
                        <p className="font-medium text-[var(--color-text-primary)]">
                            Drop your CV here or click to browse
                        </p>
                        <p className="text-sm text-[var(--color-text-secondary)]">
                            Supports PDF and DOCX files
                        </p>
                    </div>
                )}
            </div>
        </div>
    );
}
