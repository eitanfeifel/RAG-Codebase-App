import { useNavigate } from "react-router-dom";
import "bootstrap/dist/css/bootstrap.min.css";
import React from "react";
import "./HomePage.css";


function HomePage() {
    const navigate = useNavigate();

    const connectToGitHub = () => {
        window.location.href = "/oauth/github";
    };

    return (
        <div className="container d-flex align-items-center justify-content-center vh-100">
        <div className="text-center p-5 border rounded shadow-lg">
          <h1 className="mb-4">Welcome to Codebase RAG</h1>
          <p className="mb-4">Connect your GitHub to get started.</p>
          <button
            className="btn btn-primary btn-lg"
            onClick={connectToGitHub}
          >
            Connect to GitHub
          </button>
        </div>
      </div>
    );
}

export default HomePage;
