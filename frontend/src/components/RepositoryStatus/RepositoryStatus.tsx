import "./RepositoryStatus.css";

import { useRepository } from "../../context/RepositoryContext";

function RepositoryStatus() {

    const { repositoryProfile } = useRepository();

    if (!repositoryProfile) {

        return null;

    }

    return (

        <div className="repository-status">

            <div className="status-left">

                <div className="status-icon">

                    📂

                </div>

                <div>

                    <h2>

                        {repositoryProfile.repository_name}

                    </h2>

                    <p>

                        {repositoryProfile.repository_path}

                    </p>

                </div>

            </div>


            <div className="status-right">

                <div className="status-item">

                    <span>

                        Language

                    </span>

                    <strong>

                        {repositoryProfile.languages.join(", ") || "--"}

                    </strong>

                </div>

                <div className="status-item">

                    <span>

                        Framework

                    </span>

                    <strong>

                        {repositoryProfile.frameworks.join(", ") || "--"}

                    </strong>

                </div>

                <div className="status-item">

                    <span>

                        Database

                    </span>

                    <strong>

                        {repositoryProfile.databases.join(", ") || "--"}

                    </strong>

                </div>

                <div className="status-item">

                    <span>

                        Status

                    </span>

                    <strong className="ready">

                        ● Indexed

                    </strong>

                </div>

            </div>

        </div>

    );

}

export default RepositoryStatus;