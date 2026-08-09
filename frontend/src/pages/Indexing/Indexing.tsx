import "./Indexing.css";

import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { getProgress } from "../../services/repositoryService";
import { useRepository } from "../../context/RepositoryContext";

function Indexing() {

    const navigate = useNavigate();

    const {
        taskId,
    } = useRepository();

    console.log("==================================");
    console.log("INDEXING PAGE LOADED");
    console.log("TASK ID FROM CONTEXT:", taskId);
    console.log("==================================");

    const [progress, setProgress] = useState(0);

    const [stage, setStage] = useState("Queued");

    const [status, setStatus] = useState("STARTED");

    const [currentFile, setCurrentFile] = useState("");

    const [filesProcessed, setFilesProcessed] = useState(0);

    const [totalFiles, setTotalFiles] = useState(0);

    useEffect(() => {

        console.log("STARTING POLL FOR TASK:", taskId);

        if (!taskId) {

            console.log("NO TASK ID FOUND");

            navigate("/");

            return;

        }

        const interval = setInterval(async () => {

            try {

                console.log("REQUESTING PROGRESS:", taskId);

                const response = await getProgress(taskId);

                console.log("PROGRESS RESPONSE:", response);

                setProgress(Number(response.progress || 0));

                setStage(response.stage || "");

                setStatus(response.status || "");

                setCurrentFile(response.current_file || "");

                setFilesProcessed(
                    Number(response.files_processed || 0)
                );

                setTotalFiles(
                    Number(response.total_files || 0)
                );

                if (response.status === "SUCCESS") {

                    console.log("INDEXING COMPLETED");

                    clearInterval(interval);

                    setTimeout(() => {

                        navigate("/dashboard");

                    }, 1000);

                }

                if (response.status === "FAILED") {

                    console.log("INDEXING FAILED");

                    clearInterval(interval);

                    alert("Repository indexing failed.");

                }

            } catch (error) {

                console.error(error);

            }

        }, 1000);

        return () => clearInterval(interval);

    }, [taskId, navigate]);

    return (

        <div className="indexing-page">

            <div className="indexing-card">

                <h1>
                    Repository Indexing
                </h1>

                <p>
                    Preparing your repository for AI analysis...
                </p>

                <div className="progress-bar">

                    <div
                        className="progress-fill"
                        style={{
                            width: `${progress}%`,
                        }}
                    />

                </div>

                <h2>{progress}%</h2>

                <div className="info-grid">

                    <div className="info-card">

                        <span>Stage</span>

                        <strong>{stage}</strong>

                    </div>

                    <div className="info-card">

                        <span>Status</span>

                        <strong>{status}</strong>

                    </div>

                    <div className="info-card">

                        <span>Current File</span>

                        <strong>{currentFile || "--"}</strong>

                    </div>

                    <div className="info-card">

                        <span>Files</span>

                        <strong>{filesProcessed} / {totalFiles}</strong>

                    </div>

                </div>

            </div>

        </div>

    );
}

export default Indexing;