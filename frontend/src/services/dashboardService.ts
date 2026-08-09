import api from "../api/api";

export async function getRepositoryProfile(taskId: string) {
    const response = await api.get(
        `/repositories/profile/${taskId}`
    );

    return response.data;
}