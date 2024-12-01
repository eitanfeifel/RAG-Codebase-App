import React from "react";
import "./ChatWindow.css";

const ChatWindow = () => {
  return (
    <div className="chat-window">
      <h2>Repository Chat</h2>
      <div className="chat-area"></div>
      <div className="chat-input">
        <input type="text" placeholder="Type your message..." />
        <button>Send</button>
      </div>
    </div>
  );
};

export default ChatWindow;
