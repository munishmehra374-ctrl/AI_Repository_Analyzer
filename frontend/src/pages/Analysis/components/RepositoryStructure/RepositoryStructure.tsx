import "./RepositoryStructure.css";

interface RepositoryStructureProps {
    dependencies: string[];
    modules: string[];
}

const RepositoryStructure = ({
    dependencies,
    modules,
}: RepositoryStructureProps) => {
    return (
        <section className="repository-structure">

            <div className="repository-structure-header">
                <h2>Repository Structure</h2>

                <p>
                    Modules and dependencies identified during repository analysis.
                </p>
            </div>

            <div className="repository-structure-grid">

                <div className="repository-structure-block">

                    <h3>Modules</h3>

                    {modules.length > 0 ? (
                        <div className="structure-list">

                            {modules.map((module) => (
                                <div
                                    className="structure-item"
                                    key={module}
                                >
                                    <span className="structure-dot" />

                                    <span className="structure-name">
                                        {module}
                                    </span>
                                </div>
                            ))}

                        </div>
                    ) : (
                        <span className="structure-empty">
                            No modules detected
                        </span>
                    )}

                </div>

                <div className="repository-structure-block">

                    <h3>Dependencies</h3>

                    {dependencies.length > 0 ? (
                        <div className="structure-list">

                            {dependencies.map((dependency) => (
                                <div
                                    className="structure-item"
                                    key={dependency}
                                >
                                    <span className="structure-dot dependency-dot" />

                                    <span className="structure-name">
                                        {dependency}
                                    </span>
                                </div>
                            ))}

                        </div>
                    ) : (
                        <span className="structure-empty">
                            No dependencies detected
                        </span>
                    )}

                </div>

            </div>

        </section>
    );
};

export default RepositoryStructure;