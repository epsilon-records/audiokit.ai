from pathlib import Path
from typing import List

import git
from pydantic import BaseModel


class RepoInfo(BaseModel):
    path: str
    name: str
    branch: str
    last_commit: str
    status: dict


class RepoRequest(BaseModel):
    repo_path: str


class RepoListResponse(BaseModel):
    repositories: List[RepoInfo]


async def get_repo_info(repo_path: str) -> RepoInfo:
    repo = git.Repo(repo_path)
    return RepoInfo(
        path=repo_path,
        name=Path(repo_path).name,
        branch=repo.active_branch.name,
        last_commit=repo.head.commit.hexsha,
        status={
            "modified": [item.a_path for item in repo.index.diff(None)],
            "untracked": repo.untracked_files,
        },
    )


async def list_repositories(request: RepoRequest) -> RepoListResponse:
    """List all repositories in the workspace"""
    workspace_path = Path(request.repo_path)
    repos = []

    for path in workspace_path.rglob(".git"):
        if path.is_dir():
            repo_path = str(path.parent)
            try:
                repo_info = await get_repo_info(repo_path)
                repos.append(repo_info)
            except git.InvalidGitRepositoryError:
                continue

    return RepoListResponse(repositories=repos)
