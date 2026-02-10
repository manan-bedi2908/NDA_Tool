const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Uploads a file to the backend.
 * @param file - The file object to upload.
 * @returns The response data from the backend.
 */
export const createProject = async (name: string, description: string = ""): Promise<any> => {
    const response = await fetch(`${API_BASE_URL}/projects`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name, description }),
    });
    if (!response.ok) throw new Error("Failed to create project");
    return response.json();
};

export const getProjects = async (): Promise<any> => {
    const response = await fetch(`${API_BASE_URL}/projects`);
    if (!response.ok) throw new Error("Failed to fetch projects");
    return response.json();
};

/**
 * Uploads files to create a new iteration.
 * @param projectId - The project ID to add iteration to.
 * @param fileA - Document A (Standard).
 * @param fileB - Document B (Client).
 * @returns The response data from the backend.
 */
export const createIteration = async (projectId: string, fileA: File, fileB: File): Promise<any> => {
    const formData = new FormData();
    formData.append('project_id', projectId);
    formData.append('fileA', fileA);
    formData.append('fileB', fileB);

    try {
        const response = await fetch(`${API_BASE_URL}/create_iteration`, {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || errorData.message || `Upload failed with status ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('Error creating iteration:', error);
        throw error;
    }
};

/**
 * Sends a question to the backend.
 * @param question - The question string to ask.
 * @returns The response data from the backend.
 */
export const askQuestion = async (question: string): Promise<any> => {
    try {
        const response = await fetch(`${API_BASE_URL}/ask`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ question }),
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || errorData.message || `Question failed with status ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('Error asking question:', error);
        throw error;
    }
};

export const generateProjectAnalysis = async (projectId: string): Promise<any> => {
    const response = await fetch(`${API_BASE_URL}/projects/${projectId}/analyze`, {
        method: 'POST',
    });
    if (!response.ok) throw new Error("Failed to generate analysis");
    return response.json();
};

export const draftEmail = async (projectId: string, userInput: string): Promise<any> => {
    const response = await fetch(`${API_BASE_URL}/projects/${projectId}/draft_email`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ user_input: userInput }),
    });
    if (!response.ok) throw new Error("Failed to draft email");
    return response.json();
};

export const getLatestIteration = async (projectId: string): Promise<any> => {
    const response = await fetch(`${API_BASE_URL}/projects/${projectId}/iteration/latest`);
    if (!response.ok) throw new Error("Failed to fetch latest iteration");
    return response.json();
};

export const getIteration = async (projectId: string, iterationId: string): Promise<any> => {
    const response = await fetch(`${API_BASE_URL}/projects/${projectId}/iteration/${iterationId}`);
    if (!response.ok) throw new Error("Failed to fetch iteration");
    return response.json();
};


export const updateClause = async (projectId: string, index: number, status: string, notes: string): Promise<any> => {
    const response = await fetch(`${API_BASE_URL}/projects/${projectId}/iteration/clause/update`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ index, status, notes }),
    });
    if (!response.ok) throw new Error("Failed to update clause");
    return response.json();
};

export const compareIterations = async (projectId: string, iterationIds: string[]): Promise<any> => {
    const response = await fetch(`${API_BASE_URL}/projects/${projectId}/compare`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ iteration_ids: iterationIds }),
    });
    if (!response.ok) throw new Error("Failed to compare iterations");
    return response.json();
};
