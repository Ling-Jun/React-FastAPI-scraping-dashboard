from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn
from utils.config import *

# from utils.github_remote import download_from_remote
from routers.landing import landing_page
from routers.add_grants import add_grant_urls
from routers.show_prior_diff import prior_diff
from routers.update_keywords import edit_keywords
from routers.semantic_change import detect_semantic_change
from routers.toggle_status import toggle_row_status
from routers.shared_funcs import local_repo_path, static_dir
from routers.send_email import send2custom_email
from routers.mark_reviewed import mark_as_reviewed
from routers.delete_row import delete_row

# from routers.update_url import update_urls
from routers.celery_schedule import celery_schedule
from routers.get_all_emails import get_emails_route
from routers.add_email_addrs import add_email_route
from routers.delete_email_addrs import delete_emails_route

# from celery_tasks import local_repo_path, DB_PATH


# download_from_remote(local_repo_path, "", "", "")

app = FastAPI(root_path="/api")
app.mount("/static", StaticFiles(directory=static_dir), name="static")
# app.mount("/templates", StaticFiles(directory=templates_dir), name="templates")

app.include_router(landing_page)
app.include_router(add_grant_urls)
app.include_router(prior_diff)
app.include_router(edit_keywords)
app.include_router(detect_semantic_change)
app.include_router(toggle_row_status)
app.include_router(send2custom_email)
app.include_router(mark_as_reviewed)
app.include_router(delete_row)
# app.include_router(update_urls)
app.include_router(celery_schedule)
app.include_router(add_email_route)
app.include_router(delete_emails_route)
app.include_router(get_emails_route)

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", reload=True)
