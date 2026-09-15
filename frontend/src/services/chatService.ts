import api from "../api/api";

import type { ChatResponse } from "../types/chat";

export async function askQuestion(
    question: string,
    generateTitle: boolean = false
): Promise<ChatResponse> {

    const taskId =
        localStorage.getItem(
            "repository_task_id"
        );

    const response = await api.post(
        "/repositories/chat",
        null,
        {
            params: {
                question,
                generate_title: generateTitle,
                task_id: taskId,
            },
        }
    );

    return response.data;
}