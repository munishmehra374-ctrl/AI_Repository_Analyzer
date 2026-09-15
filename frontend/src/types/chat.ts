export interface Message {
    sender: "user" | "assistant";
    message: string;
}

export interface ChatResponse {
    answer: string;
    title?: string;
}