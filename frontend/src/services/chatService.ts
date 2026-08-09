import api from "../api/api";

import type{ ChatResponse } from "../types/chat";

export async function askQuestion(
    question: string
): Promise<ChatResponse> {

    const response = await api.post(
        "/repositories/chat",
        null,
        {
            params: {
                question,
            },
        }
    );

    return response.data;

}