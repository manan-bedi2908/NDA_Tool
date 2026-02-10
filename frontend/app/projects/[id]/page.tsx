"use client";

import React from 'react';
import { useParams } from 'next/navigation';
import { useProjects } from '../../../context/ProjectContext';
import { useProjectLogic } from '../../../hooks/useProjectLogic';
import ProjectHeader from '../../../components/ProjectHeader';
import IterationUpload from '../../../components/IterationUpload';
import ComparisonSummary from '../../../components/ComparisonSummary';
import ClauseReview from '../../../components/ClauseReview';
import ReviewTable from '../../../components/ReviewTable';
import EmailDraft from '../../../components/EmailDraft';
import ActionButtons from '../../../components/ActionButtons';
import IterationComparison from '../../../components/IterationComparison';
import IterationHeader from '../../../components/IterationHeader';

export default function ProjectPage() {
    const params = useParams();
    const id = params?.id as string;
    const { projects, refreshProjects } = useProjects();
    const selectedProject = projects.find(p => p.id === id);

    const {
        showUpload, setShowUpload,
        isUploading, uploadStatus,
        isAnalyzing, summary, showSummary, setShowSummary,
        emailInput, setEmailInput, emailDraft, isDrafting,
        clauses, filterStatus, setFilterStatus, expandedClause, setExpandedClause,
        isFullScreen, setIsFullScreen, showSearch, setShowSearch, searchQuery, setSearchQuery,
        isComparing, comparisonResults, showComparisonSection, setShowComparisonSection,
        handleUpload, handleGenerateSummary, handleDraftEmail, handleUpdateClause, handleNoteChange, handleCompareIterations,
        stats,
        selectedIterationId, handleSelectIteration
    } = useProjectLogic(id);

    if (!selectedProject) {
        return (
            <div className="p-12 flex items-center justify-center h-full bg-white">
                <div className="bg-surface border border-light rounded-2xl p-8 text-center max-w-md shadow-sm">
                    <div className="w-16 h-16 bg-muted rounded-full flex items-center justify-center mx-auto mb-6 border border-light">
                        <span className="text-2xl text-warning">!</span>
                    </div>
                    <h2 className="text-xl font-bold text-foreground mb-2">Project Not Found</h2>
                    <p className="text-secondary-text font-medium text-sm leading-relaxed mb-6">
                        The requested project data may have been archived or moved.
                    </p>
                    <button
                        onClick={() => window.location.href = '/'}
                        className="px-6 py-2.5 bg-primary text-white rounded-xl text-sm font-bold shadow-md shadow-primary/10 hover:bg-primary-hover transition-all"
                    >
                        Return to Control Center
                    </button>
                </div>
            </div>
        );
    }

    const handleExportSummary = () => {
        if (!clauses.length) return;
        const headers = ["Page", "Title", "Difference", "Legal Impact", "Risk", "Status", "Notes"];
        const rows = clauses.map((c: any) => [
            c.page,
            `"${(c.title || '').replace(/"/g, '""')}"`,
            `"${(c.difference || '').replace(/"/g, '""')}"`,
            `"${(c.legal_impact || '').replace(/"/g, '""')}"`,
            c.risk,
            c.status,
            `"${(c.notes || '').replace(/"/g, '""')}"`
        ]);
        const csvContent = [headers.join(","), ...rows.map((r: any) => r.join(","))].join("\n");
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.setAttribute("href", url);
        link.setAttribute("download", `review_summary_${selectedProject.name}.csv`);
        link.style.display = "none";
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    const handleGenerateRedline = () => {
        window.location.href = `http://localhost:8000/projects/${id}/redline`;
    };

    const handleDownloadIterationInfo = () => {
        if (!selectedProject.iterations?.length) return;
        const latestIteration = selectedProject.iterations[selectedProject.iterations.length - 1];
        const content = [
            `Project Name: ${selectedProject.name}`,
            `Iteration Number: ${latestIteration.iteration_number}`,
            `Document A File Name: ${latestIteration.docA_name || 'N/A'}`,
            `Document B File Name: ${latestIteration.docB_name || 'N/A'}`,
            `Creation Date: ${latestIteration.created_at || 'N/A'}`,
        ].join('\n');
        const blob = new Blob([content], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `iteration_info_v${latestIteration.iteration_number}.txt`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    };

    return (
        <div className="w-full min-h-screen bg-muted flex flex-col">
            <IterationHeader
                project={selectedProject}
                selectedIterationId={selectedIterationId}
                onSelectIteration={handleSelectIteration}
            />

            <div className="flex-1 w-full max-w-6xl mx-auto px-6 py-8 md:px-12 md:py-10">
                <div className="space-y-10">
                    <ProjectHeader
                        project={selectedProject}
                        onCompare={() => setShowComparisonSection(true)}
                        selectedIterationId={selectedIterationId}
                        stats={stats}
                    />

                    {showComparisonSection ? (
                        <IterationComparison
                            project={selectedProject}
                            onCompare={handleCompareIterations}
                            onClose={() => setShowComparisonSection(false)}
                            comparisonResults={comparisonResults}
                            isComparing={isComparing}
                        />
                    ) : (
                        <>
                            <IterationUpload
                                onUpload={(docA, docB) => handleUpload(docA, docB, refreshProjects)}
                                isUploading={isUploading}
                                uploadStatus={uploadStatus}
                                showUpload={showUpload}
                                setShowUpload={setShowUpload}
                            />

                            {selectedProject.iterations && selectedProject.iterations.length > 0 && (
                                <>
                                    <ComparisonSummary
                                        project={selectedProject}
                                        showSummary={showSummary}
                                        setShowSummary={setShowSummary}
                                        isAnalyzing={isAnalyzing}
                                        summary={summary}
                                    />

                                    <ClauseReview
                                        clauses={clauses}
                                        stats={stats}
                                        filterStatus={filterStatus}
                                        setFilterStatus={setFilterStatus}
                                        expandedClause={expandedClause}
                                        setExpandedClause={setExpandedClause}
                                        handleUpdateClause={handleUpdateClause}
                                        handleNoteChange={handleNoteChange}
                                    />

                                    <ReviewTable
                                        clauses={clauses}
                                        isFullScreen={isFullScreen}
                                        setIsFullScreen={setIsFullScreen}
                                        showSearch={showSearch}
                                        setShowSearch={setShowSearch}
                                        searchQuery={searchQuery}
                                        setSearchQuery={setSearchQuery}
                                        handleExportSummary={handleExportSummary}
                                    />

                                    <EmailDraft
                                        emailInput={emailInput}
                                        setEmailInput={setEmailInput}
                                        isDrafting={isDrafting}
                                        handleDraftEmail={handleDraftEmail}
                                        emailDraft={emailDraft}
                                    />

                                    <ActionButtons
                                        handleGenerateRedline={handleGenerateRedline}
                                        handleExportSummary={handleExportSummary}
                                        handleDownloadIterationInfo={handleDownloadIterationInfo}
                                    />
                                </>
                            )}
                        </>
                    )}
                </div>
            </div>
        </div>
    );
}
