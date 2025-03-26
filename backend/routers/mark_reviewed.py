from fastapi import APIRouter
from utils.config import Grant
from utils.csvIO import update_grants_CSV, new_row

# from utils.github_remote import upload_to_remote
# from utils.change_tracker import (
#     commit_changes2git,
#     create_or_assign_local_repo,
# )
from routers.shared_funcs import DB_PATH, local_repo_path
import threading

mark_as_reviewed = APIRouter()
repo_lock = threading.Lock()  # Global lock for the repository


@mark_as_reviewed.post("/mark_reviewed")
async def mark_reviewed(data: Grant):
    with repo_lock:
        # print(f"""Marking {data} as reviewed.\n""")
        await update_grants_CSV(
            new_row(pageURL=data.url, status=data.status), DB_PATH=DB_PATH
        )
        # repo = create_or_assign_local_repo(local_repo_path)
        # repo.git.add(A=True)
        # commit_changes2git(repo=repo, url="updated grants.csv file")
        # upload_to_remote(
        #     local_repo_path=local_repo_path,
        #     az_container_client="",
        #     az_remote_repo_path="",
        # )
