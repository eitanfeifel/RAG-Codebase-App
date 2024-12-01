import React, { useEffect, useState } from "react";
import Sidebar from "./components/Sidebar";
import ChatWindow from "./components/ChatWindow";
import RepoModal from "./components/RepoModal";
import axios from "axios";
import { BrowserRouter as Router, Route, Routes, useNavigate } from "react-router-dom";

function ConnectGitHub() {
  const handleConnect = () => {
    window.location.href = "http://127.0.0.1:5000/auth/github";
  };

  return (
    <div className="connect-page">
      <h1>Welcome to the GitHub Chat App</h1>
      <p>Connect your GitHub account to get started.</p>
      <button className="modern-button connect-button" onClick={handleConnect}>
        Connect to GitHub
      </button>
    </div>
  );
}

function CloneReposPage({ onCloneComplete }) {
  const [repositories, setRepositories] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const token = params.get("access_token");

    if (token) {
      axios
        .post("http://127.0.0.1:5000/list-github-repos", { access_token: token })
        .then((response) => setRepositories(response.data.repositories))
        .catch((error) => console.error("Error fetching GitHub repositories:", error));
    }
  }, []);

  const handleClone = () => {
    const selectedRepos = Array.from(
      document.querySelectorAll('input[type="checkbox"]:checked')
    ).map((checkbox) => checkbox.value);

    onCloneComplete(selectedRepos);
    navigate("/chat");
  };

  return (
    <div className="clone-repos-page">
      <h2>Select Repositories to Clone</h2>
      <ul className="repo-list">
        {repositories.map((repo, index) => (
          <li key={index}>
            <input type="checkbox" id={`repo-${index}`} value={repo} />
            <label htmlFor={`repo-${index}`}>{repo}</label>
          </li>
        ))}
      </ul>
      <button className="modern-button" onClick={handleClone}>
        Clone Selected Repositories
      </button>
    </div>
  );
}

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [clonedRepos, setClonedRepos] = useState([]);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const token = params.get("access_token");

    if (token) {
      setIsAuthenticated(true);
      window.history.replaceState({}, document.title, "/clone-repos");
    }
  }, []);

  return (
    <Router>
      <div style={{ display: "flex", height: "100vh" }}>
        {isAuthenticated && <Sidebar repositories={clonedRepos} />}
        <div style={{ flex: 1, padding: "20px" }}>
          <Routes>
            {!isAuthenticated ? (
              <Route path="*" element={<ConnectGitHub />} />
            ) : (
              <>
                <Route
                  path="/clone-repos"
                  element={<CloneReposPage onCloneComplete={setClonedRepos} />}
                />
                <Route path="/chat/:repoName" element={<ChatWindow />} />
              </>
            )}
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;