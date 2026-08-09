import "./RepositoryProfile.css";

interface RepositoryProfileProps {
    repositoryName: string;
    repositoryPath: string;
    modules: string[];
    designPatterns: string[];
}

const RepositoryProfile = ({
    repositoryName,
    repositoryPath,
    modules,
    designPatterns,
}: RepositoryProfileProps) => {
    return (
        <section className="repository-profile">

            <div className="repository-profile-header">
                <h2>Repository Profile</h2>

                <p>
                    High-level information extracted from the repository.
                </p>
            </div>

            <div className="repository-profile-grid">

                <div className="repository-profile-item">
                    <span className="repository-profile-label">
                        Repository
                    </span>

                    <span className="repository-profile-value">
                        {repositoryName}
                    </span>
                </div>

                <div className="repository-profile-item">
                    <span className="repository-profile-label">
                        Repository Path
                    </span>

                    <span className="repository-profile-value repository-path">
                        {repositoryPath}
                    </span>
                </div>

                <div className="repository-profile-item">
                    <span className="repository-profile-label">
                        Modules
                    </span>

                    <span className="repository-profile-value">
                        {modules.length.toLocaleString()}
                    </span>
                </div>

                <div className="repository-profile-item">
                    <span className="repository-profile-label">
                        Design Patterns
                    </span>

                    <span className="repository-profile-value">
                        {designPatterns.length.toLocaleString()}
                    </span>
                </div>

            </div>

        </section>
    );
};

export default RepositoryProfile;