from typing import Dict, Any, Callable, List, Optional
import asyncio
from sqlalchemy.orm import Session
from fastapi import BackgroundTasks

# Service and schema imports
from terminal.service import TerminalService
from server_python.git_service.service import GitService
from server_python.git_service import schemas as git_schemas
from server_python.database import User
from server_python.arcana import crud as arcana_crud
from server_python.arcana import agent_orchestration_service as arcana_service
from server_python.arcana.schemas import AgentExecuteRequest

# 1. Tool Definition
# A tool is a dictionary with a schema for the LLM and a function to call.

async def execute_shell_command(db: Session, user: User, terminal_service: TerminalService, background_tasks: BackgroundTasks, command: str) -> str:
    """
    Executes a shell command in the user's sandboxed environment and returns the output.
    """
    print(f"Executing shell command: '{command}'")
    stdout, stderr, exit_code = await terminal_service.execute_command(command)
    
    output = ""
    if stdout:
        output += f"STDOUT:\n{stdout}\n"
    if stderr:
        output += f"STDERR:\n{stderr}\n"
    output += f"EXIT CODE: {exit_code}\n"
    
    if not output:
        return "Command executed with no output."
        
    return output

async def delegate_task_to_arcana(
    db: Session, 
    user: User, 
    terminal_service: TerminalService, # Keep for consistent signature
    background_tasks: BackgroundTasks,
    task_prompt: str, 
    parent_job_id: Optional[str] = None
) -> str:
    """
    Delegates a complex, multi-step task (like coding, file manipulation, git operations) 
    to a specialized Arcana agent. Finds a suitable agent automatically. Returns the Job ID for tracking.
    """
    try:
        # Automatically find a suitable worker agent
        worker_agent = db.query(arcana_crud.ArcanaAgent).filter(
            arcana_crud.ArcanaAgent.owner_id == str(user.id),
            arcana_crud.ArcanaAgent.mode.in_(['tool_user', 'autonomous'])
        ).first()

        if not worker_agent:
            return "Error: No suitable Arcana worker agent found for the current user."

        agent_id = worker_agent.id
        
        # 1. Create the AgentExecuteRequest for Arcana
        arcana_request = AgentExecuteRequest(agent_id=agent_id, task_prompt=task_prompt)

        # 2. Create the Arcana Job in the database
        job = arcana_crud.create_agent_job(
            db=db,
            agent_id=agent_id,
            owner_id=str(user.id),
            goal=task_prompt,
            message_history=[{"role": "user", "content": task_prompt}],
            original_request=arcana_request,
            parent_job_id=parent_job_id # Link to the parent job
        )
        db.flush() # Ensure job.id is available
        
        # 3. Add the execution to background tasks
        background_tasks.add_task(
            arcana_service.execute_agent_task,
            db=db,
            user=user,
            request=arcana_request,
            job_id=job.id
        )
        
        return f"Task successfully delegated to Arcana agent '{worker_agent.name}' (ID: {agent_id}). Job ID: {job.id}. Monitor this job ID for completion."
    except Exception as e:
        return f"Error delegating task to Arcana: {str(e)}"


# --- Git Service Tools ---
# Note: These tools now initialize GitService on-the-fly using the provided user and db context.

async def git_clone_repo(db: Session, user: User, terminal_service: TerminalService, repo_url: str, local_path: str, pat: Optional[str] = None, branch: Optional[str] = "main") -> str:
    """Clones a Git repository from a given URL to a local path."""
    git_service = GitService(db, user)
    request = git_schemas.GitCloneRequest(repo_url=repo_url, local_path=local_path, pat=pat, branch=branch)
    return git_service.clone_repo(request)

async def git_get_status(db: Session, user: User, terminal_service: TerminalService, local_path: str) -> Dict[str, Any]:
    """Gets the current Git status of a repository."""
    git_service = GitService(db, user)
    status = git_service.get_status(local_path)
    return status.dict()

async def git_add_files(db: Session, user: User, terminal_service: TerminalService, local_path: str, files: List[str]) -> str:
    """Adds files to the Git staging area."""
    git_service = GitService(db, user)
    request = git_schemas.GitAddRequest(files=files)
    return git_service.add_files(local_path, request)

