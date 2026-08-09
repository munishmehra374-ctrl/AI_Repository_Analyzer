import "./UploadRepository.css";

import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { indexRepository } from "../../services/repositoryService";
import { useRepository } from "../../context/RepositoryContext";


function UploadRepository() {

    const [repositoryPath, setRepositoryPath] =
        useState("");

    const navigate = useNavigate();

    const {
        setTaskId,
    } = useRepository();


    const handleIndexRepository = async () => {

        if (!repositoryPath.trim()) {

            alert(
                "Please enter a repository path."
            );

            return;
        }


        try {

            const response =
                await indexRepository(
                    repositoryPath
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
                "=================================="
            );


            // =========================================
            // Store Task ID in React Context
            // =========================================

            setTaskId(
                response.task_id
            );


            // =========================================
            // Store Task ID in Local Storage
            // =========================================

            localStorage.setItem(
                "task_id",
                response.task_id
            );


            console.log(
                "TASK ID STORED:",
                localStorage.getItem(
                    "task_id"
                )
            );


            // =========================================
            // Go to Indexing Page
            // =========================================

            navigate(
                "/indexing"
            );

        } catch (error) {

            console.error(
                error
            );

            alert(
                "Failed to start indexing."
            );

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
                    placeholder="Repository Path"
                    value={
                        repositoryPath
                    }
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
                >
                    Index Repository
                </button>

            </div>

        </div>

    );
}


export default UploadRepository;