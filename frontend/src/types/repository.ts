export interface IndexRepositoryResponse {

    task_id: string;

    status: string;

}

export interface ProgressResponse {

    status: string;

    stage: string;

    progress: number;

    current_file?: string;

    files_processed?: number;

    total_files?: number;

    error?: string;

}

export interface RepositoryProfile {

    repository_name: string;

    repository_path: string;

    statistics: {

        files: number;

        classes: number;

        functions: number;

        imports: number;

    };

    languages: string[];

    frameworks: string[];

    databases: string[];

    vector_databases: string[];

    llm_frameworks: string[];

    llm_providers: string[];

    dependencies: string[];

    modules: string[];

    design_patterns: string[];

}

export interface IndexingResult {

    status: string;

    files: number;

    chunks: number;

    repository_profile: RepositoryProfile;

}