import React, { useEffect } from "react";

function Sidebar({ repositories, onRepoSelect }) {
  // Log updates to repositories (for debugging purposes)
  useEffect(() => {
    console.log("Repositories updated in Sidebar:", repositories);
  }, [repositories]);

  return (
    <div className="sidebar">
      <h3>Cloned Repositories</h3>
      <ul className="repo-list">
        {repositories.map((repo, index) => (
          <li
            key={index}
            onClick={() => onRepoSelect(repo)}
            className="repo-item"
          >
            {repo}
          </li>
        ))}
      </ul>
      <button className="clone-button" onClick={() => window.location.reload()}>
        Clone More Repositories
      </button>
    </div>
  );
}

export default Sidebar;
