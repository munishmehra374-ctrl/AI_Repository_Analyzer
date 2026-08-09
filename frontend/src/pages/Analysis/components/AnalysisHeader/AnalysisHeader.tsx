import "./AnalysisHeader.css";

interface AnalysisHeaderProps {
    repositoryName: string;
    repositoryPath: string;
}

const AnalysisHeader = ({
    repositoryName,
    repositoryPath,
}: AnalysisHeaderProps) => {
    return (
        <section className="analysis-header">

            <div className="analysis-header-content">

                <h1>
                    Repository analysis
                </h1>

                <p className="analysis-header-description">
                    Structural insights derived from parsed source,
                    the knowledge graph and dependency metadata.
                </p>

                <div className="analysis-repository-info">

                    <span className="analysis-repository-name">
                        {repositoryName}
                    </span>

                    <span className="analysis-repository-separator">
                        •
                    </span>

                    <span className="analysis-repository-path">
                        {repositoryPath}
                    </span>

                </div>

            </div>

        </section>
    );
};

export default AnalysisHeader;