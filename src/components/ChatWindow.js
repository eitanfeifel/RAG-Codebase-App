import "bootstrap/dist/css/bootstrap.min.css";
import React, { useState } from "react";
import "./ChatWindow.css";

function ChatWindow({ activeRepo, chatHistory, updateChatHistory }) {
    const [ input, setInput ] = useState( "" );
    const [ loading, setLoading ] = useState( false ); // For indicating the bot is processing

    const handleSend = async () => {
        if ( !input.trim() ) return;
    
        const newMessage = { user: "You", text: input };
    
        // Update chat history with user's message
        updateChatHistory( newMessage );
    
        // Send query to backend with chat history
        try {
            const response = await fetch( "/chat", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify( {
                    query: input,
                    repo: activeRepo,
                    chat_history: chatHistory, // Include chat history
                } ),
            } );
    
            if ( response.ok ) {
                const data = await response.json();
                updateChatHistory( { user: "Bot", text: data.answer } );
            } else {
                console.error( "Failed to get a response from the server" );
            }
        } catch ( error ) {
            console.error("Error during chat:", error);
        }
    
        setInput( "" ); // Clear input field
    };    

    return (
        <div className="chat-window border rounded p-3">
            <div className="messages mb-3">
                {chatHistory.map((msg, index) => (
                    <div key={index} className={`alert ${msg.user === "You" ? "alert-primary" : "alert-secondary"}`}>
                        <strong>{msg.user}: </strong> {msg.text}
                    </div>
                ))}
                {loading && (
                    <div className="alert alert-secondary">
                        <strong>Bot: </strong> Typing...
                    </div>
                )}
            </div>
            <div className="input-group">
                <input
                    type="text"
                    className="form-control"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder={`Ask a question about ${activeRepo}`}
                />
                <button className="btn btn-primary" onClick={handleSend}>
                    Send
                </button>
            </div>
        </div>
    );
}

export default ChatWindow;
