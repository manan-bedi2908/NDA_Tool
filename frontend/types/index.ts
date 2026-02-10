export interface Iteration {
    id: string;
    iteration_number: number;
    created_at: string;
    docA_name?: string;
    docB_name?: string;
    stats?: {
        accepted: number;
        rejected: number;
        pending: number;
    };
}

export interface Project {
    id: string;
    name: string;
    description?: string;
    createdAt?: string; // Frontend might use createdAt or created_at
    created_at?: string; // Backend sends created_at
    iterations?: Iteration[];
}
