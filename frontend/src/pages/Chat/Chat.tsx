import "./Chat.css";

import { useState } from "react";

import ChatHeader from "../../components/ChatHeader/ChatHeader";
import RepositoryStatus from "../../components/RepositoryStatus/RepositoryStatus";
import SuggestedQuestions from "../../components/SuggestedQuestions/SuggestedQuestions";
import ChatWindow from "../../components/ChatWindow/ChatWindow";
import ChatInput from "../../components/ChatInput/ChatInput";

import { askQuestion } from "../../services/chatService";

import type { Message } from "../../types/chat";

function Chat() {

    const [messages, setMessages] = useState<Message[]>([
        {
            sender: "assistant",
            message:
                "👋 Welcome! Your repository has been indexed successfully.\n\nAsk me anything about your project.",
        },
    ]);

    const [loading, setLoading] = useState(false);

    const handleSend = async (question: string) => {

        if (!question.trim()) return;

        setMessages((previous) => [
            ...previous,
            {
                sender: "user",
                message: question,
            },
        ]);

        setLoading(true);

        try {

            const response = await askQuestion(question);

            setMessages((previous) => [
                ...previous,
                {
                    sender: "assistant",
                    message: response.answer,
                },
            ]);

        } catch (error) {

            console.error(error);

            setMessages((previous) => [
                ...previous,
                {
                    sender: "assistant",
                    message: "Something went wrong while contacting the AI.",
                },
            ]);

        } finally {

            setLoading(false);

        }

    };

    return (

        <div className="chat-page">

            <ChatHeader />

            <RepositoryStatus />

            <SuggestedQuestions
                onSelect={handleSend}
            />

            <ChatWindow
                messages={messages}
                loading={loading}
            />

            <ChatInput
                onSend={handleSend}
                loading={loading}
            />

        </div>

    );

}

export default Chat;