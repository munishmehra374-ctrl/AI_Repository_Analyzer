import "./Dashboard.css";

import { useEffect, useState } from "react";

import MetricCard from "../../components/MetricCard/MetricCard";
import GlassCard from "../../components/GlassCard/GlassCard";

import { useRepository } from "../../context/RepositoryContext";
import { getRepositoryProfile } from "../../services/dashboardService";

import type { RepositoryProfile } from "../../types/repository";

function Dashboard() {

    const { taskId } = useRepository();

    const [profile, setProfile] =
        useState<RepositoryProfile | null>(null);

    const [loading, setLoading] =
        useState(true);

    useEffect(() => {

        async function loadRepository() {

            if (!taskId) return;

            try {

                const data =
                    await getRepositoryProfile(taskId);

                setProfile(data);

            }

            catch (error) {

                console.error(error);

            }

            finally {

                setLoading(false);

            }

        }

        loadRepository();

    }, [taskId]);

    if (loading) {

        return <h2>Loading...</h2>;

    }

    if (!profile) {

        return <h2>No Repository Indexed</h2>;

    }

    const technologies = [

        ...profile.languages,

        ...profile.frameworks,

        ...profile.databases,

        ...profile.vector_databases,

        ...profile.llm_frameworks,

        ...profile.llm_providers,

    ];

    return (

        <div className="dashboard">

            {/* =====================================
                Repository Header
            ====================================== */}

            <section className="repository-header">

                <h1>

                    {profile.repository_name}

                </h1>

                <p>

                    {profile.repository_path}

                </p>

                <span className="indexed-label">

                    ● Indexed Successfully

                </span>

            </section>


            {/* =====================================
                Repository Metadata
            ====================================== */}

            <section className="metadata-grid">

                <div className="metadata-card">

                    <span>Repository</span>

                    <h2>

                        {profile.repository_name}

                    </h2>

                </div>


                <div className="metadata-card">

                    <span>Primary Language</span>

                    <h2 className="highlight">

                        {profile.languages.length
                            ? profile.languages.join(", ")
                            : "--"}

                    </h2>

                </div>


                <div className="metadata-card">

                    <span>Framework</span>

                    <h2>

                        {profile.frameworks.length
                            ? profile.frameworks.join(", ")
                            : "--"}

                    </h2>

                </div>


                <div className="metadata-card">

                    <span>Database</span>

                    <h2>

                        {profile.databases.length
                            ? profile.databases.join(", ")
                            : "--"}

                    </h2>

                </div>


                <div className="metadata-card">

                    <span>Vector Store</span>

                    <h2>

                        {profile.vector_databases.length
                            ? profile.vector_databases.join(", ")
                            : "--"}

                    </h2>

                </div>

            </section>


            {/* =====================================
                Repository Statistics Cards
            ====================================== */}

            <section className="statistics-grid">

                <MetricCard
                    title="Files"
                    value={profile.statistics.files}
                />

                <MetricCard
                    title="Classes"
                    value={profile.statistics.classes}
                />

                <MetricCard
                    title="Functions"
                    value={profile.statistics.functions}
                />

                <MetricCard
                    title="Imports"
                    value={profile.statistics.imports}
                />

                <MetricCard
                    title="Modules"
                    value={profile.modules.length}
                />

            </section>


            {/* =====================================
                Technology + Statistics
            ====================================== */}


            <section className="dashboard-row">

    <GlassCard title="Technology Stack">

        <p className="section-description">
            Detected across the codebase
        </p>

        <div className="technology-list">

            {technologies.length > 0 ? (

                technologies.map((technology) => (

                    <span
                        className="technology-pill"
                        key={technology}
                    >
                        {technology}
                    </span>

                ))

            ) : (

                <span>No technologies detected</span>

            )}

        </div>

    </GlassCard>


    <GlassCard title="Repository Statistics">

        <div className="stat-row">

            <span>Source Files</span>

            <strong>
                {profile.statistics.files}
            </strong>

        </div>


        <div className="stat-row">

            <span>Classes</span>

            <strong>
                {profile.statistics.classes}
            </strong>

        </div>


        <div className="stat-row">

            <span>Functions</span>

            <strong>
                {profile.statistics.functions}
            </strong>

        </div>


        <div className="stat-row">

            <span>Imports</span>

            <strong>
                {profile.statistics.imports}
            </strong>

        </div>


        <div className="stat-row">

            <span>Dependencies</span>

            <strong>
                {profile.dependencies.length}
            </strong>

        </div>


        <div className="stat-row">

            <span>Modules</span>

            <strong>
                {profile.modules.length}
            </strong>

        </div>


        <div className="stat-row">

            <span>Status</span>

            <strong className="ready-status">
                ● Indexed
            </strong>

        </div>

    </GlassCard>

</section>



{/* =====================================
    Architecture + Knowledge Graph
====================================== */}

<section className="dashboard-row">

    <GlassCard title="Architecture Summary">

        <p className="section-description">

            Generated from repository metadata

        </p>

        <p className="architecture-text">

            This repository contains{" "}

            <b>{profile.statistics.files}</b> source files,

            <b> {profile.statistics.classes}</b> classes and

            <b> {profile.statistics.functions}</b> functions.

            The primary framework detected is{" "}

            <b>

                {profile.frameworks.length
                    ? profile.frameworks.join(", ")
                    : "Unknown"}

            </b>

            {" "}and the project is primarily written in{" "}

            <b>

                {profile.languages.length
                    ? profile.languages.join(", ")
                    : "Unknown"}

            </b>.

        </p>


        <div className="architecture-flow">

            <span>Repository</span>

            <b>→</b>

            <span>Parser</span>

            <b>→</b>

            <span>Chunking</span>

            <b>→</b>

            <span>Knowledge Graph</span>

            <b>→</b>

            <span>Embeddings</span>

            <b>→</b>

            <span>Retrieval</span>

        </div>

    </GlassCard>



    <GlassCard title="Knowledge Graph Summary">

        <p className="section-description">

            Repository metadata extracted

        </p>


        <div className="stat-row">

            <span>Languages</span>

            <strong>

                {profile.languages.length}

            </strong>

        </div>


        <div className="stat-row">

            <span>Frameworks</span>

            <strong>

                {profile.frameworks.length}

            </strong>

        </div>


        <div className="stat-row">

            <span>Databases</span>

            <strong>

                {profile.databases.length}

            </strong>

        </div>


        <div className="stat-row">

            <span>Dependencies</span>

            <strong>

                {profile.dependencies.length}

            </strong>

        </div>


        <div className="stat-row">

            <span>Modules</span>

            <strong>

                {profile.modules.length}

            </strong>

        </div>


        <div className="stat-row">

            <span>Design Patterns</span>

            <strong>

                {profile.design_patterns.length}

            </strong>

        </div>


        <div className="stat-row">

            <span>Graph Status</span>

            <strong className="ready-status">

                ● Generated

            </strong>

        </div>

    </GlassCard>

</section>

</div>

);

}

export default Dashboard;