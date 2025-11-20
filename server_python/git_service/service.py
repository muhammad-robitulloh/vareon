import os
import shutil
from typing import List, Optional, Tuple
from datetime import datetime
import git # GitPython
from fastapi import HTTPException
from sqlalchemy.orm import Session

from server_python.database import User, UserGitConfig as DBUserGitConfig # Assuming User model is available
from server_python.encryption_utils import encrypt_api_key, decrypt_api_key # Assuming these exist
from server_python.github_app import get_installation_access_token
from . import schemas, crud

class GitService:
    def __init__(self, db: Session, user: User):
        self.db = db
        self.user = user
        # Base directory for all user repositories
        self.user_repos_base_dir = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '.gemini', 'tmp')), f"user_git_repos_{self.user.id}")
        os.makedirs(self.user_repos_base_dir, exist_ok=True)

    def _get_user_git_config(self) -> Optional[DBUserGitConfig]:
        """Retrieves and decrypts the user's Git configuration."""
        # Call crud.get_user_git_config with decrypt_pat=True
        db_config = crud.get_user_git_config(self.db, str(self.user.id), decrypt_pat=True)
        return db_config

    def _get_repo_path(self, local_path: str) -> str:
        """Constructs a safe absolute path for a repository within the user's base directory."""
        if not local_path:
            raise HTTPException(status_code=400, detail="Local path cannot be empty.")
        abs_path = os.path.abspath(os.path.join(self.user_repos_base_dir, local_path))
        if not abs_path.startswith(self.user_repos_base_dir):
            raise HTTPException(status_code=400, detail="Invalid repository path: outside user's allowed directory.")
        return abs_path

    async def _get_repo(self, local_path: str) -> git.Repo:
        """Gets a git.Repo object for the given local_path, setting up credentials if available."""
        repo_path = self._get_repo_path(local_path)
        if not os.path.exists(os.path.join(repo_path, '.git')):
            raise HTTPException(status_code=404, detail=f"Git repository not found at {local_path}. Please clone or initialize it.")
        
        repo = git.Repo(repo_path)
        
        # Configure credentials for push/pull operations if installation ID is available
        user_config = self._get_user_git_config()
        if user_config and user_config.github_app_installation_id and repo.remotes:
            installation_token = await get_installation_access_token(user_config.github_app_installation_id)
            for remote in repo.remotes:
                # Only modify remote URL if it's a GitHub HTTPS URL
                if "github.com" in remote.url and remote.url.startswith("https://"):
                    # Ensure the URL is not already configured with a token to avoid duplication
                    if f"x-access-token:{installation_token}@" not in remote.url:
                        parsed_url = git.cmd.Git.polish_url(remote.url)
                        auth_url = f"https://x-access-token:{installation_token}@{parsed_url.hostname}{parsed_url.path}"
                        with repo.config.edit() as config:
                            config.set_value(f"remote.{remote.name}", "url", auth_url)
        return repo

    def init_repo(self, request: schemas.GitInitRequest) -> str:
        repo_path = self._get_repo_path(request.local_path)
        if os.path.exists(os.path.join(repo_path, '.git')):
            raise HTTPException(status_code=400, detail=f"Repository already exists at {request.local_path}")
        
        os.makedirs(repo_path, exist_ok=True)
        repo = git.Repo.init(repo_path)
        return f"Repository initialized at {request.local_path}"

    async def clone_repo(self, request: schemas.GitCloneRequest) -> str:
        repo_path = self._get_repo_path(request.local_path)
        if os.path.exists(repo_path) and os.path.exists(os.path.join(repo_path, '.git')):
            raise HTTPException(status_code=400, detail=f"Repository already cloned to {request.local_path}")

        user_config = self._get_user_git_config()
        if not user_config or not user_config.github_app_installation_id:
            raise HTTPException(status_code=400, detail="GitHub App not installed for this user.")

        try:
            installation_token = await get_installation_access_token(user_config.github_app_installation_id)
            auth_repo_url = request.repo_url
            if "github.com" in request.repo_url:
                parsed_url = git.cmd.Git.polish_url(request.repo_url)
                auth_repo_url = f"https://x-access-token:{installation_token}@{parsed_url.hostname}{parsed_url.path}"

            repo = git.Repo.clone_from(auth_repo_url, repo_path, branch=request.branch)
            return f"Repository '{request.repo_url}' cloned to {request.local_path}"
        except git.exc.GitCommandError as e:
            raise HTTPException(status_code=400, detail=f"Failed to clone repository: {e.stderr}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred during cloning: {e}")

    async def get_status(self, local_path: str) -> schemas.GitStatus:
        repo = await self._get_repo(local_path)
        
        staged_files = []
        unstaged_files = []
        untracked_files = []

        # Staged changes
        for (path, stage), entry in repo.index.entries.items():
            if stage > 0: # Stage 0 is for unstaged, 1,2,3 for staged
                staged_files.append(schemas.GitStatusFile(path=path, status=repo.git.diff('--name-status', '--cached', path).split('\t')[0]))

        # Unstaged changes
        for diff_obj in repo.index.diff(None):
            unstaged_files.append(schemas.GitStatusFile(path=diff_obj.a_path or diff_obj.b_path, status=diff_obj.change_type))

        # Untracked files
        for f in repo.untracked_files:
            untracked_files.append(f)

        # Ahead/Behind
        ahead_by = 0
        behind_by = 0
        try:
            current_branch = repo.active_branch
            if current_branch.tracking_branch():
                tracking = current_branch.tracking_branch()
                if tracking:
                    ahead_by = len(list(repo.iter_commits(f'{current_branch.name}@{{upstream}}..{current_branch.name}')))
                    behind_by = len(list(repo.iter_commits(f'{current_branch.name}..{current_branch.name}@{{upstream}}')))
        except Exception:
            pass # No tracking branch or other error
        
        return schemas.GitStatus(
            current_branch=repo.active_branch.name,
            is_dirty=repo.is_dirty(untracked_files=True),
            staged_files=staged_files,
            unstaged_files=unstaged_files,
            untracked_files=untracked_files,
            ahead_by=ahead_by,
            behind_by=behind_by
        )

    async def add_files(self, local_path: str, request: schemas.GitAddRequest) -> str:
        repo = await self._get_repo(local_path)
        try:
            if '.' in request.files:
                repo.git.add(all=True)
            else:
                repo.index.add(request.files)
            return f"Files added to staging in {local_path}"
        except git.exc.GitCommandError as e:
            raise HTTPException(status_code=400, detail=f"Failed to add files: {e.stderr}")

    async def commit_changes(self, local_path: str, request: schemas.GitCommitRequest) -> str:
        repo = await self._get_repo(local_path)
        if not repo.index.diff("HEAD"):
            raise HTTPException(status_code=400, detail="No changes to commit from index.")
        
        user_config = self._get_user_git_config()
        author_name_to_use = request.author_name or (user_config.default_author_name if user_config else None)
        author_email_to_use = request.author_email or (user_config.default_author_email if user_config else None)

        try:
            # Set author if provided or from user config
            if author_name_to_use and author_email_to_use:
                repo.config_writer().set_value('user', 'name', author_name_to_use).release()
                repo.config_writer().set_value('user', 'email', author_email_to_use).release()
            
            commit_result = repo.index.commit(request.message)
            return f"Changes committed with SHA: {commit_result.hexsha[:7]}"
        except git.exc.GitCommandError as e:
            raise HTTPException(status_code=400, detail=f"Failed to commit changes: {e.stderr}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred during commit: {e}")

    async def push_changes(self, local_path: str, request: schemas.GitPushRequest) -> str:
        repo = await self._get_repo(local_path)
        try:
            remote = repo.remote(request.remote_name)
            branch_name = request.branch_name or repo.active_branch.name
            
            user_config = self._get_user_git_config()
            if user_config and hasattr(user_config, 'github_pat') and user_config.github_pat:
                # This should ideally update the remote's URL to include the PAT
                # before calling push, or rely on credential helper.
                # For GitPython, it's often more reliable to have the remote URL
                # already configured with PAT or rely on a global credential manager.
                # Here, we ensure the remote URL is correctly formatted with PAT if
                # it's a GitHub HTTPS URL and not already configured.
                if "github.com" in remote.url and remote.url.startswith("https://"):
                    parsed_url = git.cmd.Git.polish_url(remote.url)
                    auth_url = f"https://oauth2:{user_config.github_pat}@{parsed_url.hostname}{parsed_url.path}"
                    remote.set_url(auth_url) # Temporarily change URL for push
                
            remote.push(branch_name)
            return f"Changes pushed to {request.remote_name}/{branch_name}"
        except git.exc.GitCommandError as e:
            raise HTTPException(status_code=400, detail=f"Failed to push changes: {e.stderr}")

    async def pull_changes(self, local_path: str, request: schemas.GitPullRequest) -> str:
        repo = await self._get_repo(local_path)
        try:
            remote = repo.remote(request.remote_name)
            branch_name = request.branch_name or repo.active_branch.name

            # Use PAT if available for pull
            user_config = self._get_user_git_config()
            if user_config and hasattr(user_config, 'github_pat') and user_config.github_pat:
                if "github.com" in remote.url and remote.url.startswith("https://"):
                    parsed_url = git.cmd.Git.polish_url(remote.url)
                    auth_url = f"https://oauth2:{user_config.github_pat}@{parsed_url.hostname}{parsed_url.path}"
                    remote.set_url(auth_url)
            
            remote.pull(branch_name)
            return f"Changes pulled from {request.remote_name}/{branch_name}"
        except git.exc.GitCommandError as e:
            raise HTTPException(status_code=400, detail=f"Failed to pull changes: {e.stderr}")

    async def checkout_branch(self, local_path: str, request: schemas.GitCheckoutRequest) -> str:
        repo = await self._get_repo(local_path)
        try:
            repo.git.checkout(request.branch_name)
            return f"Checked out branch {request.branch_name}"
        except git.exc.GitCommandError as e:
            raise HTTPException(status_code=400, detail=f"Failed to checkout branch: {e.stderr}")

    async def create_branch(self, local_path: str, request: schemas.GitCreateBranchRequest) -> str:
        repo = await self._get_repo(local_path)
        try:
            new_branch = repo.create_head(request.branch_name)
            # new_branch.checkout() # Often you want to checkout after creating
            return f"Created branch {request.branch_name}"
        except git.exc.GitCommandError as e:
            raise HTTPException(status_code=400, detail=f"Failed to create branch: {e.stderr}")
    
    async def get_branches(self, local_path: str) -> List[schemas.GitBranch]:
        repo = await self._get_repo(local_path)
        branches: List[schemas.GitBranch] = []
        try:
            active_branch_name = repo.active_branch.name
        except TypeError: # Detached HEAD state
            active_branch_name = None

        # Local branches
        for head in repo.heads:
            branches.append(schemas.GitBranch(
                name=head.name,
                is_current=(head.name == active_branch_name),
                is_remote=False
            ))
        
        # Remote branches
        for remote in repo.remotes:
            for ref in remote.refs:
                # Exclude HEAD refs and avoid duplicates if remote tracking branch has same name as local
                if ref.name.endswith('/HEAD'):
                    continue
                branch_name = ref.name.replace(f'{remote.name}/', '')
                if not any(b.name == branch_name and not b.is_remote for b in branches): # Avoid duplicate if local exists
                     branches.append(schemas.GitBranch(
                        name=branch_name,
                        is_current=False, # Remote can't be current local branch
                        is_remote=True
                    ))
        return branches

    async def read_file_content(self, local_path: str, file_path: str) -> str:
        repo_abs_path = self._get_repo_path(local_path)
        file_abs_path = os.path.join(repo_abs_path, file_path)
        # Ensure the file is actually within the repository path after normalization
        if not os.path.abspath(file_abs_path).startswith(os.path.abspath(repo_abs_path)):
            raise HTTPException(status_code=400, detail="File path outside repository bounds.")

        if not os.path.exists(file_abs_path) or os.path.isdir(file_abs_path):
            raise HTTPException(status_code=404, detail=f"File not found or is a directory: {file_path}")
        
        try:
            with open(file_abs_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return content
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to read file '{file_path}': {e}")

    async def write_file_content(self, local_path: str, file_path: str, content: str) -> str:
        repo_abs_path = self._get_repo_path(local_path)
        file_abs_path = os.path.join(repo_abs_path, file_path)
        
        # Ensure the file is actually within the repository path after normalization
        if not os.path.abspath(file_abs_path).startswith(os.path.abspath(repo_abs_path)):
            raise HTTPException(status_code=400, detail="File path outside repository bounds.")

        # Ensure directory exists
        os.makedirs(os.path.dirname(file_abs_path), exist_ok=True)

        try:
            with open(file_abs_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"File '{file_path}' written successfully."
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to write to file '{file_path}': {e}")

    async def get_diff(self, local_path: str, request: schemas.GitDiffRequest) -> schemas.GitDiffResponse:
        repo = await self._get_repo(local_path)
        try:
            if request.path:
                diff_output = repo.git.diff(request.path)
            else:
                diff_output = repo.git.diff()
            return schemas.GitDiffResponse(diff=diff_output)
        except git.exc.GitCommandError as e:
            raise HTTPException(status_code=400, detail=f"Failed to get diff: {e.stderr}")

    async def get_log(self, local_path: str) -> schemas.GitLogResponse:
        repo = await self._get_repo(local_path)
        log_entries = []
        try:
            for commit in repo.iter_commits():
                log_entries.append(schemas.GitLogEntry(
                    hexsha=commit.hexsha,
                    author_name=commit.author.name,
                    author_email=commit.author.email,
                    authored_date=datetime.fromtimestamp(commit.authored_date),
                    message=commit.message
                ))
            return schemas.GitLogResponse(log_entries=log_entries)
        except git.exc.GitCommandError as e:
            raise HTTPException(status_code=400, detail=f"Failed to get log: {e.stderr}")
