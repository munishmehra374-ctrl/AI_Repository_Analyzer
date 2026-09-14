import "./ChatSidebar.css";

interface ChatItem {
    id: string;
    title: string;
}

interface Props {
    chats: ChatItem[];
    activeChatId: string;
    onNewChat: () => void;
    onSelectChat: (id: string) => void;
    onDeleteChat: (id: string) => void;
}

function ChatSidebar({
    chats,
    activeChatId,
    onNewChat,
    onSelectChat,
    onDeleteChat,
}: Props) {

    return (
        <aside className="chat-sidebar">

            <button
                className="new-chat-button"
                onClick={onNewChat}
            >
                <span className="new-chat-icon">
                    +
                </span>

                <span>
                    New Chat
                </span>
            </button>


            <div className="chat-history">

                <div className="history-title">
                    Chats
                </div>

                {chats.length === 0 ? (

                    <div className="no-chats">
                        No previous chats
                    </div>

                ) : (

                    chats.map((chat) => (

                        <div
                            key={chat.id}
                            className={`chat-history-wrapper ${
                                chat.id === activeChatId
                                    ? "active"
                                    : ""
                            }`}
                        >

                            <button
                                className="chat-history-item"
                                onClick={() =>
                                    onSelectChat(chat.id)
                                }
                            >
                                <span className="chat-title">
                                    {chat.title}
                                </span>
                            </button>

                            <button
                                className="delete-chat-button"
                                onClick={(e) => {
                                    e.stopPropagation();
                                    onDeleteChat(chat.id);
                                }}
                                aria-label="Delete chat"
                            >
                                ×
                            </button>

                        </div>

                    ))

                )}

            </div>

        </aside>
    );
}

export default ChatSidebar;