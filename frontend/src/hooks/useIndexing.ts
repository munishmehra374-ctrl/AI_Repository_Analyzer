import { useState } from "react";

import {
    indexRepository,
    getProgress,
} from "../services/repositoryService";


export const useIndexing = () => {

    const [taskId, setTaskId] =
        useState<string | null>(null);

    const [progress, setProgress] =
        useState<any>(null);

    const [loading, setLoading] =
        useState(false);

    const [error, setError] =
        useState<string | null>(null);


    const startIndexing = async (
        repositoryPath: string
    ) => {

        try {

            setLoading(true);
            setError(null);


            // =========================================
            // Start Repository Indexing
            // =========================================

            const response =
                await indexRepository(
                    repositoryPath
                );


            // =========================================
            // Get Task ID
            // =========================================

            const newTaskId =
                response.task_id;


            if (!newTaskId) {

                throw new Error(
                    "Task ID was not returned by the backend."
                );

            }


            // =========================================
            // Store Task ID
            // =========================================

            localStorage.setItem(
                "task_id",
                newTaskId
            );


            setTaskId(
                newTaskId
            );


            return newTaskId;

        } catch (err) {

            console.error(
                "Indexing failed:",
                err
            );

            setError(
                "Failed to start repository indexing."
            );

            throw err;

        } finally {

            setLoading(false);

        }
    };


    const fetchProgress = async (
        id: string
    ) => {

        try {

            const data =
                await getProgress(
                    id
                );

            setProgress(
                data
            );

            return data;

        } catch (err) {

            console.error(
                "Failed to fetch indexing progress:",
                err
            );

            return null;

        }
    };


    return {
        taskId,
        progress,
        loading,
        error,
        startIndexing,
        fetchProgress,
    };
};