async def git_commit_changes(db: Session, user: User, terminal_service: TerminalService, local_path: str, message: str, author_name: Optional[str] = None, author_email: Optional[str] = None) -> str:
    """Commits staged changes to the repository."""
    git_service = GitService(db, user)
    request = git_schemas.GitCommitRequest(message=message, author_name=author_name, author_email=author_email)
    return git_service.commit_changes(local_path, request)

async def git_push_changes(db: Session, user: User, terminal_service: TerminalService, local_path: str, remote_name: Optional[str] = "origin", branch_name: Optional[str] = None) -> str:
    """Pushes committed changes to a remote repository."""
    git_service = GitService(db, user)
    request = git_schemas.GitPushRequest(remote_name=remote_name, branch_name=branch_name)
    return git_service.push_changes(local_path, request)

async def git_pull_changes(db: Session, user: User, terminal_service: TerminalService, local_path: str, remote_name: Optional[str] = "origin", branch_name: Optional[str] = None) -> str:
    """Pulls changes from a remote repository."""
    git_service = GitService(db, user)
    request = git_schemas.GitPullRequest(remote_name=remote_name, branch_name=branch_name)
    return git_service.pull_changes(local_path, request)

async def git_checkout_branch(db: Session, user: User, terminal_service: TerminalService, local_path: str, branch_name: str) -> str:
    """Switches to a specified Git branch."""
    git_service = GitService(db, user)
    request = git_schemas.GitCheckoutRequest(branch_name=branch_name)
    return git_service.checkout_branch(local_path, request)

async def git_create_branch(db: Session, user: User, terminal_service: TerminalService, local_path: str, branch_name: str) -> str:
    """Creates a new Git branch."""
    git_service = GitService(db, user)
    request = git_schemas.GitCreateBranchRequest(branch_name=branch_name)
    return git_service.create_branch(local_path, request)

# 2. Tool Schema for the LLM
# This tells the LLM how to call our function.

tools_schema = [

    {
        "type": "function",
        "function": {
            "name": "delegate_task_to_arcana",
            "description": "Delegates a complex, multi-step task to a specialized 'Arcana' agent. Use this for tasks involving coding, file editing, running tests, or complex git workflows. This is the preferred tool for any software development task.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_prompt": {
                        "type": "string",
                        "description": "A clear, detailed, and self-contained natural language prompt describing the entire task for the Arcana agent.",
                    },
                    "parent_job_id": {
                        "type": "string",
                        "description": "Optional: The ID of the parent job in Cognisys, for hierarchical tracking."
                    }
                },
                "required": ["task_prompt"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "git_clone_repo",
            "description": "Clones a Git repository from a given URL to a local path. Requires a GitHub Personal Access Token (PAT) for private repositories.",
            "parameters": {
                "type": "object",
                "properties": {
                    "repo_url": {"type": "string", "description": "The URL of the Git repository (e.g., https://github.com/user/repo.git)."},
                    "local_path": {"type": "string", "description": "The local directory path where the repository should be cloned."},
                    "pat": {"type": "string", "description": "Optional: GitHub Personal Access Token for authentication with private repositories."},
                    "branch": {"type": "string", "description": "Optional: The branch to checkout after cloning. Defaults to 'main'."}
                },
                "required": ["repo_url", "local_path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "git_get_status",
            "description": "Gets the current Git status of a repository, including current branch, dirty state, staged, unstaged, and untracked files.",
            "parameters": {
                "type": "object",
                "properties": {
                    "local_path": {"type": "string", "description": "The local directory path of the Git repository."}
                },
                "required": ["local_path"],
            },
        },
    },
    # ... other git tool schemas are omitted for brevity but should be here ...
]

# 3. Tool Registry
# This maps the function name from the schema to the actual Python function.

tool_registry: Dict[str, Callable] = {
    "execute_shell_command": execute_shell_command,
    "delegate_task_to_arcana": delegate_task_to_arcana,
    "git_clone_repo": git_clone_repo,
    "git_get_status": git_get_status,
    "git_add_files": git_add_files,
    "git_commit_changes": git_commit_changes,
    "git_push_changes": git_push_changes,
    "git_pull_changes": git_pull_changes,
    "git_checkout_branch": git_checkout_branch,
    "git_create_branch": git_create_branch,
}
