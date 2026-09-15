import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import {
    Prism as SyntaxHighlighter
} from "react-syntax-highlighter";
import {
    oneDark
} from "react-syntax-highlighter/dist/esm/styles/prism";

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

            {/* =========================================
                MESSAGE CONTENT
               ========================================= */}

            <div className="message-bubble">

                {sender === "assistant" ? (

                    <ReactMarkdown
                        remarkPlugins={[remarkGfm]}
                        components={{
                            code({
                                className,
                                children,
                                ref: _ref,
                                ...props
                            }) {

                                const match =
                                    /language-(\w+)/.exec(
                                        className || ""
                                    );

                                return match ? (

                                    <SyntaxHighlighter
                                        style={oneDark as any}
                                        language={match[1]}
                                        PreTag="div"
                                        {...props}
                                    >
                                        {String(children).replace(
                                            /\n$/,
                                            ""
                                        )}
                                    </SyntaxHighlighter>

                                ) : (

                                    <code
                                        className={className}
                                        {...props}
                                    >
                                        {children}
                                    </code>

                                );
                            },
                        }}
                    >
                        {message}
                    </ReactMarkdown>

                ) : (

                    message

                )}

            </div>

        </div>
    );
}

export default ChatMessage;