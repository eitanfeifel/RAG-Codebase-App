import React, { useState, useEffect } from "react";
import ChatWindow from "../components/ChatWindow";
import "bootstrap/dist/css/bootstrap.min.css"; 
import SideBar from "../components/SideBar";
import "./ChatPage.css";

function ChatPage() {
    const [ repos, setRepos ] = useState( [] ); // Cloned repos for sidebar
    const [ loadingRepos, setLoadingRepos ] = useState( [] ); // Current repo being loaded
    const [ currentRepo, setCurrentRepo ] = useState( null ); // Active chat repo
    const [ availableRepos, setAvailableRepos ] = useState( [] ); // Repos available to clone
    const [ isCloneMenuVisible, setCloneMenuVisible ] = useState( false ); // Toggle clone menu visibility
    const [ chatHistories, setChatHistories ] = useState( {} ); // Maintain separate chat histories per repo

    // Fetch available repos when Clone Repo button is clicked
    useEffect( () => {
        if ( isCloneMenuVisible ) {
            fetch( "/repos" )
                .then( ( response ) => response.json() )
                .then( ( data) => setAvailableRepos( data ) )
                .catch( ( error ) => console.error( "Error fetching repos:", error ) );
        }
    }, [ isCloneMenuVisible ] );

    const handleRepoSelect = ( repo ) => {
        setCurrentRepo( repo ); // Set the repo as active for chat
        if ( !chatHistories[ repo ] ) {
            setChatHistories( ( prev ) => ( {
                ...prev,
                [ repo ]: [], // Initialize chat history if it doesn't exist
            } ) );
        }
    };

    const handleCloneRepo = async ( repoUrl ) => {
        const clonedRepo = repoUrl.split( "/" ).pop().replace( ".git", "" ); // Extract repo name
    
        // If the repository is already cloned or currently being loaded, return early
        if ( repos.includes( clonedRepo ) || loadingRepos.includes( clonedRepo ) ) return;
    
        // Add the repository to the list of currently loading repos
        setLoadingRepos( ( prevLoadingRepos ) => [ ...prevLoadingRepos, clonedRepo ] );
    
        try {
            const response = await fetch( "/embed", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify( { repo_url: repoUrl } ),
            } );
    
            if ( response.ok ) {
                // Successfully cloned repo, add it to repos list
                setRepos( ( prevRepos ) => [ ...prevRepos, clonedRepo ] );
            } else {
                console.error( "Failed to clone repository" );
            }
        } catch ( error ) {
            console.error( "Error cloning repository:", error );
        } finally {
            // Remove the repository from the list of currently loading repos
            setLoadingRepos( ( prevLoadingRepos ) => prevLoadingRepos.filter( ( repo ) => repo !== clonedRepo ) );
            setCloneMenuVisible( false ); // Hide clone menu
        }
    };
    

    return (
        <div className="container-fluid">
        <div className="row">
            <div className="col-md-3">
                <SideBar repos={repos} loadingRepos={loadingRepos} onRepoSelect={handleRepoSelect} />
            </div>
            <div className="col-md-9">
                <div className="chat-window">
                    {currentRepo ? (
                        <ChatWindow
                            activeRepo={currentRepo}
                            chatHistory={chatHistories[currentRepo]}
                            updateChatHistory={(newMessage) =>
                                setChatHistories((prev) => ({
                                    ...prev,
                                    [currentRepo]: [...prev[currentRepo], newMessage],
                                }))
                            }
                        />
                    ) : (
                        <p className="text-center mt-5">Select a repository to start chatting</p>
                    )}
                </div>
            </div>
        </div>
        {isCloneMenuVisible && (
            <div className="clone-menu card mt-3 p-3">
                <h4>Available Repositories</h4>
                <ul className="list-group list-group-flush">
                    {availableRepos.map((repoUrl, index) => (
                        <li key={index} className="list-group-item d-flex justify-content-between align-items-center">
                            {repoUrl.split("/").pop().replace(".git", "")}
                            <button className="btn btn-primary" onClick={() => handleCloneRepo(repoUrl)}>
                                Clone
                            </button>
                        </li>
                    ))}
                </ul>
                <button className="btn btn-secondary mt-3" onClick={() => setCloneMenuVisible(false)}>
                    Close
                </button>
            </div>
        )}
        {!isCloneMenuVisible && (
            <button
                className="btn btn-primary mt-3"
                onClick={() => setCloneMenuVisible(true)}
            >
                Clone Repo
            </button>
        )}
    </div>
);
}

export default ChatPage;
