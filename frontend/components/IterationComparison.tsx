import React, { useState } from 'react';
import { Project, Iteration } from '../types';
import { ChevronRight, Calendar, FileText, CheckCircle, Clock, Layout, ArrowRight, X } from 'lucide-react';
import ReactMarkdown from 'react-markdown';


interface IterationComparisonProps {
    project: Project;
    onCompare: (iterationIds: string[]) => void;
    onClose: () => void;
    comparisonResults: any;
    isComparing: boolean;
}

const IterationComparison: React.FC<IterationComparisonProps> = ({
    project,
    onCompare,
    onClose,
    comparisonResults,
    isComparing
}) => {
    const [selectedIds, setSelectedIds] = useState<string[]>([]);
    const [showComparison, setShowComparison] = useState(false);

    const toggleSelection = (id: string) => {
        if (selectedIds.includes(id)) {
            setSelectedIds(selectedIds.filter(i => i !== id));
        } else {
            setSelectedIds([...selectedIds, id]);
        }
    };

    const handleCompare = () => {
        if (selectedIds.length < 2) return;
        const sortedIds = project.iterations!
            .filter(it => selectedIds.includes(it.id))
            .map(it => it.id);

        onCompare(sortedIds);
        setShowComparison(true);
    };

    if (!project.iterations || project.iterations.length < 2) return null;

    return (
        <div className="space-y-10 pt-10 border-t border-slate-100">
            <div className="flex items-center gap-3 text-2xl font-semibold text-slate-900">
                <Layout size={28} className="text-blue-600" strokeWidth={2.5} />
                <h3>Compare Iterations - Document Changes</h3>
            </div>

            <div className="bg-white rounded-3xl border border-slate-200 p-10 space-y-10 shadow-xl shadow-slate-200/50">
                <div className="bg-blue-50/50 border border-blue-100 rounded-2xl p-6 flex items-start gap-4 text-blue-800 text-sm font-medium">
                    <div className="p-2 bg-blue-600 rounded-lg text-white shadow-md shadow-blue-200">
                        <CheckCircle size={18} strokeWidth={2.5} />
                    </div>
                    <p className="leading-relaxed">
                        Select multiple iterations to see what the client changed in their NDA versions
                    </p>
                </div>

                <div className="space-y-6">
                    <label className="text-[10px] font-bold text-slate-400 uppercase tracking-widest block pl-1">
                        Select iterations to compare (in order)
                    </label>

                    <div className="relative group">
                        <select
                            onChange={(e) => {
                                const val = e.target.value;
                                if (val && !selectedIds.includes(val)) {
                                    setSelectedIds([...selectedIds, val]);
                                }
                                e.target.value = "";
                            }}
                            className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-6 py-4 text-sm text-slate-900 focus:outline-none focus:ring-4 focus:ring-blue-500/5 focus:border-blue-500 hover:bg-white transition-all cursor-pointer appearance-none font-bold"
                        >
                            <option value="" disabled selected> Choose Options</option>
                            {project.iterations.map((it) => (
                                <option
                                    key={it.id}
                                    value={it.id}
                                    disabled={selectedIds.includes(it.id)}
                                >
                                    Revision v{it.iteration_number} — {it.created_at}
                                </option>
                            ))}
                        </select>
                        <div className="absolute right-6 top-1/2 -translate-y-1/2 pointer-events-none text-slate-400">
                            <ChevronRight className="rotate-90" size={20} strokeWidth={2.5} />
                        </div>
                    </div>

                    {selectedIds.length > 0 && (
                        <div className="flex flex-wrap gap-3 pt-2">
                            {selectedIds.map((id) => {
                                const it = project.iterations?.find(i => i.id === id);
                                return (
                                    <div
                                        key={id}
                                        className="flex items-center gap-3 bg-white border-2 border-slate-200 text-slate-700 px-4 py-2 rounded-xl text-xs font-bold animate-in zoom-in-95 duration-200 shadow-sm"
                                    >
                                        <span className="text-blue-600">v{it?.iteration_number}</span>
                                        <button
                                            onClick={() => setSelectedIds(selectedIds.filter(i => i !== id))}
                                            className="hover:text-rose-600 transition-colors"
                                        >
                                            <X size={14} strokeWidth={3} />
                                        </button>
                                    </div>
                                );
                            })}
                            <button
                                onClick={() => setSelectedIds([])}
                                className="text-xs text-slate-400 hover:text-rose-600 font-bold uppercase tracking-widest transition-all px-3"
                            >
                                Reset Set
                            </button>
                        </div>
                    )}
                </div>

                <div className="flex justify-start">
                    <button
                        onClick={handleCompare}
                        disabled={selectedIds.length < 2 || isComparing}
                        className={`flex items-center gap-3 px-8 py-4 rounded-2xl font-bold text-base transition-all shadow-xl ${selectedIds.length >= 2 && !isComparing
                            ? 'bg-slate-900 hover:bg-slate-800 text-white shadow-slate-200 translate-y-0 active:translate-y-0.5'
                            : 'bg-slate-100 text-slate-300 cursor-not-allowed shadow-none'
                            }`}
                    >
                        {isComparing ? (
                            <div className="w-6 h-6 border-3 border-white/30 border-t-white rounded-full animate-spin" />
                        ) : (
                            <Clock size={20} strokeWidth={2.5} />
                        )}
                        Compare Selected Iterations
                    </button>
                </div>
            </div>

            {showComparison && comparisonResults && (
                <div className="space-y-12 mt-16 animate-in fade-in slide-in-from-bottom-6 duration-700">
                    <div className="space-y-6">
                        <div className="flex items-center gap-3 text-xl font-bold text-slate-900">
                            <FileText size={24} className="text-slate-700" strokeWidth={2.5} />
                            <h3>Comparison Cohort</h3>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                            {comparisonResults.iterations.map((it: any) => (
                                <div key={it.id} className="bg-white border border-slate-200 rounded-2xl p-6 space-y-4 shadow-sm hover:shadow-md transition-shadow relative overflow-hidden group">
                                    <div className="absolute -top-4 -right-4 w-16 h-16 bg-slate-50 rounded-full flex items-center justify-center pt-4 pr-4 text-xl font-black text-slate-200 group-hover:text-blue-100 transition-colors">
                                        v{it.number}
                                    </div>
                                    <h4 className="text-lg font-bold text-slate-900">Version {it.number}</h4>
                                    <div className="space-y-2">
                                        <div className="flex items-center gap-3 text-xs font-bold text-slate-500 bg-slate-50 p-2.5 rounded-lg">
                                            <Calendar size={14} className="text-blue-600" strokeWidth={2.5} />
                                            {it.date}
                                        </div>
                                        <div className="flex items-center gap-3 text-xs font-bold text-slate-500 bg-slate-50 p-2.5 rounded-lg">
                                            <FileText size={14} className="text-blue-600 flex-shrink-0" strokeWidth={2.5} />
                                            <span className="truncate">{it.docs}</span>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                    <div className="space-y-6">
                        <div className="flex items-center gap-3 text-xl font-bold text-slate-900">
                            <Clock size={24} className="text-slate-700" strokeWidth={2.5} />
                            <h3>Analytical Diff Log</h3>
                        </div>

                        <div className="space-y-6">
                            {comparisonResults.document_changes.map((change: any, idx: number) => (
                                <div key={idx} className="bg-white rounded-3xl border border-slate-200 overflow-hidden shadow-sm">
                                    <details className="group" open>
                                        <summary className="flex items-center justify-between px-8 py-6 cursor-pointer hover:bg-slate-50 transition-all list-none">
                                            <div className="flex items-center gap-4">
                                                <div className="p-3 bg-blue-50 rounded-xl text-blue-600 group-open:bg-blue-600 group-open:text-white transition-colors duration-300 shadow-sm">
                                                    <FileText size={20} strokeWidth={2.5} />
                                                </div>
                                                <div className="flex flex-col">
                                                    <span className="font-bold text-slate-900 text-lg">
                                                        Comparative Delta: v{change.from} → v{change.to}
                                                    </span>
                                                    <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Structural Modification Log</span>
                                                </div>
                                            </div>
                                            <div className={`p-2 rounded-lg transition-transform duration-300 ${idx === 0 ? 'bg-slate-100 rotate-90' : 'bg-slate-50 group-open:rotate-90'}`}>
                                                <ChevronRight className="text-slate-500" size={20} strokeWidth={3} />
                                            </div>
                                        </summary>
                                        <div className="p-10 bg-slate-50/30 border-t border-slate-100 font-medium">
                                            <div className="prose prose-slate max-w-none prose-headings:font-bold prose-p:text-slate-700 prose-li:text-slate-700 prose-strong:text-slate-900">
                                                <ReactMarkdown components={{
                                                    ul: ({ ...props }) => <ul className="list-disc pl-6 space-y-3 mt-4" {...props} />,
                                                    li: ({ ...props }) => <li className="text-slate-700 leading-relaxed" {...props} />,
                                                    p: ({ ...props }) => <p className="text-slate-700 leading-relaxed mb-6" {...props} />,
                                                    h1: ({ ...props }) => <h1 className="text-2xl font-bold text-slate-900 mb-8 border-b border-slate-200 pb-4" {...props} />,
                                                    h2: ({ ...props }) => <h2 className="text-lg font-bold text-blue-700 mt-10 mb-5 uppercase tracking-wider" {...props} />,
                                                    h3: ({ ...props }) => <h3 className="text-base font-bold text-slate-800 mt-8 mb-4 border-l-4 border-blue-600 pl-4" {...props} />,
                                                    strong: ({ ...props }) => <strong className="text-slate-900 font-black" {...props} />,
                                                }}>
                                                    {change.changes}
                                                </ReactMarkdown>
                                            </div>
                                        </div>
                                    </details>
                                </div>
                            ))}
                        </div>
                    </div>

                    <div className="flex justify-start">
                        <button
                            onClick={onClose}
                            className="flex items-center gap-3 px-6 py-3 bg-white hover:bg-slate-50 text-slate-700 rounded-xl text-sm font-bold transition-all border border-slate-200 shadow-sm active:translate-y-0.5"
                        >
                            <ArrowRight size={18} className="rotate-180" strokeWidth={2.5} />
                            Exit Comparison Suite
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default IterationComparison;
