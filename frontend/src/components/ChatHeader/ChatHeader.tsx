import "./ChatHeader.css";

function ChatHeader() {

    return (

        <div className="chat-header">

            <div>

                <h1>

                    AI Repository Assistant

                </h1>

                <p>

                    Ask questions about your repository, architecture,
                    functions, dependencies and implementation.

                </p>

            </div>

            <button className="new-chat-btn">

                + New Chat

            </button>

        </div>

    );

}

export default ChatHeader;