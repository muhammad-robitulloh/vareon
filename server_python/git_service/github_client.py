import requests
from typing import List, Dict, Any
from server_python.github_app import get_installation_access_token

class GitHubClient:
    def __init__(self, installation_id: int):
        self.installation_id = installation_id
        self.headers = {}

    async def __aenter__(self):
        access_token = await get_installation_access_token(self.installation_id)
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github.v3+json",
        }
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass

    async def get_repositories(self) -> List[Dict[str, Any]]:
        url = "https://api.github.com/installation/repositories"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()["repositories"]

    async def get_branches(self, repo_full_name: str) -> List[str]:
        url = f"https://api.github.com/repos/{repo_full_name}/branches"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return [branch["name"] for branch in response.json()]
