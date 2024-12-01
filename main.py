from flask import Flask, jsonify, request, redirect, url_for, send_from_directory, session
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from pinecone import Pinecone
from flask_cors import CORS
from openai import OpenAI
from git import Repo
import requests
import esprima  
import javalang  
import hashlib
import ast
import os
import re


load_dotenv()


# Configuration:

app = Flask( __name__, static_folder = "build/static", template_folder = "build" )
app.secret_key = os.getenv( "FLASK_SECRET_KEY", "your_secret_key" )
CORS( app )

 
## Environement Keys
PINECONE_ENV = os.getenv( "PINECONE_ENV" ) 
SUPPORTED_EXTENSIONS = { '.py', '.js', '.java' } 
PINECONE_API_KEY = os.getenv( "PINECONE_API_KEY" )
GITHUB_CLIENT_ID = os.getenv( "GITHUB_CLIENT_ID" )
GITHUB_CLIENT_SECRET = os.getenv( "GITHUB_CLIENT_SECRET" )
REDIRECT_URI = os.getenv( "REDIRECT_URI", "http://127.0.0.1:5000/oauth/callback" )
IGNORED_DIRS = { '.git', 'venv','env', '.next' ,'build' , 'dist', '.vscode', 'node_modules', '__pycache__' }

##Pinecone Set up:  
index_name = "codebase-rag"
pc = Pinecone(api_key=PINECONE_API_KEY)
if index_name not in [idx.name for idx in pc.list_indexes()]:
    pc.create_index(name=index_name, dimension=768, metric="cosine")
index = pc.Index(index_name)

## Initialize embedding model
embedding_model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")
chunks_embedded = {}


#Routers:

##Home Page
@app.route( "/" )
def serve_react():
    return send_from_directory( app.template_folder, "index.html" )


##Git Hub Authorization
@app.route( "/oauth/github" )
def github_login():
    github_authorize_url = f"https://github.com/login/oauth/authorize?client_id={ GITHUB_CLIENT_ID }&redirect_uri={ REDIRECT_URI }"
    return redirect( github_authorize_url )


@app.route("/<path:path>")
def catch_all(path):
    """
    Catch-all route to serve React app for unknown routes.
    """
    return send_from_directory(app.template_folder, "index.html")


@app.route( "/oauth/callback" )
def oauth_callback():
    code = request.args.get( "code" )
    if not code:
        return "Authorization code not provided", 400
    
    token_url = "https://github.com/login/oauth/access_token"
    headers = { "Accept": "application/json" }
    data = {
        "client_id": GITHUB_CLIENT_ID,
        "client_secret": GITHUB_CLIENT_SECRET,
        "code": code,
        "redirect_uri": REDIRECT_URI,
    }
    response = requests.post( token_url, headers=headers, data=data )
    if response.status_code != 200:
        return f"Error: { response.text }", 400

    token_data = response.json()
    session[ "access_token" ] = token_data.get( "access_token" )
    return redirect( "/chat" )


##Chat Page:
@app.route( "/chat" )
def serve_chat():
    return send_from_directory( app.template_folder, "index.html" )


@app.route( "/repos", methods=[ "GET" ] )
def list_repos():
    access_token = session.get( "access_token" )
    if not access_token:
        return jsonify( { "error": "Not authenticated" } ), 403
    
    headers = { "Authorization": f"token { access_token }" }
    response = requests.get( "https://api.github.com/user/repos", headers=headers )
    if response.status_code != 200:
        return f"Error: { response.text }", 400

    repos = response.json()
    return jsonify( [ repo[ "clone_url" ] for repo in repos ] )

processed_repos = set()


##Chunking code files
def chunk_code(code, file_extension):
    if file_extension == ".py":
        return parse_python_code(code)
    elif file_extension == ".js":
        return parse_javascript_code(code)
    elif file_extension == ".java":
        return parse_java_code(code)
    elif file_extension in [".c", ".cpp"]:
        return parse_c_cpp_code(code)
    else:
        return parse_generic_code(code)

