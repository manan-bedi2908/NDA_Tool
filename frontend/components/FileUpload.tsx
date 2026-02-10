import React, { useCallback, useState } from 'react';
import { CloudUpload, File as FileIcon, X, CheckCircle2 } from 'lucide-react';

interface FileUploadProps {
    label: string;
    subLabel?: string;
    accept?: string;
    onFileSelect: (file: File | null) => void;
    className?: string;
}

const FileUpload: React.FC<FileUploadProps> = ({
    label,
    subLabel = "Limit 200MB per file • PDF",
    accept = ".pdf,.docx",
    onFileSelect,
    className = "",
}) => {
    const [dragActive, setDragActive] = useState(false);
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const inputRef = React.useRef<HTMLInputElement>(null);

    const handleDrag = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === "dragenter" || e.type === "dragover") {
            setDragActive(true);
        } else if (e.type === "dragleave") {
            setDragActive(false);
        }
    }, []);

    const handleDrop = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleFile(e.dataTransfer.files[0]);
        }
    }, []);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        e.preventDefault();
        if (e.target.files && e.target.files[0]) {
            handleFile(e.target.files[0]);
        }
    };

    const handleFile = (file: File) => {
        // Simulate loading/validation
        setIsLoading(true);
        setTimeout(() => {
            setSelectedFile(file);
            onFileSelect(file);
            setIsLoading(false);
        }, 800);
    };

    const removeFile = (e: React.MouseEvent) => {
        e.stopPropagation();
        setSelectedFile(null);
        onFileSelect(null);
        if (inputRef.current) {
            inputRef.current.value = '';
        }
    };

    const onButtonClick = () => {
        inputRef.current?.click();
    };

    return (
        <div className={`w-full ${className}`}>
            <label className="block text-sm font-semibold text-foreground mb-2">
                {label}
            </label>

            <div
                className={`relative flex items-center justify-between p-5 rounded-xl border-2 border-dashed transition-all duration-300 cursor-pointer ${dragActive
                    ? "border-primary bg-primary-light"
                    : "border-border bg-muted hover:border"
                    } ${selectedFile ? "border-solid border-success/30 bg-success-light" : ""}`}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
            >
                <input
                    ref={inputRef}
                    type="file"
                    className="hidden"
                    accept={accept}
                    onChange={handleChange}
                />

                {isLoading ? (
                    <div className="flex-1 flex items-center justify-center py-2">
                        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
                        <span className="ml-3 text-sm text-secondary-text font-medium">Validating document...</span>
                    </div>
                ) : selectedFile ? (
                    <div className="flex-1 flex items-center gap-4 overflow-hidden">
                        <div className="p-2.5 bg-surface rounded-lg shadow-sm border border-success/20">
                            <CheckCircle2 size={22} className="text-success" />
                        </div>
                        <div className="flex-1 min-w-0">
                            <p className="text-sm font-bold text-foreground truncate">
                                {selectedFile.name}
                            </p>
                            <p className="text-xs text-secondary-text font-medium">
                                {(selectedFile.size / 1024 / 1024).toFixed(2)} MB • Ready
                            </p>
                        </div>
                        <button
                            onClick={removeFile}
                            className="p-1.5 hover:bg-surface rounded-full transition-colors text-muted-text hover:text-error hover:shadow-sm"
                        >
                            <X size={18} />
                        </button>
                    </div>
                ) : (
                    <>
                        <div className="flex items-center gap-4">
                            <div className="p-3 bg-surface rounded-xl shadow-sm border border-light">
                                <CloudUpload size={24} className="text-primary" />
                            </div>
                            <div>
                                <p className="text-sm text-foreground font-bold">
                                    Click or drag to upload
                                </p>
                                <p className="text-xs text-secondary-text font-medium mt-0.5">{subLabel}</p>
                            </div>
                        </div>
                        <button
                            type="button"
                            onClick={onButtonClick}
                            className="px-4 py-2 text-xs font-bold bg-surface border border-light hover:border-primary hover:text-primary text-foreground rounded-lg transition-all shadow-sm hover:shadow-md"
                        >
                            Browse
                        </button>
                    </>
                )}
            </div>
        </div>
    );
};

export default FileUpload;
