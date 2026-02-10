import React from 'react';
import { Table, X, Maximize2, Search, Download } from 'lucide-react';

interface ReviewTableProps {
    clauses: any[];
    isFullScreen: boolean;
    setIsFullScreen: (fs: boolean) => void;
    showSearch: boolean;
    setShowSearch: (s: boolean) => void;
    searchQuery: string;
    setSearchQuery: (q: string) => void;
    handleExportSummary: () => void;
}

const ReviewTable: React.FC<ReviewTableProps> = ({
    clauses,
    isFullScreen,
    setIsFullScreen,
    showSearch,
    setShowSearch,
    searchQuery,
    setSearchQuery,
    handleExportSummary
}) => {
    if (!clauses.length) return null;

    const tableData = clauses.filter(c =>
        !searchQuery ||
        (c.title && c.title.toLowerCase().includes(searchQuery.toLowerCase())) ||
        (c.difference && c.difference.toLowerCase().includes(searchQuery.toLowerCase())) ||
        (c.legal_impact && c.legal_impact.toLowerCase().includes(searchQuery.toLowerCase()))
    );

    return (
        <div className={`space-y-6 pt-10 border-t border-slate-100 ${isFullScreen ? 'fixed inset-0 z-50 bg-white p-12 overflow-y-auto' : ''}`}>
            <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-3 text-xl font-semibold text-slate-900">
                    <Table size={24} className="text-slate-700" strokeWidth={2.5} />
                    <h3>Detailed Clause Matrix</h3>
                </div>
                <div className="flex items-center gap-3">
                    {showSearch && (
                        <div className="relative animate-in slide-in-from-right-2 duration-300">
                            <input
                                type="text"
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                placeholder="Search provisions..."
                                className="bg-slate-50 border border-slate-200 rounded-xl px-10 py-2.5 text-sm text-slate-900 focus:outline-none focus:ring-4 focus:ring-blue-500/5 focus:border-blue-500 transition-all w-80 font-medium"
                                autoFocus
                            />
                            <Search size={16} className="absolute left-4 top-3.5 text-slate-400" />
                        </div>
                    )}
                    <div className="flex items-center bg-slate-50 rounded-xl border border-slate-200 p-1">
                        <button
                            onClick={() => setIsFullScreen(!isFullScreen)}
                            className={`p-2.5 rounded-lg transition-all ${isFullScreen ? 'bg-white text-blue-600 shadow-sm' : 'text-slate-400 hover:text-slate-600'}`}
                            title={isFullScreen ? "Exit Full Screen" : "Full Screen"}
                        >
                            {isFullScreen ? <X size={18} strokeWidth={2.5} /> : <Maximize2 size={18} strokeWidth={2.5} />}
                        </button>
                        <button
                            onClick={() => { setShowSearch(!showSearch); if (showSearch) setSearchQuery(""); }}
                            className={`p-2.5 rounded-lg transition-all ${showSearch ? 'bg-white text-blue-600 shadow-sm' : 'text-slate-400 hover:text-slate-600'}`}
                            title="Filter Matrix"
                        >
                            <Search size={18} strokeWidth={2.5} />
                        </button>
                        <div className="w-px h-6 bg-slate-200 mx-1" />
                        <button
                            onClick={handleExportSummary}
                            className="p-2.5 rounded-lg text-slate-400 hover:text-blue-600 hover:bg-white transition-all"
                            title="Export to CSV"
                        >
                            <Download size={18} strokeWidth={2.5} />
                        </button>
                    </div>
                </div>
            </div>

            <div className={`bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden overflow-x-auto ${isFullScreen ? 'h-[calc(100vh-180px)]' : ''}`}>
                <table className="w-full text-left text-sm border-collapse table-fixed">
                    <thead>
                        <tr className="bg-slate-50 border-b border-slate-200">
                            <th className="px-4 py-4 font-bold text-slate-400 uppercase tracking-widest text-[10px] text-center w-[5%]">Page</th>
                            <th className="px-4 py-4 font-bold text-slate-900 text-xs uppercase tracking-wider w-[15%]">Clause Title</th>
                            <th className="px-4 py-4 font-bold text-slate-900 text-xs uppercase tracking-wider w-[35%]">Comparative Note</th>
                            <th className="px-4 py-4 font-bold text-slate-900 text-xs uppercase tracking-wider w-[25%]">Assessment</th>
                            <th className="px-4 py-4 font-bold text-slate-900 text-xs uppercase tracking-wider w-[10%]">Risk Profile</th>
                            <th className="px-4 py-4 font-bold text-slate-900 text-xs uppercase tracking-wider w-[10%]">Disposition</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100 font-medium">
                        {tableData.map((clause, idx) => (
                            <tr key={idx} className="hover:bg-slate-50/50 transition-colors">
                                <td className="px-4 py-3 text-center text-slate-400 font-bold align-top">{clause.page}</td>
                                <td className="px-4 py-3 font-bold text-slate-900 align-top break-words">{clause.title}</td>
                                <td className="px-4 py-3 leading-relaxed text-slate-600 align-top text-justify">{clause.difference}</td>
                                <td className="px-4 py-3 leading-relaxed text-blue-700 font-semibold align-top text-justify">{clause.legal_impact}</td>
                                <td className="px-4 py-3 align-top">
                                    <span className={`inline-flex items-center px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-tight border ${clause.risk?.toLowerCase() === 'high' ? 'bg-rose-50 text-rose-600 border-rose-100' :
                                        clause.risk?.toLowerCase() === 'medium' ? 'bg-amber-50 text-amber-600 border-amber-100' :
                                            'bg-emerald-50 text-emerald-600 border-emerald-100'
                                        }`}>
                                        {clause.risk || 'Low'}
                                    </span>
                                </td>
                                <td className="px-4 py-3 align-top">
                                    <span className={`inline-flex items-center px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-tight ${clause.status === 'accepted' ? 'bg-emerald-600 text-white shadow-sm' :
                                        clause.status === 'rejected' ? 'bg-rose-600 text-white shadow-sm' :
                                            'bg-slate-100 text-slate-400'
                                        }`}>
                                        {clause.status || 'Pending'}
                                    </span>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
                {tableData.length === 0 && (
                    <div className="py-20 text-center bg-slate-50">
                        <p className="text-slate-400 text-sm font-bold uppercase tracking-widest">No matching records found</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default ReviewTable;
