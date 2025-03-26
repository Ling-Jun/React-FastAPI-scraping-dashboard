from fastapi import APIRouter
from datetime import datetime
from zoneinfo import ZoneInfo

# from utils.github_remote import upload_to_remote
from utils.change_tracker import (
    # commit_changes2git,
    # create_or_assign_local_repo,
    scrape_n_get_diff,
)
from utils.az_blob_store import initialize_az_container_client
from utils.email_handling import sendEmail
from utils.csvIO import insert_or_update_row
from utils.config import (
    RemoteOrigin,
    ChangeMonitor,
    Grant,
    WarningMessages,
    recipients,
)
from routers.shared_funcs import local_repo_path, DB_PATH
import threading

add_grant_urls = APIRouter()

repo_lock = threading.Lock()  # Global lock for the repository


async def scrape_n_add_grant(url):
    ottawa_tz = ZoneInfo("America/Toronto")
    ottawa_time = datetime.now(ottawa_tz)
    diff, _ = await scrape_n_get_diff(
        url=url,
        local_repo_path=local_repo_path,
        az_remote_repo_path=(
            "" if not RemoteOrigin.Azure.value else ChangeMonitor.WebTrackingRepo.value
        ),
        az_container_client=(
            None if not RemoteOrigin.Azure.value else initialize_az_container_client()
        ),
    )
    # print(f"diff is: {diff}\n\n")
    # print(f"ottawa_time: {ottawa_time}\n")
    new_row = await insert_or_update_row(
        diff,
        ottawa_time.strftime("%Y-%m-%d %H-%M-%S"),
        url,
        DB_PATH,
        similarity_threshold=0.5,
    )

    if new_row["status"] == "Invalid":
        return new_row

    if new_row["status"] == WarningMessages.SignificantChange.value:
        sendEmail(
            email_content=f"""
                <html>
                <head></head>
                <body>
                    <h1 style="color:blue;">Status UPDATE</h1>
                    <p style="font-size:16px; color:grey;">
                    Status of URL {new_row["page"]} was changed to {new_row['status']}!
                    </p>
                </body>
                </html>
                """,
            recipients=recipients,
        )

    # repo = create_or_assign_local_repo(local_repo_path)
    # repo.git.add(A=True)
    # commit_changes2git(repo=repo, url="ENTIRE LOCAL REPO")
    # print("Changes committed to local repo!!!!!!\n")
    # upload_to_remote(
    #     local_repo_path=local_repo_path,
    #     az_remote_repo_path=(
    #         "" if not RemoteOrigin.Azure.value else ChangeMonitor.WebTrackingRepo.value
    #     ),
    #     az_container_client=(
    #         None if not RemoteOrigin.Azure.value else initialize_az_container_client()
    #     ),
    # )
    return new_row


@add_grant_urls.post("/add_grant")
async def add_grant(grant: Grant):
    with repo_lock:  # Acquire the lock before accessing the repository
        new_row = await scrape_n_add_grant(grant.url)
        return new_row
