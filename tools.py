import os
from github import Github
import requests
from pydantic import BaseModel, Field

def create_github_repo(repo_name: str, description: str, private: bool) -> str:
    """Creates a new GitHub repository. private should be True or False."""
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        return "Error: GITHUB_TOKEN environment variable not set."
    
    try:
        g = Github(token)
        user = g.get_user()
        repo = user.create_repo(name=repo_name, description=description, private=private)
        return f"Successfully created repository: {repo.html_url}"
    except Exception as e:
        return f"Failed to create repository: {str(e)}"


def push_file_to_github(repo_name: str, file_path: str, content: str, commit_message: str) -> str:
    """Pushes a file with content to a specific GitHub repository."""
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        return "Error: GITHUB_TOKEN environment variable not set."
        
    try:
        g = Github(token)
        user = g.get_user()
        repo = user.get_repo(repo_name)
        
        try:
            # Check if file exists to update it
            contents = repo.get_contents(file_path)
            repo.update_file(contents.path, commit_message, content, contents.sha)
            return f"Successfully updated {file_path} in {repo_name}."
        except Exception:
            # File doesn't exist, create it
            repo.create_file(file_path, commit_message, content)
            return f"Successfully created {file_path} in {repo_name}."
            
    except Exception as e:
        return f"Failed to push file: {str(e)}"


def trigger_render_deploy(hook_url: str) -> str:
    """Triggers a deployment on Render using a deploy hook URL. Pass the full deploy hook URL as hook_url."""
    url = hook_url if hook_url else os.environ.get("RENDER_DEPLOY_HOOK")
    if not url:
        return "Error: No Render deploy hook URL provided or found in environment."
        
    try:
        response = requests.get(url)
        if response.status_code in [200, 201, 202]:
            return "Successfully triggered Render deployment."
        return f"Failed to trigger deployment. Status code: {response.status_code}, Response: {response.text}"
    except Exception as e:
        return f"Error triggering Render deployment: {str(e)}"

# List of tools to pass to the AI
AVAILABLE_TOOLS = [create_github_repo, push_file_to_github, trigger_render_deploy]
