from typing import Dict, Any, Callable, List, Optional
import asyncio

from terminal.service import TerminalService
from server_python.git_service.service import GitService # Import the GitService
from server_python.git_service import schemas as git_schemas # Import Git schemas

# 1. Tool Definition
# A tool is a dictionary with a schema for the LLM and a function to call.

async def execute_shell_command(terminal_service: TerminalService, command: str) -> str:
    """
    Executes a shell command in the user's sandboxed environment and returns the output.
    
    :param terminal_service: The instance of the TerminalService for the user's session.
    :param command: The shell command to execute.
    :return: A string containing the stdout and stderr of the command.
    """
    print(f"Executing shell command: '{command}'")
    stdout, stderr = await terminal_service.execute_command(command)
    
    output = ""
    if stdout:
        output += f"STDOUT:\n{stdout}\n"
    if stderr:
        output += f"STDERR:\n{stderr}\n"
    
    if not output:
        return "Command executed with no output."
        
    return output

async def git_clone_repo(git_service: GitService, repo_url: str, local_path: str, pat: Optional[str] = None, branch: Optional[str] = "main") -> str:
    """Clones a Git repository from a given URL to a local path."""
    request = git_schemas.GitCloneRequest(repo_url=repo_url, local_path=local_path, pat=pat, branch=branch)
    return git_service.clone_repo(request)

async def git_get_status(git_service: GitService, local_path: str) -> Dict[str, Any]:
    """Gets the current Git status of a repository."""
    status = git_service.get_status(local_path)
    return status.dict()

async def git_add_files(git_service: GitService, local_path: str, files: List[str]) -> str:
    """Adds files to the Git staging area."""
    request = git_schemas.GitAddRequest(files=files)
    return git_service.add_files(local_path, request)

async def git_commit_changes(git_service: GitService, local_path: str, message: str, author_name: Optional[str] = None, author_email: Optional[str] = None) -> str:
    """Commits staged changes to the repository."""
    request = git_schemas.GitCommitRequest(message=message, author_name=author_name, author_email=author_email)
    return git_service.commit_changes(local_path, request)

async def git_push_changes(git_service: GitService, local_path: str, remote_name: Optional[str] = "origin", branch_name: Optional[str] = None) -> str:
    """Pushes committed changes to a remote repository."""
    request = git_schemas.GitPushRequest(remote_name=remote_name, branch_name=branch_name)
    return git_service.push_changes(local_path, request)

async def git_pull_changes(git_service: GitService, local_path: str, remote_name: Optional[str] = "origin", branch_name: Optional[str] = None) -> str:
    """Pulls changes from a remote repository."""
    request = git_schemas.GitPullRequest(remote_name=remote_name, branch_name=branch_name)
    return git_service.pull_changes(local_path, request)

async def git_checkout_branch(git_service: GitService, local_path: str, branch_name: str) -> str:
    """Switches to a specified Git branch."""
    request = git_schemas.GitCheckoutRequest(branch_name=branch_name)
    return git_service.checkout_branch(local_path, request)

async def git_create_branch(git_service: GitService, local_path: str, branch_name: str) -> str:
    """Creates a new Git branch."""
    request = git_schemas.GitCreateBranchRequest(branch_name=branch_name)
    return git_service.create_branch(local_path, request)

# 2. Tool Schema for the LLM
# This tells the LLM how to call our function.

tools_schema = [
    {
        "type": "function",
        "function": {
            "name": "execute_shell_command",
            "description": "Executes a shell command in the user's sandboxed environment and returns the output. Use this for any file system operations, running scripts, or checking system status.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The shell command to execute (e.g., 'ls -l', 'cat my_file.txt').",
                    }
                },
                "required": ["command"],
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
    {
        "type": "function",
        "function": {
            "name": "git_add_files",
            "description": "Adds specified files or all changes to the Git staging area.",
            "parameters": {
                "type": "object",
                "properties": {
                    "local_path": {"type": "string", "description": "The local directory path of the Git repository."},
                    "files": {"type": "array", "items": {"type": "string"}, "description": "List of files to add. Use ['.'] to add all changes."}
                },
                "required": ["local_path", "files"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "git_commit_changes",
            "description": "Commits staged changes to the repository with a given message.",
            "parameters": {
                "type": "object",
                "properties": {
                    "local_path": {"type": "string", "description": "The local directory path of the Git repository."},
                    "message": {"type": "string", "description": "The commit message."},
                    "author_name": {"type": "string", "description": "Optional: Name of the commit author."},
                    "author_email": {"type": "string", "description": "Optional: Email of the commit author."}
                },
                "required": ["local_path", "message"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "git_push_changes",
            "description": "Pushes committed changes from the local repository to a remote repository.",
            "parameters": {
                "type": "object",
                "properties": {
                    "local_path": {"type": "string", "description": "The local directory path of the Git repository."},
                    "remote_name": {"type": "string", "description": "Optional: The name of the remote to push to. Defaults to 'origin'."},
                    "branch_name": {"type": "string", "description": "Optional: The name of the branch to push. Defaults to the current branch."}
                },
                "required": ["local_path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "git_pull_changes",
            "description": "Pulls changes from a remote repository into the local repository.",
            "parameters": {
                "type": "object",
                "properties": {
                    "local_path": {"type": "string", "description": "The local directory path of the Git repository."},
                    "remote_name": {"type": "string", "description": "Optional: The name of the remote to pull from. Defaults to 'origin'."},
                    "branch_name": {"type": "string", "description": "Optional: The name of the branch to pull. Defaults to the current branch."}
                },
                "required": ["local_path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "git_checkout_branch",
            "description": "Switches the repository to a specified Git branch.",
            "parameters": {
                "type": "object",
                "properties": {
                    "local_path": {"type": "string", "description": "The local directory path of the Git repository."},
                    "branch_name": {"type": "string", "description": "The name of the branch to checkout."}
                },
                "required": ["local_path", "branch_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "git_create_branch",
            "description": "Creates a new Git branch.",
            "parameters": {
                "type": "object",
                "properties": {
                    "local_path": {"type": "string", "description": "The local directory path of the Git repository."},
                    "branch_name": {"type": "string", "description": "The name of the new branch to create."}
                },
                "required": ["local_path", "branch_name"],
            },
        },
    },
]

# 3. Tool Registry
# This maps the function name from the schema to the actual Python function.

tool_registry: Dict[str, Callable] = {
    "execute_shell_command": execute_shell_command,
    "git_clone_repo": git_clone_repo,
    "git_get_status": git_get_status,
    "git_add_files": git_add_files,
    "git_commit_changes": git_commit_changes,
    "git_push_changes": git_push_changes,
    "git_pull_changes": git_pull_changes,
    "git_checkout_branch": git_checkout_branch,
    "git_create_branch": git_create_branch,
}
