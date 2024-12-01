import React, { useState } from "react";
import "./RepoModal.css";

function RepoModal({ githubRepos, onCloneRepos, onClose }) {
  const [selectedRepos, setSelectedRepos] = useState([]);

  const toggleRepo = (repo) => {
    setSelectedRepos((prev) =>
      prev.includes(repo) ? prev.filter((r) => r !== repo) : [...prev, repo]
    );
  };

  return (
    <div className="modal">
      <div className="modal-content">
        <h2>Select Repositories to Clone</h2>
        <ul>
          {githubRepos.map((repo, index) => (
            <li key={index}>
              <label>
                <input
                  type="checkbox"
                  onChange={() => toggleRepo(repo)}
                  checked={selectedRepos.includes(repo)}
                />
                {repo}
              </label>
            </li>
          ))}
        </ul>
        <button className="modal-button" onClick={() => onCloneRepos(selectedRepos)}>
          Clone Repositories
        </button>
        <button className="modal-button" onClick={onClose}>
          Cancel
        </button>
      </div>
    </div>
  );
}

export default RepoModal;
