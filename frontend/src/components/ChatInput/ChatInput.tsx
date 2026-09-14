import "./ChatInput.css";

import { useState } from "react";

interface Props {
    onSend: (
        question: string
    ) => void | Promise<void>;

    loading: boolean;
}

function ChatInput({
    onSend,
    loading,
}: Props) {

    const [question, setQuestion] = useState("");

    async function handleSend() {

        if (!question.trim()) return;

        await onSend(question);

        setQuestion("");
    }

    return (
        <div className="chat-input-container">

            <textarea
                rows={1}
                placeholder="Ask anything"
                value={question}
                disabled={loading}
                onChange={(e) =>
                    setQuestion(e.target.value)
                }
                onKeyDown={async (e) => {

                    if (
                        e.key === "Enter" &&
                        !e.shiftKey
                    ) {

                        e.preventDefault();

                        await handleSend();
                    }

                }}
            />

            <button
                onClick={handleSend}
                disabled={loading}
            >
                {loading ? "..." : "↑"}
            </button>

        </div>
    );
}

export default ChatInput;