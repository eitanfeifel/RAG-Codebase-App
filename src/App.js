import React, { useEffect, useState } from "react";
import Sidebar from "./components/Sidebar";
import ChatWindow from "./components/ChatWindow";
import RepoModal from "./components/RepoModal";
import axios from "axios";
import { BrowserRouter as Router, Route, Routes, useParams } from "react-router-dom";

function ChatPage() {
  const { repoName } = useParams();
  return <ChatWindow repoName={repoName} />;
}

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [clonedRepos, setClonedRepos] = useState([]);
  const [showRepoModal, setShowRepoModal] = useState(false);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const token = params.get("access_token");
    if (token) {
      setIsAuthenticated(true);
      window.history.replaceState({}, document.title, "/");
    }
  }, []);

  const handleCloneRepos = (repos) => {
    setClonedRepos(repos);
    setShowRepoModal(false);
  };

  return (
    <Router>
      <div style={{ display: "flex" }}>
        <Sidebar repositories={clonedRepos} onAddRepos={() => setShowRepoModal(true)} />
        <div style={{ flex: 1, padding: "20px" }}>
          <Routes>
            <Route
              path="/"
              element={<h2>Select a repository from the sidebar to start interacting.</h2>}
            />
            <Route path="/chat/:repoName" element={<ChatPage />} />
          </Routes>
        </div>
        {showRepoModal && (
          <RepoModal onCloneRepos={handleCloneRepos} onClose={() => setShowRepoModal(false)} />
        )}
      </div>
    </Router>
  );
}

export default App;
