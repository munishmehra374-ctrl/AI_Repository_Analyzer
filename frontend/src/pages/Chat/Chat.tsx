import "./Chat.css";

import { useState } from "react";

import RepositoryStatus from "../../components/RepositoryStatus/RepositoryStatus";
import ChatWindow from "../../components/ChatWindow/ChatWindow";
import ChatInput from "../../components/ChatInput/ChatInput";
import ChatSidebar from "../../components/ChatSidebar/ChatSidebar";

import { useChat } from "../../hooks/useChat";
import { askQuestion } from "../../services/chatService";

function Chat() {

    const {
        chats,
        messages,
        activeChatId,
        addMessage,
        updateChatTitle,
        newChat,
        selectChat,
        deleteChat,
    } = useChat();



    const [loading, setLoading] =
        useState(false);

    const [sidebarOpen, setSidebarOpen] =
        useState(true);

    const handleSend = async (
        question: string
    ) => {

        if (!question.trim()) {
            return;
        }

        const isNewChat =
            chats.find(
                (chat) => chat.id === activeChatId
            )?.messages.length === 0;

        addMessage(
            "user",
            question
        );

        setLoading(true);

        try {

            const response =
                await askQuestion(
                    question,
                    isNewChat,
                );

            console.log("========== TITLE DEBUG ==========");
            console.log("Active Chat ID:", activeChatId);
            console.log("Is New Chat:", isNewChat);
            console.log("Generated Title:", response.title);
            console.log(
                "Active Chat:",
                chats.find(
                    (chat) => chat.id === activeChatId
                )
            );
            console.log("All Chats:", chats);
            console.log("================================");

            if (isNewChat && response.title) {
                updateChatTitle(
                    response.title
                );
            }

            addMessage(
                "assistant",
                response.answer
            );

        } catch (error) {

            console.error(
                "Chat error:",
                error
            );

            addMessage(
                "assistant",
                "Something went wrong while contacting the AI."
            );

        } finally {

            setLoading(false);

        }
    };

    const emptyChat =
        messages.length === 0 && !loading;

    return (

        <div
            className={`chat-layout ${
                sidebarOpen
                    ? "sidebar-open"
                    : "sidebar-closed"
            }`}
        >

            {sidebarOpen && (

                <ChatSidebar
                    chats={chats}
                    activeChatId={activeChatId}
                    onNewChat={newChat}
                    onSelectChat={selectChat}
                    onDeleteChat={deleteChat}
                />

            )}

            <div className="chat-page">

                <button
                    className="sidebar-toggle"
                    onClick={() =>
                        setSidebarOpen(
                            !sidebarOpen
                        )
                    }
                    aria-label={
                        sidebarOpen
                            ? "Hide sidebar"
                            : "Show sidebar"
                    }
                >
                    {sidebarOpen ? "‹" : "›"}
                </button>

                <RepositoryStatus />

                {emptyChat ? (

                    <div className="empty-chat">

                        <div className="empty-chat-content">

                            <div className="ready-message">
                                Ready when you are.
                            </div>

                            <ChatInput
                                onSend={handleSend}
                                loading={loading}
                            />

                        </div>

                    </div>

                ) : (

                    <>

                        <div className="chat-body">

                            <ChatWindow
                                messages={messages}
                                loading={loading}
                            />

                        </div>

                        <div className="chat-composer">

                            <ChatInput
                                onSend={handleSend}
                                loading={loading}
                            />

                        </div>

                    </>

                )}

            </div>

        </div>
    );
}

export default Chat;