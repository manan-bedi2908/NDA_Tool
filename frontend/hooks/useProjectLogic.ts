"use client";

import { useState, useEffect } from 'react';
import { Project } from '../types';
import {
    createIteration,
    generateProjectAnalysis,
    draftEmail,
    getLatestIteration,
    updateClause,
    compareIterations,
    getIteration
} from '../services/api';

export function useProjectLogic(selectedProjectId: string | null) {
    // File Upload State
    const [showUpload, setShowUpload] = useState(true);
    const [isUploading, setIsUploading] = useState(false);
    const [uploadStatus, setUploadStatus] = useState<{ type: 'success' | 'error' | 'info'; message: string } | null>(null);

    // Analysis State
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [summary, setSummary] = useState<string | null>(null);
    const [showSummary, setShowSummary] = useState(false);

    // Email Drafting State
    const [emailInput, setEmailInput] = useState("");
    const [emailDraft, setEmailDraft] = useState<string | null>(null);
    const [isDrafting, setIsDrafting] = useState(false);

    // Clause Review State
    const [clauses, setClauses] = useState<any[]>([]);
    const [filterStatus, setFilterStatus] = useState<string>('All');
    const [expandedClause, setExpandedClause] = useState<number | null>(null);

    // Table State
    const [isFullScreen, setIsFullScreen] = useState(false);
    const [showSearch, setShowSearch] = useState(false);
    const [searchQuery, setSearchQuery] = useState("");

    // Comparison State
    const [isComparing, setIsComparing] = useState(false);
    const [comparisonResults, setComparisonResults] = useState<any>(null);
    const [showComparisonSection, setShowComparisonSection] = useState(false);

    // Iteration State
    const [selectedIterationId, setSelectedIterationId] = useState<string | null>(null);

    // Reset state when project changes
    useEffect(() => {
        setSummary(null);
        setShowSummary(false);
        setEmailDraft(null);
        setEmailInput("");
        setClauses([]);
        setComparisonResults(null);
        setShowComparisonSection(false);
        setShowUpload(true);
        setSelectedIterationId(null);
    }, [selectedProjectId]);

    // Fetch clauses when project selected or iteration changes
    const fetchIterationData = async (iterationId?: string) => {
        if (!selectedProjectId) return;
        try {
            let data;
            if (iterationId) {
                // Fetch specific iteration
                data = await getIteration(selectedProjectId, iterationId);
            } else {
                // Fetch latest
                data = await getLatestIteration(selectedProjectId);
                if (data && data.iteration_id) {
                    setSelectedIterationId(data.iteration_id);
                }
            }

            if (data) {
                if (data.clauses) setClauses(data.clauses);
                // We update summary if it's new or if we switched iterations
                if (data.overall) setSummary(data.overall);
            }
        } catch (e) {
            console.error("Failed to fetch clauses", e);
        }
    };

    useEffect(() => {
        if (selectedProjectId) {
            fetchIterationData(selectedIterationId || undefined);
        }
    }, [selectedProjectId, selectedIterationId]); // Re-run when iteration changes

    const handleSelectIteration = (iterationId: string) => {
        setSelectedIterationId(iterationId);
    };

    const handleUpload = async (docA: File, docB: File, onRefresh: () => Promise<void>) => {
        if (!selectedProjectId) return;

        setIsUploading(true);
        setUploadStatus({ type: 'info', message: 'Starting upload & analysis...' });

        try {
            await createIteration(selectedProjectId, docA, docB);
            setUploadStatus({ type: 'success', message: 'Iteration created and analyzed successfully!' });

            // Refresh data
            await fetchIterationData();
            await onRefresh();

            setShowUpload(false);
            setSummary(null); // Clear summary so it can be re-generated for the new iteration
        } catch (error: any) {
            setUploadStatus({ type: 'error', message: error.message || 'Upload failed' });
        } finally {
            setIsUploading(false);
        }
    };

    const handleGenerateSummary = async () => {
        if (!selectedProjectId) return;

        setIsAnalyzing(true);
        try {
            const result = await generateProjectAnalysis(selectedProjectId);
            setSummary(result.summary);
        } catch (error) {
            console.error("Failed to generate summary", error);
        } finally {
            setIsAnalyzing(false);
        }
    };

    const toggleSummary = (show: boolean) => {
        setShowSummary(show);
        // If we're opening it and either have no summary or only the short "simple" one,
        // trigger the full AI assessment.
        if (show && !isAnalyzing && (!summary || summary.length < 500)) {
            handleGenerateSummary();
        }
    };

    const handleDraftEmail = async () => {
        if (!selectedProjectId) return;

        setIsDrafting(true);
        try {
            const result = await draftEmail(selectedProjectId, emailInput);
            setEmailDraft(result.email);
        } catch (error) {
            console.error("Failed to draft email", error);
        } finally {
            setIsDrafting(false);
        }
    };

    const handleUpdateClause = async (index: number, status: string, notes: string = "") => {
        if (!selectedProjectId) return;

        const updatedClauses = [...clauses];
        updatedClauses[index] = { ...updatedClauses[index], status, notes };
        setClauses(updatedClauses);

        try {
            await updateClause(selectedProjectId, index, status, notes);
        } catch (e) {
            console.error("Failed to update clause", e);
        }
    };

    const handleNoteChange = (index: number, newNotes: string) => {
        const updatedClauses = [...clauses];
        updatedClauses[index] = { ...updatedClauses[index], notes: newNotes };
        setClauses(updatedClauses);
    };

    const handleCompareIterations = async (iterationIds: string[]) => {
        if (!selectedProjectId) return;
        setIsComparing(true);
        try {
            const results = await compareIterations(selectedProjectId, iterationIds);
            setComparisonResults(results);
        } catch (e) {
            console.error("Failed to compare iterations", e);
        } finally {
            setIsComparing(false);
        }
    };

    const stats = {
        total: clauses.length,
        accepted: clauses.filter(c => c.status === 'accepted').length,
        rejected: clauses.filter(c => c.status === 'rejected').length,
        pending: clauses.filter(c => c.status === 'pending').length
    };

    return {
        showUpload, setShowUpload,
        isUploading, uploadStatus,
        isAnalyzing, summary, showSummary, setShowSummary: toggleSummary,
        emailInput, setEmailInput, emailDraft, isDrafting,
        clauses, filterStatus, setFilterStatus, expandedClause, setExpandedClause,
        isFullScreen, setIsFullScreen, showSearch, setShowSearch, searchQuery, setSearchQuery,
        isComparing, comparisonResults, showComparisonSection, setShowComparisonSection,
        handleUpload, handleGenerateSummary, handleDraftEmail, handleUpdateClause, handleNoteChange, handleCompareIterations,
        stats,
        selectedIterationId, handleSelectIteration
    };
}
