import React, { useState, useEffect, useRef } from 'react';
import { Plus, User, ChevronDown } from 'lucide-react';
import { Project } from '../types';

interface NavbarProps {
    projects: Project[];
    selectedProjectId: string | null;
    onSelectProject: (id: string) => void;
    onCreateProject: (name: string, description: string) => void;
}

const Navbar: React.FC<NavbarProps> = ({
    projects,
    selectedProjectId,
    onSelectProject,
    onCreateProject,
}) => {
    const [isCreating, setIsCreating] = useState(false);
    const [newProjectName, setNewProjectName] = useState('');
    const [newProjectDesc, setNewProjectDesc] = useState('');
    const [showProjectDropdown, setShowProjectDropdown] = useState(false);
    const dropdownRef = useRef<HTMLDivElement>(null);

    const selectedProject = projects.find(p => p.id === selectedProjectId);

    // Close dropdown when clicking outside
    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
                setShowProjectDropdown(false);
            }
        };

        if (showProjectDropdown) {
            document.addEventListener('mousedown', handleClickOutside);
        }

        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, [showProjectDropdown]);

    const handleCreate = () => {
        if (newProjectName.trim()) {
            onCreateProject(newProjectName, newProjectDesc);
            setNewProjectName('');
            setNewProjectDesc('');
            setIsCreating(false);
        }
    };

    return (
        <>
            <nav className="h-16 bg-surface border-b border-light px-6 flex items-center justify-between shadow-sm">
                {/* Left: Atlas Brand + Project Selector */}
                <div className="flex items-center gap-6">
                    {/* Atlas Branding */}
                    <div className="flex items-center gap-2 cursor-pointer group/brand">
                        <span className="text-xl font-bold text-foreground group-hover/brand:text-primary transition-all duration-300 transform group-hover/brand:scale-105">
                            Atlas
                        </span>
                    </div>

                    {/* Divider */}
                    <div className="h-8 w-px bg-border-light"></div>

                    {/* Project Selector */}
                    <div className="relative" ref={dropdownRef}>
                        <button
                            onClick={() => setShowProjectDropdown(!showProjectDropdown)}
                            className="flex items-center gap-2.5 px-4 py-2 rounded-xl hover:bg-surface-hover transition-all duration-300 border border-light bg-surface shadow-sm hover:shadow-md hover:border group transform hover:scale-[1.02] active:scale-[0.98]"
                        >
                            <div className="w-1.5 h-1.5 rounded-full bg-primary group-hover:scale-150 group-hover:shadow-lg group-hover:shadow-primary/50 transition-all duration-300"></div>
                            <span className="font-semibold text-foreground text-sm transition-colors">
                                {selectedProject ? selectedProject.name : 'Select Project'}
                            </span>
                            <ChevronDown size={14} className="text-secondary-text group-hover:text-primary transition-all duration-300 group-hover:translate-y-0.5" />
                        </button>

                        {/* Project Dropdown */}
                        {showProjectDropdown && (
                            <div className="absolute top-full left-0 mt-2 w-80 bg-surface border border-light rounded-2xl shadow-xl z-50 max-h-96 overflow-hidden">
                                <div className="p-2 max-h-96 overflow-y-auto">
                                    {projects.length === 0 ? (
                                        <div className="text-center text-sm text-muted-text py-12 px-4">
                                            <div className="w-12 h-12 bg-muted rounded-full flex items-center justify-center mx-auto mb-3">
                                                <Plus size={20} className="text-muted-text" />
                                            </div>
                                            <p className="font-medium">No projects yet</p>
                                            <p className="text-xs mt-1">Create your first project to get started</p>
                                        </div>
                                    ) : (
                                        projects.map((project) => (
                                            <button
                                                key={project.id}
                                                onClick={() => {
                                                    onSelectProject(project.id);
                                                    setShowProjectDropdown(false);
                                                }}
                                                className={`w-full text-left px-4 py-3 rounded-xl flex items-center gap-3 transition-all duration-300 text-sm font-medium group/item transform ${selectedProjectId === project.id
                                                    ? 'bg-primary text-white shadow-md'
                                                    : 'text-secondary-text hover:bg-muted hover:shadow-sm hover:scale-[1.02] active:scale-[0.98]'
                                                    }`}
                                            >
                                                <div className={`w-2 h-2 rounded-full transition-all duration-300 ${selectedProjectId === project.id
                                                    ? 'bg-white shadow-lg shadow-white/50'
                                                    : 'bg-border group-hover/item:bg-primary group-hover/item:scale-125 group-hover/item:shadow-md group-hover/item:shadow-primary/50'
                                                    }`} />
                                                <span className="truncate flex-1">{project.name}</span>
                                                {selectedProjectId === project.id && (
                                                    <div className="w-1.5 h-1.5 rounded-full bg-white animate-pulse"></div>
                                                )}
                                            </button>
                                        ))
                                    )}
                                </div>
                            </div>
                        )}
                    </div>
                </div>

                {/* Right: Create Project + User */}
                <div className="flex items-center gap-3">
                    {/* Create New Project Button */}
                    <button
                        onClick={() => setIsCreating(true)}
                        className="group relative flex items-center gap-2 px-5 py-2.5 bg-primary hover:bg-primary-hover text-white rounded-xl text-sm font-semibold transition-all shadow-lg shadow-primary/25 hover:shadow-xl hover:shadow-primary/40 hover:scale-[1.02] active:scale-[0.98]"
                    >
                        <div className="absolute inset-0 bg-white/20 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity"></div>
                        <Plus size={18} className="relative z-10" strokeWidth={2.5} />
                        <span className="relative z-10">New Project</span>
                    </button>

                    {/* User Profile */}
                    <div className="flex items-center gap-2.5 px-4 py-2 border border-light rounded-xl bg-surface shadow-sm hover:bg-surface-hover hover:shadow-md hover:border transition-all duration-300 cursor-pointer group/user transform hover:scale-[1.02] active:scale-[0.98]">
                        <div className="w-7 h-7 bg-muted rounded-full flex items-center justify-center group-hover/user:bg-primary transition-all duration-300 group-hover/user:shadow-lg group-hover/user:shadow-primary/30">
                            <User size={14} className="text-secondary-text group-hover/user:text-white transition-colors duration-300" strokeWidth={2.5} />
                        </div>
                        <span className="text-sm font-semibold text-secondary-text group-hover/user:text-foreground transition-colors">User</span>
                    </div>
                </div>
            </nav>


            {/* Create Project Modal */}
            {isCreating && (
                <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4" onClick={() => setIsCreating(false)}>
                    <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg p-8 transform transition-all" onClick={(e) => e.stopPropagation()}>
                        {/* Header */}
                        <div className="flex items-center gap-3 mb-6">
                            <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg">
                                <Plus size={20} className="text-white" strokeWidth={2.5} />
                            </div>
                            <h2 className="text-2xl font-bold bg-gradient-to-r from-slate-900 to-slate-700 bg-clip-text text-transparent">
                                Create New Project
                            </h2>
                        </div>

                        <div className="space-y-5">
                            <div>
                                <label className="block text-xs font-bold text-slate-500 mb-2 uppercase tracking-wider">
                                    Project Name
                                </label>
                                <input
                                    type="text"
                                    value={newProjectName}
                                    onChange={(e) => setNewProjectName(e.target.value)}
                                    placeholder="e.g. Asset Purchase NDA"
                                    className="w-full px-4 py-3 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 bg-slate-50/50 text-slate-900 placeholder-slate-400 transition-all hover:bg-white"
                                    autoFocus
                                />
                            </div>
                            <div>
                                <label className="block text-xs font-bold text-slate-500 mb-2 uppercase tracking-wider">
                                    Description (Optional)
                                </label>
                                <textarea
                                    value={newProjectDesc}
                                    onChange={(e) => setNewProjectDesc(e.target.value)}
                                    placeholder="Brief description of your project..."
                                    rows={3}
                                    className="w-full px-4 py-3 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 bg-slate-50/50 text-slate-900 placeholder-slate-400 resize-none transition-all hover:bg-white"
                                />
                            </div>
                            <div className="flex gap-3 pt-2">
                                <button
                                    onClick={() => setIsCreating(false)}
                                    className="flex-1 py-3 px-4 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl text-sm font-semibold transition-all"
                                >
                                    Cancel
                                </button>
                                <button
                                    onClick={handleCreate}
                                    disabled={!newProjectName.trim()}
                                    className="flex-1 py-3 px-4 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white rounded-xl text-sm font-semibold disabled:opacity-40 disabled:cursor-not-allowed shadow-lg shadow-blue-500/25 hover:shadow-xl hover:shadow-blue-500/40 transition-all disabled:hover:shadow-lg"
                                >
                                    Create Project
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </>
    );
};

export default Navbar;
