import api from "../api/api";

export const indexRepository = async (
    repositoryPath: string
) => {

    const response = await api.post(
        "/repositories/index",
        null,
        {
            params: {
                file_path: repositoryPath,
            },
        }
    );

    return response.data;
};


export const getProgress = async (
    taskId: string
) => {

    const response = await api.get(
        `/repositories/progress/${taskId}`
    );

    return response.data;
};


export const getRepositoryProfile = async (
    taskId: string
) => {

    const response = await api.get(
        `/repositories/profile/${taskId}`
    );

    return response.data;
};

export const getGraphStatistics = async () => {
    const response = await api.get(
        "/repositories/graph/statistics"
    );

    return response.data;
};

export const getDependencyGraph = async () => {

    const response = await api.get(
        "/repositories/graph/dependencies"
    );

    return response.data;
};