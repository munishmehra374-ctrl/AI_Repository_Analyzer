import "./ArchitectureSummary.css";

interface ArchitectureSummaryProps {
    modules: string[];
    designPatterns: string[];
}

const ArchitectureSummary = ({
    modules,
    designPatterns,
}: ArchitectureSummaryProps) => {
    return (
        <section className="architecture-summary">

            <div className="architecture-summary-header">
                <h2>Architecture</h2>

                <p>
                    Structural patterns and modules detected in the repository.
                </p>
            </div>

            <div className="architecture-content">

                <div className="architecture-block">

                    <h3>Modules</h3>

                    {modules.length > 0 ? (
                        <div className="architecture-tags">

                            {modules.map((module) => (
                                <span
                                    className="architecture-tag"
                                    key={module}
                                >
                                    {module}
                                </span>
                            ))}

                        </div>
                    ) : (
                        <span className="architecture-empty">
                            No modules detected
                        </span>
                    )}

                </div>

                <div className="architecture-block">

                    <h3>Design Patterns</h3>

                    {designPatterns.length > 0 ? (
                        <div className="architecture-tags">

                            {designPatterns.map((pattern) => (
                                <span
                                    className="architecture-tag architecture-pattern"
                                    key={pattern}
                                >
                                    {pattern}
                                </span>
                            ))}

                        </div>
                    ) : (
                        <span className="architecture-empty">
                            No design patterns detected
                        </span>
                    )}

                </div>

            </div>

        </section>
    );
};

export default ArchitectureSummary;