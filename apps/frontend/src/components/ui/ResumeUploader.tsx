"use client";

import React, { useState, useRef } from 'react';
import { api } from '@/lib/api';

export const ResumeUploader: React.FC<{ onUploadSuccess: (data: any) => void }> = ({ onUploadSuccess }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setIsDragging(true);
    } else if (e.type === "dragleave") {
      setIsDragging(false);
    }
  };

  const processFile = async (file: File) => {
    if (!file.name.match(/\.(pdf|doc|docx)$/i)) {
      setError("Please upload a PDF or Microsoft Word document.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const result = await api.uploadResume(file);
      onUploadSuccess(result);
    } catch (err: any) {
      setError(err.message || "Failed to upload and parse resume.");
    } finally {
      setLoading(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      processFile(e.target.files[0]);
    }
  };

  return (
    <div className="w-full">
      <div 
        className={`relative border-2 border-dashed rounded-[var(--stitch-radius-lg)] p-10 text-center transition-all duration-300 ${
          isDragging 
            ? 'border-[var(--stitch-primary)] bg-[var(--stitch-primary)]/5' 
            : 'border-[var(--stitch-border)] hover:border-[var(--stitch-primary)]/50 bg-[var(--stitch-surface)]/50'
        } ${loading ? 'opacity-50 pointer-events-none' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input 
          ref={fileInputRef}
          type="file" 
          className="hidden" 
          accept=".pdf,.doc,.docx" 
          onChange={handleChange}
        />
        
        {loading ? (
          <div className="flex flex-col items-center">
            <div className="w-10 h-10 border-4 border-[var(--stitch-border)] border-t-[var(--stitch-primary)] rounded-full animate-spin mb-4"></div>
            <p className="text-[var(--stitch-typography-primary)] font-medium">Analyzing resume...</p>
            <p className="text-sm text-[var(--stitch-typography-secondary)] mt-1">Extracting skills and experience</p>
          </div>
        ) : (
          <div className="flex flex-col items-center">
            <div className="w-16 h-16 mb-4 rounded-full bg-[var(--stitch-surface-hover)] flex items-center justify-center text-[var(--stitch-typography-secondary)]">
              <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <p className="text-lg font-medium text-[var(--stitch-typography-primary)] mb-1">
              Drag & Drop your resume
            </p>
            <p className="text-sm text-[var(--stitch-typography-secondary)] mb-6">
              PDF, DOC, or DOCX (Max 5MB)
            </p>
            <button 
              onClick={() => fileInputRef.current?.click()}
              className="px-6 py-2.5 rounded-[var(--stitch-radius-md)] bg-[var(--stitch-primary)] text-white font-medium hover:brightness-110 transition-all shadow-[var(--stitch-shadow-md)]"
            >
              Browse Files
            </button>
          </div>
        )}
      </div>

      {error && (
        <div className="mt-4 p-3 rounded-[var(--stitch-radius-md)] bg-[var(--stitch-error)]/10 border border-[var(--stitch-error)]/20 text-[var(--stitch-error)] text-sm flex items-start gap-2">
          <svg className="w-5 h-5 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p>{error}</p>
        </div>
      )}
    </div>
  );
};
