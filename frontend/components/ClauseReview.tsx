import React, { useState } from 'react';
import { ClipboardList, Check, X, Clock, ChevronDown, ChevronRight, AlertTriangle } from 'lucide-react';

interface ClauseReviewProps {
    clauses: any[];
    stats: {
        total: number;
        accepted: number;
        rejected: number;
        pending: number;
    };
    filterStatus: string;
    setFilterStatus: (status: string) => void;
    expandedClause: number | null;
    setExpandedClause: (idx: number | null) => void;
    handleUpdateClause: (index: number, status: string, notes?: string) => Promise<void>;
    handleNoteChange: (index: number, newNotes: string) => void;
}

const ClauseReview: React.FC<ClauseReviewProps> = ({
    clauses,
    stats,
    filterStatus,
    setFilterStatus,
    expandedClause,
    setExpandedClause,
    handleUpdateClause,
    handleNoteChange
}) => {
    const filteredClauses = filterStatus === 'All'
        ? clauses
        : clauses.filter(c => c.status && c.status.toLowerCase() === filterStatus.toLowerCase());

    return (
        <div className="space-y-6 pt-10 border-t border-slate-100">
            <div className="flex items-center gap-3 text-xl font-semibold text-slate-900">
                <ClipboardList size={22} className="text-slate-700" strokeWidth={2.5} />
                <h3>Clause-by-Clause Review</h3>
            </div>

            {/* Stats Row */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
                    <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1.5">Total Clauses</p>
                    <p className="text-3xl font-bold text-slate-900">{stats.total}</p>
                </div>
                <div className="bg-emerald-50/30 p-5 rounded-2xl border border-emerald-100 shadow-sm">
                    <div className="flex items-center gap-2 mb-1.5">
                        <Check size={14} className="text-emerald-600" strokeWidth={3} />
                        <p className="text-[10px] text-emerald-600 font-bold uppercase tracking-widest">Accepted</p>
                    </div>
                    <p className="text-3xl font-bold text-slate-900">{stats.accepted}</p>
                </div>
                <div className="bg-rose-50/30 p-5 rounded-2xl border border-rose-100 shadow-sm">
                    <div className="flex items-center gap-2 mb-1.5">
                        <X size={14} className="text-rose-600" strokeWidth={3} />
                        <p className="text-[10px] text-rose-600 font-bold uppercase tracking-widest">Rejected</p>
                    </div>
                    <p className="text-3xl font-bold text-slate-900">{stats.rejected}</p>
                </div>
                <div className="bg-amber-50/30 p-5 rounded-2xl border border-amber-100 shadow-sm">
                    <div className="flex items-center gap-2 mb-1.5">
                        <Clock size={14} className="text-amber-600" strokeWidth={3} />
                        <p className="text-[10px] text-amber-600 font-bold uppercase tracking-widest">Pending</p>
                    </div>
                    <p className="text-3xl font-bold text-slate-900">{stats.pending}</p>
                </div>
            </div>

            {/* Filter */}
            <div className="flex items-center justify-between bg-slate-50 p-4 rounded-xl border border-slate-200">
                <div className="flex items-center gap-3">
                    <p className="text-sm text-slate-500 font-bold">Filter view:</p>
                    <div className="flex gap-2">
                        {['All', 'Accepted', 'Rejected', 'Pending'].map((status) => (
                            <button
                                key={status}
                                onClick={() => setFilterStatus(status)}
                                className={`px-4 py-1.5 rounded-lg text-xs font-bold transition-all border ${filterStatus === status
                                    ? 'bg-white text-blue-600 border-slate-200 shadow-sm'
                                    : 'text-slate-500 border-transparent hover:text-slate-900 hover:bg-slate-200/50'}`}
                            >
                                {status}
                            </button>
                        ))}
                    </div>
                </div>
            </div>

            {/* Clauses List */}
            <div className="space-y-4">
                {filteredClauses.map((clause, idx) => (
                    <div key={idx} className={`bg-white rounded-2xl border transition-all duration-300 ${expandedClause === idx ? 'border-slate-300 shadow-lg' : 'border-slate-200 hover:border-slate-300 hover:shadow-sm'}`}>
                        <button
                            onClick={() => setExpandedClause(expandedClause === idx ? null : idx)}
                            className={`w-full text-left px-6 py-4 flex items-center gap-3 transition-colors ${expandedClause === idx ? 'bg-slate-50/50' : ''}`}
                        >
                            <div className={`transition-transform duration-300 ${expandedClause === idx ? '' : '-rotate-90'}`}>
                                <ChevronDown size={18} className="text-slate-500" />
                            </div>

                            <div className="flex items-center gap-2">
                                {clause.status === 'accepted' ? <Check size={16} className="text-emerald-600" strokeWidth={3} /> :
                                    clause.status === 'rejected' ? <X size={16} className="text-rose-600" strokeWidth={3} /> :
                                        <Clock size={16} className="text-amber-600" strokeWidth={3} />}
                                <div className={`w-2 h-2 rounded-full ${clause.status === 'accepted' ? 'bg-emerald-500' : clause.status === 'rejected' ? 'bg-rose-500' : 'bg-amber-500'}`} />
                            </div>

                            <div className="flex flex-col">
                                <span className="font-semibold text-slate-800 text-sm">
                                    {clause.page ? `Page ${clause.page} - ` : ''}{clause.title || `Compliance Item ${idx + 1}`}
                                </span>
                            </div>
                        </button>

                        {expandedClause === idx && (
                            <div className="px-6 pb-6 pt-2 space-y-5 animate-in slide-in-from-top-1 duration-200">
                                <div className="space-y-4">
                                    {clause.difference && (
                                        <p className="text-sm text-slate-700 leading-relaxed font-medium">
                                            <span className="font-bold text-slate-900">Difference: </span>
                                            {clause.difference}
                                        </p>
                                    )}

                                    {clause.legal_impact && (
                                        <p className="text-sm text-slate-700 leading-relaxed font-medium">
                                            <span className="font-bold text-slate-900">Legal Impact: </span>
                                            {clause.legal_impact}
                                        </p>
                                    )}

                                    <p className="text-sm text-slate-700 leading-relaxed font-medium">
                                        <span className="font-bold text-slate-900">Risk Level: </span>
                                        <span className={`uppercase ${clause.risk === 'high' ? 'text-rose-600' : clause.risk === 'medium' ? 'text-amber-600' : 'text-emerald-600'}`}>
                                            {clause.risk || 'MEDIUM'}
                                        </span>
                                    </p>
                                </div>

                                <div className="flex items-center gap-6 pt-2">
                                    <button
                                        onClick={() => handleUpdateClause(idx, 'accepted', clause.notes)}
                                        className={`flex items-center gap-2 px-4 py-2 rounded-lg border text-sm font-bold transition-all ${clause.status === 'accepted'
                                            ? 'bg-emerald-50 border-emerald-200 text-emerald-700'
                                            : 'bg-white border-slate-200 text-slate-600 hover:border-emerald-500 hover:text-emerald-600'
                                            }`}
                                    >
                                        <div className={`flex items-center justify-center p-1 rounded ${clause.status === 'accepted' ? 'bg-emerald-600 text-white' : 'bg-slate-100 text-slate-400'}`}>
                                            <Check size={14} strokeWidth={4} />
                                        </div>
                                        <span>Accept</span>
                                    </button>

                                    <button
                                        onClick={() => handleUpdateClause(idx, 'rejected', clause.notes)}
                                        className={`flex items-center gap-2 px-4 py-2 rounded-lg border text-sm font-bold transition-all ${clause.status === 'rejected'
                                            ? 'bg-rose-50 border-rose-200 text-rose-700'
                                            : 'bg-white border-slate-200 text-slate-600 hover:border-rose-500 hover:text-rose-600'
                                            }`}
                                    >
                                        <X size={18} className={`${clause.status === 'rejected' ? 'text-rose-600' : 'text-slate-400'}`} strokeWidth={3} />
                                        <span>Reject</span>
                                    </button>
                                </div>

                                <div className="space-y-2 pt-2">
                                    <p className="text-xs font-bold text-slate-500">Add notes/reason:</p>
                                    <textarea
                                        rows={1}
                                        value={clause.notes || ""}
                                        onChange={(e) => handleNoteChange(idx, e.target.value)}
                                        onBlur={() => handleUpdateClause(idx, clause.status, clause.notes)}
                                        className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-3 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500/10 focus:border-slate-400 transition-all resize-none font-medium"
                                        placeholder=""
                                    />
                                </div>
                            </div>
                        )}
                    </div>
                ))}

                {filteredClauses.length === 0 && (
                    <div className="text-center py-20 bg-slate-50 rounded-3xl border border-dashed border-slate-200">
                        <p className="text-slate-400 text-sm font-medium">No clauses matching the selected filter.</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default ClauseReview;
