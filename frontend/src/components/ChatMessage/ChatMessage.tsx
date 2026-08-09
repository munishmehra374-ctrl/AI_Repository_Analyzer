import "./ChatMessage.css";

interface Props {

    sender: "user" | "assistant";

    message: string;

}

function ChatMessage({

    sender,

    message,

}: Props) {

    return (

        <div className={`chat-message ${sender}`}>

            <div className="avatar">

                {sender === "assistant" ? "AI" : "You"}

            </div>

            <div className="message-bubble">

                {message}

            </div>

        </div>

    );

}

export default ChatMessage;