import { useEffect, useState } from "react";

export interface ChatMessage {
    sender: "user" | "assistant";
    message: string;
}

export interface Chat {
    id: string;
    title: string;
    messages: ChatMessage[];
}

const STORAGE_KEY = "ai_repository_chats";

const createInitialChat = (): Chat => ({
    id: Date.now().toString(),

    title: "New Chat",

    messages: [],
});

export function useChat() {

    // =====================================================
    // LOAD CHATS
    // =====================================================

    const [chats, setChats] = useState<Chat[]>(() => {

        const saved =
            localStorage.getItem(STORAGE_KEY);

        if (saved) {

            try {

                const parsed = JSON.parse(saved);

                if (
                    Array.isArray(parsed) &&
                    parsed.length > 0
                ) {
                    return parsed;
                }

            } catch {
                // Ignore invalid saved data
            }
        }

        return [createInitialChat()];
    });


    // =====================================================
    // ACTIVE CHAT
    // =====================================================

    const [activeChatId, setActiveChatId] =
        useState<string>(() => {

            const saved =
                localStorage.getItem(STORAGE_KEY);

            if (saved) {

                try {

                    const parsed = JSON.parse(saved);

                    if (
                        Array.isArray(parsed) &&
                        parsed.length > 0
                    ) {
                        return parsed[0].id;
                    }

                } catch {
                    // Ignore invalid data
                }
            }

            return "";
        });


    // =====================================================
    // SAVE CHATS
    // =====================================================

    useEffect(() => {

        localStorage.setItem(
            STORAGE_KEY,
            JSON.stringify(chats)
        );

    }, [chats]);


    // =====================================================
    // CURRENT CHAT
    // =====================================================

    const activeChat =
        chats.find(
            (chat) =>
                chat.id === activeChatId
        ) || chats[0];


    // =====================================================
    // ADD MESSAGE
    // =====================================================

    const addMessage = (
        sender: "user" | "assistant",
        message: string
    ) => {

        if (!activeChat) {
            return;
        }

        setChats((previous) =>

            previous.map((chat) => {

                if (chat.id !== activeChat.id) {
                    return chat;
                }

                return {
                    ...chat,

                    messages: [
                        ...chat.messages,
                        {
                            sender,
                            message,
                        },
                    ],
                };

            })

        );
    };


    // =====================================================
    // UPDATE CHAT TITLE
    // =====================================================

    const updateChatTitle = (
        title: string
    ) => {

        if (
            !activeChat ||
            !title.trim()
        ) {
            return;
        }

        setChats((previous) =>

            previous.map((chat) => {

                if (
                    chat.id !== activeChat.id
                ) {
                    return chat;
                }

                return {
                    ...chat,

                    title: title.trim(),
                };

            })

        );
    };


    // =====================================================
    // NEW CHAT
    // =====================================================

    const newChat = () => {

        /*
         * If the current chat is already empty,
         * do not create another empty chat.
         */

        if (
            activeChat &&
            activeChat.messages.length === 0
        ) {
            return;
        }

        const chat = createInitialChat();

        setChats((previous) => [
            chat,
            ...previous,
        ]);

        setActiveChatId(chat.id);
    };


    // =====================================================
    // SELECT CHAT
    // =====================================================

    const selectChat = (id: string) => {

        setActiveChatId(id);

    };


    // =====================================================
    // DELETE CHAT
    // =====================================================

    const deleteChat = (id: string) => {

        setChats((previous) => {

            const remaining =
                previous.filter(
                    (chat) =>
                        chat.id !== id
                );

            if (remaining.length === 0) {

                const freshChat =
                    createInitialChat();

                setActiveChatId(
                    freshChat.id
                );

                return [freshChat];
            }

            if (id === activeChatId) {

                setActiveChatId(
                    remaining[0].id
                );
            }

            return remaining;
        });
    };


    // =====================================================
    // CLEAR CURRENT CHAT
    // =====================================================

    const clearMessages = () => {

        if (!activeChat) {
            return;
        }

        setChats((previous) =>

            previous.map((chat) => {

                if (
                    chat.id !== activeChat.id
                ) {
                    return chat;
                }

                return {
                    ...chat,

                    title: "New Chat",

                    messages: [],
                };

            })

        );
    };


    return {

        chats,

        activeChatId,

        messages:
            activeChat?.messages || [],

        addMessage,

        updateChatTitle,

        newChat,

        selectChat,

        deleteChat,

        clearMessages,
    };
}