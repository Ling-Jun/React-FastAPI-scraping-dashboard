from pathlib import Path
from fastapi import Request, APIRouter
from utils.config import *
from utils.change_tracker import *
from utils.csvIO import grants_status_from_csv
from routers.shared_funcs import (
    DB_PATH,
    KEYWORDS_FILE,
    SCHEDULES_FILE,
    EMAILS_FILE,
)

# from celery_tasks import local_repo_path, DB_PATH

landing_page = APIRouter()


@landing_page.get(
    "/landing"
)  # default is JSON response, so we dont have response_class
async def get_home():
    # create the DB and KEYWORDS files if not existing
    try:
        fp = open(DB_PATH, "x")
        fp.close()
        fp = open(KEYWORDS_FILE, "x")
        fp.close()
        fp = open(SCHEDULES_FILE, "x")
        fp.close()
        fp = open(EMAILS_FILE, "x")
        fp.close()
    except:
        pass
    if Path(KEYWORDS_FILE).exists():
        # keywords are loaded when the app starts, cuold use an optimization to speed things up
        keywords = Path(KEYWORDS_FILE).read_text()
    if Path(SCHEDULES_FILE).exists():
        # keywords are loaded when the app starts, cuold use an optimization to speed things up
        schedules = Path(SCHEDULES_FILE).read_text()
    return {
        "grants": await grants_status_from_csv(DB_PATH=DB_PATH),
        "keywords": keywords,
        "schedules": schedules,
    }
