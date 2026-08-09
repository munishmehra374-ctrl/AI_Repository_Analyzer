import "./KnowledgeGraphSummary.css";

interface KnowledgeGraphSummaryProps {
    files: number;
    classes: number;
    functions: number;
    relationships: number;
}

const KnowledgeGraphSummary = ({
    files,
    classes,
    functions,
    relationships,
}: KnowledgeGraphSummaryProps) => {

    const items = [
        {
            label: "Files",
            value: files,
        },
        {
            label: "Classes",
            value: classes,
        },
        {
            label: "Functions",
            value: functions,
        },
        {
            label: "Relationships",
            value: relationships,
        },
    ];

    return (
        <section className="knowledge-graph-summary">

            <div className="knowledge-graph-header">

                <div>
                    <span className="knowledge-graph-eyebrow">
                        CODE INTELLIGENCE
                    </span>

                    <h2>
                        Knowledge Graph
                    </h2>

                    <p>
                        Structural entities and relationships
                        extracted from the repository.
                    </p>
                </div>

                <div className="knowledge-graph-status">
                    <span className="knowledge-graph-status-dot" />
                    Graph Indexed
                </div>

            </div>

            <div className="knowledge-graph-grid">

                {items.map((item) => (

                    <div
                        className="knowledge-graph-card"
                        key={item.label}
                    >

                        <span className="knowledge-graph-label">
                            {item.label}
                        </span>

                        <span className="knowledge-graph-value">
                            {item.value.toLocaleString()}
                        </span>

                    </div>

                ))}

            </div>

            <div className="knowledge-graph-footer">

                <span>
                    Repository entities and relationships
                    are available for dependency analysis,
                    call tracing and structural queries.
                </span>

            </div>

        </section>
    );
};

export default KnowledgeGraphSummary;