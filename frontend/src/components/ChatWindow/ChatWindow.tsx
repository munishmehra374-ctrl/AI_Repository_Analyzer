import "./ChatWindow.css";

import ChatMessage from "../ChatMessage/ChatMessage";

import type { Message } from "../../types/chat";

interface Props {
    messages: Message[];
    loading: boolean;
}

function ChatWindow({ messages, loading }: Props) {
    return (
        <div className="chat-window">

            {messages.length === 0 && !loading && (
                <div className="ready-message">
                    Ready when you are.
                </div>
            )}

            {messages.map((message, index) => (
                <ChatMessage
                    key={index}
                    sender={message.sender}
                    message={message.message}
                />
            ))}

            {loading && (
                <ChatMessage
                    sender="assistant"
                    message="Thinking..."
                />
            )}

        </div>
    );
}

export default ChatWindow;