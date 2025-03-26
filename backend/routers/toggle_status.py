from fastapi import APIRouter, BackgroundTasks
from utils.config import Grant, recipients
from utils.csvIO import update_grants_CSV, new_row

# from utils.github_remote import upload_to_remote
# from utils.change_tracker import (
#     commit_changes2git,
#     create_or_assign_local_repo,
# )
from utils.email_handling import sendEmail
from routers.shared_funcs import DB_PATH, local_repo_path
import threading

repo_lock = threading.Lock()  # Global lock for the repository
toggle_row_status = APIRouter()


@toggle_row_status.post("/toggle_status")
async def update_table(data: Grant, background_tasks: BackgroundTasks):
    with repo_lock:
        print(data)
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
    background_tasks.add_task(
        sendEmail,
        email_content=f"""
        <html>
        <head></head>
        <body>
            <h1 style="color:blue;">Status UPDATE</h1>
            <p style="font-size:16px; color:grey;">
            Status of URL {data.url} was changed to {data.status}!
            </p>
        </body>
        </html>
        """,
        recipients=recipients,
    )
    return {"message": "Updated URLs table!"}
