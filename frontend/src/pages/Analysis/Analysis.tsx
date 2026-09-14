import React, {
    useEffect,
    useState,
} from "react";

import {
    getRepositoryProfile,
    getGraphStatistics,
    getDependencyGraph,
} from "../../services/repositoryService";

import AnalysisHeader from "./components/AnalysisHeader/AnalysisHeader";
import AnalysisStats from "./components/AnalysisStats/AnalysisStats";
import TechnologyStack from "./components/TechnologyStack/TechnologyStack";
import ArchitectureSummary from "./components/ArchitectureSummary/ArchitectureSummary";
import RepositoryStructure from "./components/RepositoryStructure/RepositoryStructure";
import FolderStructure from "./components/FolderStructure/FolderStructure";
import KnowledgeGraphSummary from "./components/KnowledgeGraphSummary/KnowledgeGraphSummary";
import DependencyGraph from "./components/DependencyGraph/DependencyGraph";
import { useRepository } from "../../context/RepositoryContext";

import "./Analysis.css";


const Analysis: React.FC = () => {

    const {
        taskId: contextTaskId,
        repositoryId: contextRepoId,
    } = useRepository();

    const [profile, setProfile] =
        useState<any>(null);

    const [graphStats, setGraphStats] =
        useState<any>(null);

    const [dependencyGraph, setDependencyGraph] =
        useState<any[]>([]);

    const [loading, setLoading] =
        useState(true);

    const [error, setError] =
        useState<string | null>(null);


    useEffect(() => {

        const loadAnalysis = async () => {

            try {

                const taskId =
                    contextTaskId ||
                    localStorage.getItem(
                        "repository_task_id"
                    ) ||
                    contextRepoId ||
                    localStorage.getItem(
                        "repository_id"
                    ) ||
                    localStorage.getItem(
                        "task_id"
                    );

                if (!taskId) {

                    setError(
                        "Repository task ID not found."
                    );

                    return;
                }


                // =========================================
                // Repository Profile
                // =========================================

                const profileData =
                    await getRepositoryProfile(
                        taskId
                    );

                if (profileData?.error) {

                    setError(
                        profileData.error
                    );

                    return;
                }


                const repoId =
                    profileData?.repository_id ||
                    localStorage.getItem("repository_id") ||
                    undefined;

                // =========================================
                // Knowledge Graph Statistics
                // =========================================

                const graphData =
                    await getGraphStatistics(repoId);


                // =========================================
                // Dependency Graph
                // =========================================

                const dependencyData =
                    await getDependencyGraph(repoId);


                // =========================================
                // Store Data
                // =========================================

                setProfile(
                    profileData
                );

                setGraphStats(
                    graphData
                );

                setDependencyGraph(
                    dependencyData
                );

            } catch (err) {

                console.error(
                    "Failed to load repository analysis:",
                    err
                );

                setError(
                    "Failed to load repository analysis."
                );

            } finally {

                setLoading(false);

            }
        };


        loadAnalysis();

    }, [contextTaskId, contextRepoId]);


    // =========================================
    // Loading
    // =========================================

    if (loading) {

        return (
            <div className="analysis-page">

                <div className="analysis-loading">
                    Loading repository analysis...
                </div>

            </div>
        );
    }


    // =========================================
    // Error
    // =========================================

    if (error) {

        return (
            <div className="analysis-page">

                <div className="analysis-error">
                    {error}
                </div>

            </div>
        );
    }


    // =========================================
    // No Profile
    // =========================================

    if (!profile) {

        return (
            <div className="analysis-page">

                <div className="analysis-error">
                    No repository profile available.
                </div>

            </div>
        );
    }


    // =========================================
    // Page
    // =========================================

    return (

        <div className="analysis-page">


            {/* =================================================
                Repository Header
            ================================================= */}

            <AnalysisHeader
                repositoryName={
                    profile.repository_name
                }
                repositoryPath={
                    profile.repository_path
                }
            />


            {/* =================================================
                Repository Statistics
            ================================================= */}

            <AnalysisStats
                statistics={
                    profile.statistics
                }
            />


            {/* =================================================
                Technology Stack
            ================================================= */}

            <TechnologyStack
                languages={
                    profile.languages
                }
                frameworks={
                    profile.frameworks
                }
                databases={
                    profile.databases
                }
                vectorDatabases={
                    profile.vector_databases
                }
                llmFrameworks={
                    profile.llm_frameworks
                }
                llmProviders={
                    profile.llm_providers
                }
            />


            {/* =================================================
                Architecture
            ================================================= */}

            <ArchitectureSummary
                modules={
                    profile.modules
                }
                designPatterns={
                    profile.design_patterns
                }
            />


            {/* =================================================
                Repository Structure
            ================================================= */}

            <RepositoryStructure
                dependencies={
                    profile.dependencies
                }
                modules={
                    profile.modules
                }
            />


            {/* =================================================
                Folder / File Structure
            ================================================= */}

            <FolderStructure
                files={
                    (
                        profile.source_files || []
                    ).map(
                        (path: string) => ({
                            path,
                        })
                    )
                }
            />


            {/* =================================================
                Knowledge Graph
            ================================================= */}

            {graphStats && (

                <KnowledgeGraphSummary
                    files={
                        graphStats.files
                    }
                    classes={
                        graphStats.classes
                    }
                    functions={
                        graphStats.functions
                    }
                    relationships={
                        graphStats.relationships
                    }
                />

            )}


            {/* =================================================
                Dependency Graph
            ================================================= */}

            <DependencyGraph
                data={
                    dependencyGraph
                }
            />

        </div>
    );
};


export default Analysis;