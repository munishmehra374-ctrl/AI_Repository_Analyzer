import "./UploadRepository.css";

import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { cloneRepository, indexRepository } from "../../services/repositoryService";
import { useRepository } from "../../context/RepositoryContext";

const isGitUrl = (path: string): boolean => {
    const trimmed = path.trim();
    return (
        trimmed.startsWith("http://") ||
        trimmed.startsWith("https://") ||
        trimmed.startsWith("git@") ||
        trimmed.includes("github.com") ||
        trimmed.includes("gitlab.com") ||
        trimmed.includes("bitbucket.org") ||
        trimmed.endsWith(".git")
    );
};

function UploadRepository() {

    const [repositoryPath, setRepositoryPath] =
        useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [statusMessage, setStatusMessage] = useState("");

    const navigate = useNavigate();

    const {
        setTaskId,
        setRepositoryId,
    } = useRepository();

    const handleIndexRepository = async () => {
        const trimmedPath = repositoryPath.trim();

        if (!trimmedPath) {
            alert(
                "Please enter a repository path or GitHub URL."
            );
            return;
        }

        setIsLoading(true);

        try {
            let targetPath = trimmedPath;

            if (isGitUrl(trimmedPath)) {
                setStatusMessage("Cloning repository from GitHub...");
                const cloneResponse = await cloneRepository(trimmedPath);
                targetPath = cloneResponse.path;
            }

            setStatusMessage("Starting repository indexing...");

            const response =
                await indexRepository(
                    targetPath
                );

            console.log(
                "=================================="
            );

            console.log(
                "BACKEND RESPONSE:",
                response
            );

            console.log(
                "TASK ID RECEIVED:",
                response.task_id
            );

            console.log(
                "REPOSITORY ID RECEIVED:",
                response.repository_id
            );

            console.log(
                "=================================="
            );

            // Store task ID
            setTaskId(
                response.task_id
            );

            // Store repository ID
            setRepositoryId(
                response.repository_id
            );

            console.log(
                "TASK ID STORED:",
                response.task_id
            );

            console.log(
                "REPOSITORY ID STORED:",
                response.repository_id
            );

            navigate(
                "/indexing"
            );

        } catch (error: any) {

            console.error(
                error
            );

            const errorMsg =
                error?.response?.data?.detail ||
                error?.message ||
                "Failed to process repository.";

            alert(errorMsg);
        } finally {
            setIsLoading(false);
            setStatusMessage("");
        }
    };

    return (

        <div className="upload-container">

            <div className="upload-card">

                <h1>
                    AI <span>Repository</span> Analyzer
                </h1>

                <p>
                    Upload or index a GitHub repository
                    to begin AI-powered analysis.
                </p>

                <input
                    type="text"
                    placeholder="Local Folder Path or GitHub URL (https://github.com/...)"
                    value={repositoryPath}
                    disabled={isLoading}
                    onChange={(e) =>
                        setRepositoryPath(
                            e.target.value
                        )
                    }
                />

                <button
                    onClick={
                        handleIndexRepository
                    }
                    disabled={isLoading}
                >
                    {isLoading ? "Processing..." : "Index Repository"}
                </button>

                {statusMessage && (
                    <div className="upload-status">
                        {statusMessage}
                    </div>
                )}

            </div>

        </div>
    );
}

export default UploadRepository;