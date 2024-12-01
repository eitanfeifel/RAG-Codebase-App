from flask import Flask, request, redirect, jsonify, send_from_directory
from dotenv import load_dotenv
from flask_cors import CORS
import os
import requests

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder="build", static_url_path="/")
CORS(app)

# Disable caching of static files during development
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# GitHub OAuth credentials
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")

@app.route("/")
def serve_react():
    """Serve React Frontend."""
    return app.send_static_file("index.html")

@app.route('/auth/github')
def github_login():
    redirect_uri = "http://localhost:5000/auth/github/callback"
    github_url = f"https://github.com/login/oauth/authorize?client_id={GITHUB_CLIENT_ID}&redirect_uri={redirect_uri}&scope=repo"
    return redirect(github_url)

@app.route("/auth/github")
def github_login():
    """Redirect the user to GitHub OAuth login."""
    redirect_uri = "http://127.0.0.1:5000/auth/github/callback"
    github_url = (
        f"https://github.com/login/oauth/authorize?client_id={GITHUB_CLIENT_ID}"
        f"&redirect_uri={redirect_uri}&scope=repo"
    )
    return redirect(github_url)

@app.route("/auth/github/callback")
def github_callback():
    """Handle GitHub OAuth callback."""
    code = request.args.get("code")
    token_url = "https://github.com/login/oauth/access_token"
    headers = {"Accept": "application/json"}
    payload = {
        "client_id": GITHUB_CLIENT_ID,
        "client_secret": GITHUB_CLIENT_SECRET,
        "code": code,
    }

    response = requests.post(token_url, headers=headers, json=payload)

    # Check for errors
    if response.status_code != 200:
        return "GitHub authentication failed.", 400

    access_token = response.json().get("access_token")
    if access_token:
        return redirect(f"http://127.0.0.1:5000?access_token={access_token}")
    return "Authorization failed", 400

@app.route("/list-github-repos", methods=["POST"])
def list_github_repos():
    """List the authenticated user's GitHub repositories."""
    access_token = request.json.get("access_token")
    if not access_token:
        return jsonify({"error": "Access token is required"}), 400

    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get("https://api.github.com/user/repos", headers=headers)

    # Check for errors
    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch repositories"}), response.status_code

    repos = [repo["name"] for repo in response.json()]
    return jsonify({"repositories": repos})

@app.errorhandler(404)
def not_found(e):
    """Handle unknown routes and serve React app."""
    return app.send_static_file("index.html")

if __name__ == "__main__":
    app.run(debug=True)