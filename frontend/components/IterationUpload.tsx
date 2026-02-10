import React, { useState } from 'react';
import { BookOpen, ChevronRight, Plus, File as FileIcon, CheckCircle2 } from 'lucide-react';
import FileUpload from './FileUpload';

interface IterationUploadProps {
    onUpload: (docA: File, docB: File) => Promise<void>;
    isUploading: boolean;
    uploadStatus: { type: 'success' | 'error' | 'info'; message: string } | null;
    showUpload: boolean;
    setShowUpload: (show: boolean) => void;
}

const IterationUpload: React.FC<IterationUploadProps> = ({
    onUpload,
    isUploading,
    uploadStatus,
    showUpload,
    setShowUpload
}) => {
    const [docA, setDocA] = useState<File | null>(null);
    const [docB, setDocB] = useState<File | null>(null);

    const handleUploadClick = () => {
        if (docA && docB) {
            onUpload(docA, docB);
        }
    };

    return (
        <div className="space-y-6 pt-6">
            <div className="flex items-center gap-3 text-xl font-semibold text-foreground">
                <BookOpen size={24} className="text-primary" strokeWidth={2.5} />
                <h3>Create New Iteration</h3>
            </div>

            <div className="bg-surface rounded-2xl border border-light shadow-md overflow-hidden">
                {/* Accordion Header */}
                <button
                    onClick={() => setShowUpload(!showUpload)}
                    className={`w-full text-left px-8 py-5 flex items-center justify-between transition-all duration-300 ${showUpload ? 'bg-primary-light/30 border-b border-light' : 'hover:bg-surface-hover'}`}
                >
                    <div className="flex items-center gap-4">
                        <div className={`p-2 rounded-lg transition-colors ${showUpload ? 'bg-primary text-white shadow-sm' : 'bg-muted text-muted-text'}`}>
                            <Plus size={18} strokeWidth={3} />
                        </div>
                        <span className="text-base font-semibold text-foreground">Add New Negotiation Iteration</span>
                    </div>
                    <ChevronRight className={`transition-transform duration-300 text-muted-text ${showUpload ? 'rotate-90' : ''}`} size={20} />
                </button>

                {/* Upload Area */}
                {showUpload && (
                    <div className="p-8 space-y-8 animate-in fade-in slide-in-from-top-2 duration-300">
                        <div className="space-y-2">
                            <h4 className="text-sm font-bold text-foreground">Upload Documentation</h4>
                            <p className="text-sm text-secondary-text font-medium">
                                Upload documents to create a new iteration for this project
                            </p>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                            <FileUpload
                                label="Document A (Standard NDA)"
                                onFileSelect={setDocA}
                            />
                            <FileUpload
                                label="Document B (Client NDA)"
                                onFileSelect={setDocB}
                            />
                        </div>

                        <button
                            onClick={handleUploadClick}
                            disabled={!docA || !docB || isUploading}
                            className={`w-full py-4 rounded-xl flex items-center justify-center gap-3 font-bold text-base transition-all ${docA && docB && !isUploading
                                ? "bg-primary hover:bg-primary-hover text-white shadow-lg shadow-primary/20 hover:shadow-xl hover:shadow-primary/30 translate-y-0 active:translate-y-0.5"
                                : "bg-border-light text-muted-text cursor-not-allowed"
                                }`}
                        >
                            {isUploading ? (
                                <>
                                    <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                    <span>Analyzing Clauses...</span>
                                </>
                            ) : (
                                <>
                                    <FileIcon size={20} />
                                    <span>Create iteration and analyze</span>
                                </>
                            )}
                        </button>

                        {uploadStatus && (
                            <div className={`p-5 rounded-xl flex items-center gap-3 text-sm font-bold animate-in zoom-in-95 duration-200 ${uploadStatus.type === 'success' ? 'bg-success-light text-success border border-success/20' :
                                uploadStatus.type === 'error' ? 'bg-error-light text-error border border-error/20' :
                                    'bg-info-light text-info border border-info/20'
                                }`}>
                                {uploadStatus.type === 'success' && <CheckCircle2 size={20} />}
                                {uploadStatus.message}
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
};

export default IterationUpload;
