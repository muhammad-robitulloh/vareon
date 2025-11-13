from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class UserGitConfigBase(BaseModel):
    github_pat: Optional[str] = Field(None, description="GitHub Personal Access Token.")
    default_author_name: Optional[str] = Field(None, description="Default author name for Git commits.")
    default_author_email: Optional[str] = Field(None, description="Default author email for Git commits.")
    default_repo_url: Optional[str] = Field(None, description="Default GitHub repository URL.")
    default_local_path: Optional[str] = Field(None, description="Default local path for the repository.")
    default_branch: Optional[str] = Field("main", description="Default branch to work on.")

class UserGitConfigCreate(UserGitConfigBase):
    pass

class UserGitConfigUpdate(UserGitConfigBase):
    pass

class UserGitConfigResponse(UserGitConfigBase):
    id: str
    user_id: str
    github_pat: Optional[str] = Field(None, description="GitHub Personal Access Token (will be masked or omitted in response).")
    decrypted_github_pat: Optional[str] = Field(None, description="Decrypted GitHub Personal Access Token (only available internally).") # New field
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class GitRepoConfig(BaseModel):
    id: Optional[str] = None
    user_id: Optional[str] = None
    repo_url: str = Field(..., description="The URL of the GitHub repository (e.g., https://github.com/user/repo.git).")
    local_path: str = Field(..., description="The local path where the repository is cloned.")
    pat_encrypted: Optional[str] = Field(None, description="Encrypted GitHub Personal Access Token for authentication.")
    branch: str = Field("main", description="The default branch to work on.")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class GitStatusFile(BaseModel):
    path: str
    status: str # e.g., 'M' (modified), 'A' (added), 'D' (deleted), '??' (untracked)

class GitStatus(BaseModel):
    current_branch: str
    is_dirty: bool
    staged_files: List[GitStatusFile]
    unstaged_files: List[GitStatusFile]
    untracked_files: List[str]
    ahead_by: int
    behind_by: int

class GitCommit(BaseModel):
    message: str
    author_name: Optional[str] = None
    author_email: Optional[str] = None

class GitFileContent(BaseModel):
    path: str
    content: str

class GitBranch(BaseModel):
    name: str
    is_current: bool
    is_remote: bool

class GitCloneRequest(BaseModel):
    repo_url: str
    local_path: str
    pat: Optional[str] = None
    branch: Optional[str] = "main"

class GitInitRequest(BaseModel):
    local_path: str

class GitAddRequest(BaseModel):
    files: List[str] = Field(..., description="List of files to add. Use '.' for all changes.")

class GitCommitRequest(BaseModel):
    message: str
    author_name: Optional[str] = None
    author_email: Optional[str] = None

class GitPushRequest(BaseModel):
    remote_name: Optional[str] = "origin"
    branch_name: Optional[str] = None # Defaults to current branch

class GitPullRequest(BaseModel):
    remote_name: Optional[str] = "origin"
    branch_name: Optional[str] = None # Defaults to current branch

class GitCheckoutRequest(BaseModel):
    branch_name: str

class GitCreateBranchRequest(BaseModel):
    branch_name: str

class GitDiffRequest(BaseModel):
    path: Optional[str] = None # If None, show diff for entire repo

class GitDiffResponse(BaseModel):
    diff: str

class GitLogEntry(BaseModel):
    hexsha: str
    author_name: str
    author_email: str
    authored_date: datetime
    message: str

class GitLogResponse(BaseModel):
    log_entries: List[GitLogEntry]
