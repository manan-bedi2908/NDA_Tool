import React from 'react';
import { Project } from '../types';
import { History } from 'lucide-react';

interface IterationHeaderProps {
    project: Project;
    selectedIterationId: string | null;
    onSelectIteration: (id: string) => void;
}

const IterationHeader: React.FC<IterationHeaderProps> = ({ project, selectedIterationId, onSelectIteration }) => {
    const iterations = project.iterations || [];

    // Use selected ID or fallback to latest if available
    const activeId = selectedIterationId || (iterations.length > 0 ? iterations[iterations.length - 1].id : null);

    return (
        <div className="bg-white border-b border-slate-200 w-full sticky top-0 z-40 shadow-sm animate-in slide-in-from-top-2 duration-300">
            <div className="max-w-7xl mx-auto px-6 py-3 flex items-center justify-between">
                <div className="flex items-center gap-6">
                    <div className="flex flex-col">
                        <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Active Project</span>
                        <h3 className="text-sm font-bold text-slate-900">{project.name}</h3>
                    </div>
                    <div className="h-8 w-px bg-slate-200" />
                    <div className="flex items-center gap-2 text-slate-500">
                        <History size={14} />
                        <span className="text-xs font-medium">{iterations.length} Iterations</span>
                    </div>
                </div>

                <div className="flex items-center gap-1.5 p-1 bg-slate-100 rounded-lg">
                    {iterations.map((iteration) => {
                        const isSelected = activeId === iteration.id;
                        return (
                            <button
                                key={iteration.id}
                                onClick={() => onSelectIteration(iteration.id)}
                                className={`
                                    px-3 py-1.5 rounded-md text-xs font-bold transition-all flex items-center gap-2 cursor-pointer
                                    ${isSelected
                                        ? 'bg-white text-blue-600 shadow-sm ring-1 ring-black/5'
                                        : 'text-slate-500 hover:bg-slate-200/50 hover:text-slate-700'
                                    }
                                `}
                            >
                                <span>v{iteration.iteration_number}</span>
                                {isSelected && <span className="w-1.5 h-1.5 rounded-full bg-blue-600" />}
                            </button>
                        );
                    })}
                </div>
            </div>
        </div>
    );
};

export default IterationHeader;