def parse_python_code(code):
    try:
        tree = ast.parse(code)
        chunks = []

        for node in tree.body:
            if isinstance(node, ast.FunctionDef):  # Functions
                chunk = ast.get_source_segment(code, node)
                chunks.append({"type": "function", "name": node.name, "content": chunk})
            elif isinstance(node, ast.ClassDef):  # Classes
                chunk = ast.get_source_segment(code, node)
                chunks.append({"type": "class", "name": node.name, "content": chunk})
            elif isinstance(node, (ast.Import, ast.ImportFrom)):  # Imports
                chunk = ast.get_source_segment(code, node)
                chunks.append({"type": "import", "content": chunk})
            else:
                chunk = ast.get_source_segment(code, node)
                if chunk:
                    chunks.append({"type": "other", "content": chunk})

        return chunks
    except Exception as e:
        print(f"Error parsing Python code: {e}")
        return []
    
def parse_javascript_code(code):
    try:
        parsed_script = esprima.parseScript(code, tolerant=True)
        chunks = []

        for node in parsed_script.body:
            if node.type == "FunctionDeclaration":
                name = node.id.name if node.id else "anonymous"
                chunks.append({"type": "function", "name": name, "content": code[node.range[0]:node.range[1]]})
            elif node.type == "ClassDeclaration":
                name = node.id.name if node.id else "anonymous"
                chunks.append({"type": "class", "name": name, "content": code[node.range[0]:node.range[1]]})
            elif node.type in ["ImportDeclaration", "VariableDeclaration"]:
                chunks.append({"type": node.type.lower(), "content": code[node.range[0]:node.range[1]]})

        return chunks
    except Exception as e:
        print(f"Error parsing JavaScript code: {e}")
        return []

def parse_java_code(code):
    try:
        tree = javalang.parse.parse(code)
        chunks = []

        for path, node in tree:
            if isinstance(node, javalang.tree.ClassDeclaration):
                chunks.append({"type": "class", "name": node.name, "content": node.to_source()})
            elif isinstance(node, javalang.tree.MethodDeclaration):
                chunks.append({"type": "method", "name": node.name, "content": node.to_source()})

        return chunks
    except Exception as e:
        print(f"Error parsing Java code: {e}")
        return []

