import React from 'react';
import { FileText, BarChart, Download } from 'lucide-react';

interface ActionButtonsProps {
    handleGenerateRedline: () => void;
    handleExportSummary: () => void;
    handleDownloadIterationInfo: () => void;
}

const ActionButtons: React.FC<ActionButtonsProps> = ({
    handleGenerateRedline,
    handleExportSummary,
    handleDownloadIterationInfo
}) => {
    return (
        <div className="flex flex-col md:flex-row items-center justify-between pt-10 pb-6 gap-4 border-t border-light mt-12">
            <button
                onClick={handleGenerateRedline}
                className="w-full md:flex-1 flex items-center justify-center gap-3 bg-primary hover:bg-primary-hover text-white py-4 rounded-xl transition-all shadow-md shadow-primary/10 active:scale-[0.98]"
            >
                <FileText size={18} strokeWidth={2} />
                <span className="font-semibold text-sm">Generate Redlined Word</span>
            </button>

            <button
                onClick={handleExportSummary}
                className="w-full md:flex-1 flex items-center justify-center gap-3 bg-surface hover:bg-muted border border-light text-foreground py-4 rounded-xl transition-all shadow-sm active:scale-[0.98]"
            >
                <BarChart size={18} strokeWidth={2} className="text-secondary" />
                <span className="font-semibold text-sm">Export Review Summary</span>
            </button>

            <button
                onClick={handleDownloadIterationInfo}
                className="w-full md:flex-1 flex items-center justify-center gap-3 bg-surface hover:bg-muted border border-light text-foreground py-4 rounded-xl transition-all shadow-sm active:scale-[0.98]"
            >
                <Download size={18} strokeWidth={2} className="text-secondary-text" />
                <span className="font-semibold text-sm">Download pdf</span>
            </button>
        </div>
    );
};

export default ActionButtons;
