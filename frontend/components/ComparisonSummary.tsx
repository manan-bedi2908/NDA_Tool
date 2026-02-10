import React, { useRef } from 'react';
import { BarChart, ChevronRight, FileText } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { Project } from '../types';

interface ComparisonSummaryProps {
    project: Project;
    showSummary: boolean;
    setShowSummary: (show: boolean) => void;
    isAnalyzing: boolean;
    summary: string | null;
}

const ComparisonSummary: React.FC<ComparisonSummaryProps> = ({
    project,
    showSummary,
    setShowSummary,
    isAnalyzing,
    summary
}) => {
    if (!project.iterations || project.iterations.length === 0) return null;

    const latestIteration = project.iterations[project.iterations.length - 1];
    const h2Counter = useRef(0);

    // Reset counter when summary changes
    React.useEffect(() => {
        h2Counter.current = 0;
    }, [summary]);

    return (
        <div className="space-y-6 pt-10 border-t border-slate-100">


            <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
                <button
                    onClick={() => setShowSummary(!showSummary)}
                    className={`w-full text-left px-8 py-5 flex items-center justify-between transition-all duration-300 ${showSummary ? 'bg-slate-50 border-b border-slate-200' : 'hover:bg-slate-50'}`}
                >
                    <div className="flex items-center gap-4">
                        <div className={`p-2 rounded-lg transition-colors ${showSummary ? 'bg-blue-600 text-white' : 'bg-slate-100 text-slate-400'}`}>
                            <FileText size={18} strokeWidth={2.5} />
                        </div>
                        <span className="text-xl font-semibold text-slate-700">Overall Comparison Summary</span>
                    </div>
                    <ChevronRight className={`transition-transform duration-300 text-slate-400 ${showSummary ? 'rotate-90' : ''}`} size={20} />
                </button>

                {showSummary && (
                    <div className="p-8 animate-in fade-in slide-in-from-top-1 duration-300">
                        <div className="flex gap-4 mb-8">
                            <div className="flex-1 bg-slate-50 border border-slate-200 px-5 py-4 rounded-xl flex items-center gap-4 shadow-sm">
                                <div className="p-2 bg-white rounded-lg border border-slate-100 shadow-sm">
                                    <FileText size={18} className="text-blue-600" />
                                </div>
                                <div className="min-w-0">
                                    <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-0.5">Reference Standard</p>
                                    <p className="text-sm font-bold text-slate-900 truncate">{latestIteration.docA_name || "Document A"}</p>
                                </div>
                            </div>
                            <div className="flex-1 bg-slate-50 border border-slate-200 px-5 py-4 rounded-xl flex items-center gap-4 shadow-sm">
                                <div className="p-2 bg-white rounded-lg border border-slate-100 shadow-sm">
                                    <FileText size={18} className="text-blue-600" />
                                </div>
                                <div className="min-w-0">
                                    <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-0.5">Client Proposed</p>
                                    <p className="text-sm font-bold text-slate-900 truncate">{latestIteration.docB_name || "Document B"}</p>
                                </div>
                            </div>
                        </div>

                        {isAnalyzing && (
                            <div className="flex flex-col items-center justify-center py-16 space-y-5">
                                <div className="w-10 h-10 border-4 border-slate-100 border-t-blue-600 rounded-full animate-spin shadow-sm" />
                                <p className="text-slate-500 font-bold text-sm tracking-tight animate-pulse uppercase">Generating AI Assessment...</p>
                            </div>
                        )}

                        {summary && !isAnalyzing && (
                            <div className="prose prose-slate max-w-none prose-headings:font-bold prose-headings:tracking-tight prose-p:font-medium prose-p:text-slate-600 prose-li:text-slate-600" style={{ counterReset: 'section' }}>
                                <ReactMarkdown components={{
                                    h1: ({ ...props }) => <h1 className="text-2xl font-bold text-slate-900 mb-4 mt-0 border-b border-slate-100 pb-3" {...props} />,
                                    h2: ({ ...props }) => {
                                        // Clean leading numbers from the text content to avoid double numbering
                                        const cleanChildren = React.Children.toArray(props.children).map((child, index) => {
                                            if (index === 0 && typeof child === 'string') {
                                                return child.replace(/^\d+\.\s*/, '');
                                            }
                                            return child;
                                        });

                                        return (
                                            <h2
                                                className="text-lg font-bold text-blue-600 mt-9 mb-1 uppercase tracking-wider first:mt-0"
                                                style={{ counterIncrement: 'section' }}
                                                {...props}
                                            >
                                                <span className="text-slate-400 mr-3 before:content-[counter(section)'.']"></span>
                                                {cleanChildren}
                                            </h2>
                                        );
                                    },
                                    h3: ({ ...props }) => <h3 className="text-base font-bold text-slate-800 mt-6 mb-1" {...props} />,
                                    ul: ({ ...props }) => <ul className="list-disc pl-6 space-y-1.5 text-slate-600 my-2 mt-2" {...props} />,
                                    li: ({ ...props }) => <li className="text-slate-600 leading-relaxed" {...props} />,
                                    p: ({ ...props }) => <p className="text-slate-600 leading-relaxed mb-3 mt-2 font-medium" {...props} />,
                                    strong: ({ ...props }) => <strong className="text-slate-900 font-bold" {...props} />,
                                }}>
                                    {summary}
                                </ReactMarkdown>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div >
    );
};

export default ComparisonSummary;
