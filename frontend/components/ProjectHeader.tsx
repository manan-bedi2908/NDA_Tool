
import { Project } from '../types';
import { RefreshCw } from 'lucide-react';

interface ProjectHeaderProps {
    project: Project;
    onCompare?: () => void;
    selectedIterationId?: string | null;
    stats?: {
        accepted: number;
        rejected: number;
        pending: number;
    };
}

const ProjectHeader: React.FC<ProjectHeaderProps> = ({ project, onCompare, selectedIterationId, stats }) => {
    // Determine which iteration to show
    const latestIteration = project.iterations && project.iterations.length > 0
        ? project.iterations[project.iterations.length - 1]
        : null;

    const selectedIteration = selectedIterationId
        ? project.iterations?.find(i => i.id === selectedIterationId)
        : latestIteration;

    const displayIteration = selectedIteration || latestIteration;
    const isLatest = displayIteration && latestIteration && displayIteration.id === latestIteration.id;

    const currentStats = stats || displayIteration?.stats;

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                    <div className="w-1.5 h-8 bg-primary rounded-full" />
                    <div>
                        <h2 className="text-3xl font-bold text-foreground tracking-tight">{project.name}</h2>
                        {displayIteration && (
                            <p className="text-sm text-secondary-text font-medium mt-1">
                                {isLatest ? "Latest Iteration" : "Previous Version"} • {displayIteration.created_at}
                            </p>
                        )}
                    </div>
                </div>
                {project.iterations && project.iterations.length > 1 && (
                    <button
                        onClick={onCompare}
                        className="flex items-center gap-2.5 bg-surface border border-light hover:bg-muted text-foreground px-5 py-2.5 rounded-xl transition-all shadow-sm text-sm font-semibold"
                    >
                        <RefreshCw size={16} className="text-primary" />
                        Compare Iterations
                    </button>
                )}
            </div>

            {displayIteration ? (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {/* Version Info */}
                    <div className={`border rounded-xl px-5 py-3.5 flex flex-col gap-1 shadow-sm ${isLatest ? 'bg-muted border-light' : 'bg-slate-50 border-slate-200'}`}>
                        <span className="text-[10px] font-bold text-secondary-text uppercase tracking-widest">
                            {isLatest ? "Active Version" : "Viewing Version"}
                        </span>
                        <div className="flex items-center gap-2">
                            <span className={`font-bold text-lg ${isLatest ? 'text-primary' : 'text-slate-600'}`}>
                                Iteration v{displayIteration.iteration_number}
                            </span>
                            {!isLatest && <span className="text-xs bg-slate-200 text-slate-600 px-2 py-0.5 rounded-full font-semibold">Archived</span>}
                        </div>
                    </div>

                    {/* Documents */}
                    <div className="bg-surface border border-light rounded-xl px-5 py-3.5 flex flex-col gap-1 shadow-sm">
                        <span className="text-[10px] font-bold text-secondary-text uppercase tracking-widest">Documents Compared</span>
                        <div className="flex flex-col text-sm font-medium text-foreground truncate">
                            <span className="truncate" title={displayIteration.docA_name}>Standard: {displayIteration.docA_name || "Doc A"}</span>
                            <span className="truncate text-secondary-text" title={displayIteration.docB_name}>Client: {displayIteration.docB_name || "Doc B"}</span>
                        </div>
                    </div>

                    {/* Stats */}
                    {currentStats && (
                        <div className="bg-surface border border-light rounded-xl px-5 py-3.5 flex flex-col gap-1 shadow-sm">
                            <span className="text-[10px] font-bold text-secondary-text uppercase tracking-widest">Clause Status</span>
                            <div className="flex items-center gap-3 text-sm font-medium">
                                <span className="text-success">{currentStats.accepted} Accepted</span>
                                <span className="text-error">{currentStats.rejected} Rejected</span>
                                <span className="text-warning">{currentStats.pending} Pending</span>
                            </div>
                        </div>
                    )}
                </div>
            ) : (
                <div className="bg-surface border border-light rounded-xl px-6 py-4 inline-flex items-center gap-2 text-secondary-text text-sm italic shadow-sm">
                    No iterations created yet.
                </div>
            )}
        </div>
    );
};

export default ProjectHeader;
