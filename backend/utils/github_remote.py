import git
from github import Github
from github.GithubException import GithubException
from utils.config import *
from utils.az_blob_store import *


def create_github_repo():
    user = Github(Ghub.GITHUB_TOKEN.value).get_user()
    try:
        remote_repo = user.create_repo(
            Ghub.REPO_NAME.value,
            private=False,
            description="This is a public repository created using PyGithub",
        )
        print(
            f"Repository '{Ghub.REPO_NAME.value}' created successfully: {remote_repo.html_url}\n\n"
        )
        return remote_repo
    except GithubException as e:
        print(
            f"Repository '{Ghub.REPO_NAME.value}' already exists. Returning the existing repository."
        )
        remote_repo = user.get_repo(Ghub.REPO_NAME.value)
        print(f"Existing repository URL: {remote_repo.html_url}")
        print(f"GithubException occurred: {e.data, e.status}\n\n")
        return remote_repo
    except Exception as e:
        print(f"An unexpected error occurred: {e}\n\n")
        return None


# this line is necessary, it allows us to create/initialize the Github remote repo when starting the app
# remote_github_repo = create_github_repo()


def create_or_assign_local_repo(local_repo_path: str):
    try:
        local_repo = git.Repo(local_repo_path)
        print(f"Git Repo already exists! at {local_repo_path}\n\n")
    except Exception as e:
        print(f"There is an Exception: {e}\n\n")
        local_repo = git.Repo.init(local_repo_path)
        print(f"Creating GIT repo! at {local_repo_path}\n\n")
    return local_repo


def add_remote_origin(
    local_repo: git.Repo,
    remote_url=create_github_repo().clone_url.replace(
        "https://", f"https://{Ghub.GITHUB_USERNAME.value}:{Ghub.GITHUB_TOKEN.value}@"
    ),
):
    remotes = {remote.name: remote for remote in local_repo.remotes}
    # print(f"remotes: {remotes}\n")
    if "origin" in remotes:
        current_url = remotes["origin"].url
        if current_url != remote_url:
            # Remove the existing origin and add a new one
            local_repo.delete_remote("origin")
            print(f"Removed existing remote origin at {current_url}\n")
            origin = local_repo.create_remote("origin", remote_url)
            print(f"Added new remote origin at {remote_url}\n")
        else:
            origin = remotes["origin"]
            print(f"Remote origin exists and matches the existing origin of local repo!\n")
    else:
        # Create a new remote if no origin exists
        origin = local_repo.create_remote("origin", remote_url)
        print(f"Added remote origin pointing to {remote_url}\n")
    
    return origin



def pull_remote(origin: git.Repo.remote, local_repo: git.Repo):
    try:
        origin.fetch()
        local_repo.git.pull("origin", "master")
        print(
            f"Pulled latest changes from remote repository: {create_github_repo().html_url}\n\n"
        )
    except Exception as e:
        print(f"Error pulling changes from remote: {e}\n\n")


def push2remote(origin: git.Repo.remote):
    try:
        origin.push(refspec="master:master")
        print(f"Code pushed to remote repository: {create_github_repo().html_url}\n\n")
    except Exception as e:
        print(f"Error pushing changes to remote: {e}\n\n")


def upload_to_remote(local_repo_path, az_remote_repo_path, az_container_client):
    if RemoteOrigin.Azure.value:
        upload_dir_to_blob(
            local_dir_path=local_repo_path,
            remote_dir_path=az_remote_repo_path,
            az_container_client=az_container_client,
        )
    if RemoteOrigin.Github.value:
        local_repo = create_or_assign_local_repo(local_repo_path=local_repo_path)
        origin = add_remote_origin(local_repo=local_repo)
        push2remote(origin=origin)


def download_from_remote(
    local_repo_path, local_file_path, az_remote_file_path, az_container_client
):
    """
    TO BE OPTIMIZED, this function pulls one file at a time for Azure, but pulls the entire repo for Github
    """
    if RemoteOrigin.Azure.value:
        download_file_from_blob(
            local_file_path=local_file_path,
            remote_file_path=az_remote_file_path,
            az_container_client=az_container_client,
        )
    if RemoteOrigin.Github.value:
        local_repo = create_or_assign_local_repo(local_repo_path=local_repo_path)
        remote_origin = add_remote_origin(local_repo=local_repo)
        pull_remote(origin=remote_origin, local_repo=local_repo)
