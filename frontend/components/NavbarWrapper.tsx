"use client";

import React from 'react';
import Navbar from './Navbar';
import { useProjects } from '../context/ProjectContext';
import { useRouter, useParams } from 'next/navigation';

const NavbarWrapper: React.FC = () => {
    const { projects, handleCreateProject } = useProjects();
    const router = useRouter();
    const params = useParams();

    const selectedProjectId = params?.id as string | null;

    const handleSelectProject = (id: string) => {
        router.push(`/projects/${id}`);
    };

    const onCreate = async (name: string, description: string) => {
        const id = await handleCreateProject(name, description);
        if (id) {
            router.push(`/projects/${id}`);
        }
    };

    return (
        <Navbar
            projects={projects}
            selectedProjectId={selectedProjectId}
            onSelectProject={handleSelectProject}
            onCreateProject={onCreate}
        />
    );
};

export default NavbarWrapper;
