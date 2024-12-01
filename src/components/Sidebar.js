import "bootstrap/dist/css/bootstrap.min.css";
import React from "react";
import "./SideBar.css";

function SideBar({ repos, loadingRepos, onRepoSelect }) {
    return (
        <div className="sidebar border rounded p-3">
            <h3>Repositories</h3>
            <ul className="list-group">
                {repos.map((repo, index) => (
                    <li
                        key={index}
                        className="list-group-item list-group-item-action"
                        onClick={() => onRepoSelect(repo)}
                    >
                        {repo}
                    </li>
                ))}
                {loadingRepos.length > 0 && (
                    loadingRepos.map((loadingRepo, index) => (
                        <li key={`loading-${index}`} className="list-group-item list-group-item-warning">
                            {loadingRepo} <span className="spinner-border spinner-border-sm ml-2"></span>
                        </li>
                    ))
                )}
            </ul>
        </div>
    );
}

export default SideBar;