def parse_c_cpp_code(code):
    chunks = []

    # Function Definitions
    function_pattern = re.compile(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\([^)]*\)\s*{')
    for match in function_pattern.finditer(code):
        chunks.append({"type": "function", "name": match.group(2), "content": match.group(0)})

    # Class Definitions (C++)
    class_pattern = re.compile(r'\bclass\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*{')
    for match in class_pattern.finditer(code):
        chunks.append({"type": "class", "name": match.group(1), "content": match.group(0)})

    return chunks

def parse_generic_code(code):
    chunks = []

    function_pattern = re.compile(r'\bfunction\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\([^)]*\)\s*{')
    for match in function_pattern.finditer(code):
        chunks.append( { "type": "function", "name": match.group( 1 ), "content": match.group( 0 )} )
    return chunks



##Embed code in Pinecone Vector DB
@app.route( "/embed", methods = [ "POST" ] )
def embed_repo():
    global processed_repos, chunks_embedded
    data = request.json
    repo_url = data.get( "repo_url" )
    if not repo_url:
        return jsonify( { "error": "Repo URL not provided" } ), 400

    repo_name = repo_url.split( "/" )[ -1 ]
    repo_path = os.path.join( "cloned_repos", repo_name )
    os.makedirs( "cloned_repos", exist_ok = True )

    if os.path.exists( repo_path ):
        print(f"Repository { repo_name } already exists. Skipping cloning." )
    else:
        try:
            Repo.clone_from( repo_url, repo_path )
        except Exception as e:
            return jsonify( { "error": f"Failed to clone repository: { str( e ) }" } ), 500

    index_stats = index.describe_index_stats()
    if repo_name in index_stats.get( "namespaces", {} ):
        print( f"Namespace { repo_name } already exists in Pinecone. Skipping embedding." )
        return jsonify( { "message": f"Repo { repo_name } already processed!" } )

    
    for root, dirs, files in os.walk( repo_path ):
        dirs[ : ] = [ d for d in dirs if d not in IGNORED_DIRS ]

        for file in files:
            file_extension = os.path.splitext( file )[ 1 ]
            if file_extension in SUPPORTED_EXTENSIONS:
                file_path = os.path.join( root, file )
                try:
                    with open( file_path, "r", encoding="utf-8" ) as f:
                        content = f.read()
                        chunks = chunk_code( content, file_extension )

                        for chunk in chunks:
                            embedding = embedding_model.encode( chunk[ "content" ] )
                            metadata = {
                                "repo": repo_name,
                                "file": file,
                                "content": chunk[ "content" ],  # Include chunk content
                            }

                            # Create a unique ID based on repo, file, and chunk
                            chunk_hash = hashlib.sha256(chunk[ 'content' ].encode( 'utf-8' ) ).hexdigest()[ :10 ]
                            chunk_id = f"{ repo_name }:{ file }:{ chunk_hash }"
                            namespace = repo_name.split( '.' )[ 0 ]
                            index.upsert( [ ( chunk_id, embedding.tolist(), metadata ) ] ,namespace = namespace )
                            print( f"Upserting chunk with ID: { chunk_id }, Content: { chunk[ 'content' ][ :100 ] }" )
                            chunks_embedded[ chunk_id ] = chunk[ 'content' ]

                except Exception as e:
                    print(f"Error processing file {file}: {e}")

    processed_repos.add(repo_name)
    return jsonify({"message": f"Repo {repo_name} embedded successfully!"})


##Chat with LLM
@app.route( "/chat", methods=[ "POST" ] )
def chat():
    global chunks_embedded
    data = request.json
    query = data.get( "query" )
    repo = data.get( "repo" )
    client = OpenAI()
    chat_history = data.get( "chat_history", [] )  # Fetch the chat history

    if not query or not repo:
        return jsonify( { "error": "Query or repo not provided" } ), 400
    
    query_embedding = embedding_model.encode( query ).tolist()
    try:
        response = index.query(
            vector = query_embedding,
            top_k = 10,
            include_metadata = True,
            namespace=repo.split( '.' )[ 0 ]
        )

        # # Debugging: Print the entire response from Pinecone
        # print("Pinecone Response:", response)

        # Extract relevant context from response
        contexts = []
        for result in response[ "matches" ]:
            contexts.append( result[ 'metadata' ][ 'content' ] + '\n' + result[ 'metadata' ][ 'file' ] )
        context_text = "\n".join( contexts )

        # # Debugging: Print the final context used in conversation
        # print("Final Context for Conversation:", context_text)

        # Build the conversation with chat history
        conversation = [
            { "role": "system", "content": "You are an expert code reviewer, assisting a user with questions about their codebase. Answer the user as best you can using the given context. Do your best to direct the user to the chunks of code you are referring to in your answers and what files they are located in" }
        ]
        conversation.append( { "role": "user", "content": f"Relevant context:\n{ context_text }\n\nQuestion: { query }" } )
        # Append previous chat history to the conversation
        for message in chat_history:
            role = "user" if message["user"] == "You" else "assistant"
            conversation.append( { "role": role, "content": message[ "text" ] } )

        

        # # Debugging: Print the conversation to be sent to OpenAI
        # print("Conversation Sent to OpenAI:", conversation)

        openai_response = client.chat.completions.create(
            model = "gpt-4o", 
            messages = conversation
        )
        answer = openai_response.choices[ 0 ].message.content.strip()

        # # Debugging: Print the assistant's response
        # print("Assistant's Response:", answer)

        return jsonify( { "answer": answer } )

    except Exception as e:
        # Debugging: Print any errors that occur
        print( f"Error during chat processing: {  e }" )
        return jsonify( { "error": "Failed to process the query" } ), 500


if __name__ == "__main__":
    app.run( debug = True )
