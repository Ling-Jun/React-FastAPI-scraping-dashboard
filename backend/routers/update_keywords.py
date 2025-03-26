from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse
from pathlib import Path

# from utils.github_remote import upload_to_remote
# from utils.change_tracker import (
#     commit_changes2git,
#     create_or_assign_local_repo,
# )
from routers.shared_funcs import KEYWORDS_FILE, local_repo_path
import threading

edit_keywords = APIRouter()
repo_lock = threading.Lock()  # Global lock for the repository


@edit_keywords.post("/update_keywords")
async def update_keywords(keywords: str = Form(...)):
    with repo_lock:
        for delimiter in [";", "|", "\n", "\t"]:
            keywords = keywords.replace(delimiter, ",")
        keyword_list = [kw.strip() for kw in keywords.split(",") if kw.strip()]
        formatted_keywords = "\n".join(keyword_list)
        with Path(KEYWORDS_FILE).open("w") as file:
            file.write(formatted_keywords)

        # repo = create_or_assign_local_repo(local_repo_path)
        # repo.git.add(A=True)
        # commit_changes2git(repo=repo, url="updated keywords.txt file")
        # upload_to_remote(
        #     local_repo_path=local_repo_path,
        #     az_container_client="",
        #     az_remote_repo_path="",
        # )
        return JSONResponse(content={"message": "Keywords updated successfully"})
