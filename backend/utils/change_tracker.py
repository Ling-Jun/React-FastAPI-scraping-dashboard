import os
import re
import time
from uuid import uuid4
from git import Repo
from azure.storage.blob import ContainerClient
import aiofiles
from utils.github_remote import download_from_remote, create_or_assign_local_repo
from utils.az_blob_store import upload_file_to_blob
from utils.scrapeNsearchUtils import extract_page2txt
from utils.config import RemoteOrigin, ChangeMonitor, WarningMessages, PARSER
from routers.shared_funcs import local_repo_path


def _generate_random_filename_with_timestamp(extension="txt"):
    timestamp = time.strftime("%Y-%m-%d__%H-%M-%S")
    unique_id = uuid4().hex[:6]  # Shortened UUID for brevity
    return f"{timestamp}_{unique_id}.{extension}"


def _reduce_empty_lines(text: str):
    lines = text.splitlines()
    filtered_lines = []
    # Iterate over lines and append if it's not an empty line or if the last line added wasn't empty
    for line in lines:
        if line.strip() != "" or (filtered_lines and filtered_lines[-1].strip() != ""):
            filtered_lines.append(line)
    return "\n".join(filtered_lines)


async def add_content_to_file(content, file_path, mode="w"):
    async with aiofiles.open(file_path, mode=mode, encoding="utf-8") as file:
        await file.write(content)
    if mode == "w":
        print("CONTENT WRITTEN TO FILE!\n")
    elif mode == "a":
        print("CONTENT APPENDED TO FILE!\n")


async def git_ignore(repo_path: str, file2ignore_path: str):
    gitignore_path = os.path.join(repo_path, ".gitignore")
    async with aiofiles.open(gitignore_path, "w", encoding="utf-8") as f:
        await f.write(f"*{file2ignore_path}\n.gitignore\n")
    if RemoteOrigin.Azure.value:
        upload_file_to_blob(gitignore_path, ".gitignore")
    print(f".gitignore updated successfully. Ignoring {file2ignore_path}\n")


def commit_changes2git(repo: Repo, url: str):
    """
    This function should also allow user revert to last commit before a deadline, so that the user
    can view the diff/changes before a deadline, e.g. end of day.
    """
    timestamp = time.strftime("%Y-%m-%d  %H-%M-%S")
    repo.index.commit(f"Content update for {url} at {timestamp}")
    print("CHANGES TO FILE COMMITTED!\n")


async def get_URLs_from_name_registry(name_registry_path: str):
    # download_from_remote(local_repo_path, "", "", "")
    if not os.path.exists(name_registry_path):
        print(f"NO {name_registry_path} EXISTS\n")
        return []
    try:
        async with aiofiles.open(name_registry_path, "r") as file:
            content = file.read()
            content_list = content.replace(" ", "").replace("\n", "").split(",")
            file.close()
        # we drop the last item from the list with [:-1], since .split(",") returns an empty string as the last item
        return content_list[::2][:-1]
    except Exception as e:
        print(f"Get URLs from name registry ERROR: {e}\n")
        return []


async def match_url2filename(url, name_registry_path: str):
    if not os.path.exists(name_registry_path):
        await add_content_to_file("\n", name_registry_path, mode="w")
        print("Created new name registry!!!!\n")
    try:
        async with aiofiles.open(name_registry_path, "r", encoding="utf-8") as file:
            url_dict = {
                line.split(",")[0]: line.split(",")[1]
                async for line in file
                if "," in line
            }
        print(f"FOUND MATCHING FILE {url_dict.get(url, "")}!\n")
        return url_dict.get(url, "")
    except Exception as e:
        print(f"match_url2filename() ERROR: {e}\n")
        print("NO MATCHING FILE FOUND FOR THE GIVEN URL!\n")
        return ""


def get_diff_N_Commits_Ago(
    local_repo_path, file_name, N_commits_back=0, num_context_lines=3
):
    """
    Ensure there are enough commits in history,
    N_commits_back skips to the N_commits_back prior commit back.
    N_commits_back > = 0
    diff PERTAINS to specific file_name
    """
    try:
        print(f"Getting diff from {N_commits_back} commits ago.\n")
        original_dir = os.getcwd()
        os.chdir(local_repo_path)
        # repo = create_or_assign_local_repo(local_repo_path=local_repo_path)
        # commits_list = list(repo.iter_commits(paths=file_name))
        # diff = repo.git.diff(
        #     commits_list[N_commits_back + 1],
        #     commits_list[N_commits_back],
        #     file_name,
        #     unified=num_context_lines,
        # )
        # commit_hash = next(itertools.islice(commits_generator, N_commits_back, N_commits_back + 1), None)
        # print(f"The commit hash is {commit_hash}\n")
        # diff = repo.git.diff(commit_hash.parents[0], commit_hash[N_commits_back], file_name)
        # diff = repo.git.diff(f"HEAD~{N_commits_back+1}", f"HEAD~{N_commits_back}", file_name)
        exclude_pattern = re.compile(r"^(diff --git|index|--- |\+\+\+ |@@)")
        diff = "\n".join(
            line for line in diff.splitlines() if not exclude_pattern.match(line)
        )
        if not diff:
            os.chdir(original_dir)
            print("NO CHANGES FOUND IN THE FILE!\n")
            return WarningMessages.NoChanges.value
        return diff
    except:
        return WarningMessages.OnlyOneVersion.value


async def scrape_n_get_diff(
    url: str,
    local_repo_path: str,
    az_remote_repo_path: str,
    az_container_client: ContainerClient,
):
    content = extract_page2txt(url, parser=PARSER.BS4.value)
    # print(f"file content : {content}\n")
    content = _reduce_empty_lines(content)
    if content in [
        WarningMessages.URLNotValid.value,
        WarningMessages.ContentNotValid.value,
    ]:
        # print(f"Warning: {content}")
        return content, "Not saved to any file."

    local_name_registry = os.path.join(
        local_repo_path, ChangeMonitor.NameRegistryFile.value
    )
    # if not os.path.exists(local_name_registry):
    #     download_from_remote(
    #         local_repo_path=local_repo_path,
    #         local_file_path="",
    #         az_remote_file_path=os.path.join(
    #             az_remote_repo_path, ChangeMonitor.NameRegistryFile.value
    #         ),
    #         az_container_client=az_container_client,
    #     )

    file_name = await match_url2filename(url, local_name_registry)
    if not file_name:
        file_name = _generate_random_filename_with_timestamp()
        await add_content_to_file(
            f"{url},{file_name},\n", local_name_registry, mode="a"
        )

    file_path = os.path.join(local_repo_path, file_name)
    await add_content_to_file(content, file_path, mode="w")

    repo = create_or_assign_local_repo(local_repo_path)
    if file_name in repo.untracked_files:
        return WarningMessages.FirstTimeTracking.value, file_name

    # diff between working dir and last commit
    file_diff = repo.git.diff(file_path)
    # print(f"file_diff: {file_diff}\n")
    if not file_diff and file_name not in repo.untracked_files:
        print("Nothing to commit! File not dirty.")
        return WarningMessages.NoChanges.value, file_name
    return file_diff, file_name


def extract_ONLY_diff(diff, start_with_minus="-", start_with_plus="+"):
    """
    Extracts lines starting with '-' or '+' from the given Git diff.

    Parameters: diff (str): The Git diff as a single string.
    Returns:
        List[str]: A list containing lines that start with '-' or '+'.
    """
    lines = diff.splitlines()
    return [
        line
        for line in lines
        if line.startswith("+")
        and not line.startswith("+++")
        or line.startswith("-")
        and not line.startswith("---")
    ]
