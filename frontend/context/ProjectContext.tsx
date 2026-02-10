"use client";

import React, { createContext, useContext, useState, useEffect } from 'react';
import { Project } from '../types';
import { getProjects, createProject } from '../services/api';

interface ProjectContextType {
    projects: Project[];
    selectedProjectId: string | null;
    setSelectedProjectId: (id: string | null) => void;
    refreshProjects: () => Promise<void>;
    handleCreateProject: (name: string, description: string) => Promise<string | undefined>;
    handleDeleteProject: (id: string) => void;
}

const ProjectContext = createContext<ProjectContextType | undefined>(undefined);

export function ProjectProvider({ children }: { children: React.ReactNode }) {
    const [projects, setProjects] = useState<Project[]>([]);
    const [selectedProjectId, setSelectedProjectId] = useState<string | null>(null);

    const refreshProjects = async () => {
        try {
            const projectsData = await getProjects();
            const projectsList: Project[] = Object.values(projectsData);
            setProjects(projectsList);
        } catch (error) {
            console.error("Failed to fetch projects", error);
        }
    };

    useEffect(() => {
        refreshProjects();
    }, []);

    const handleCreateProject = async (name: string, description: string) => {
        try {
            const result = await createProject(name, description);
            await refreshProjects();
            return result.id;
        } catch (error) {
            console.error("Failed to create project", error);
        }
    };

    const handleDeleteProject = (id: string) => {
        // In a real app, you'd call a delete API here
        setProjects(prev => prev.filter((p) => p.id !== id));
        if (selectedProjectId === id) {
            setSelectedProjectId(null);
        }
    };

    return (
        <ProjectContext.Provider value={{
            projects,
            selectedProjectId,
            setSelectedProjectId,
            refreshProjects,
            handleCreateProject,
            handleDeleteProject
        }}>
            {children}
        </ProjectContext.Provider>
    );
}

export function useProjects() {
    const context = useContext(ProjectContext);
    if (context === undefined) {
        throw new Error('useProjects must be used within a ProjectProvider');
    }
    return context;
}
