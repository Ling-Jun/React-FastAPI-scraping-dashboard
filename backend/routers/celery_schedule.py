# celery_schedule.py
from fastapi import Form, APIRouter
from fastapi.responses import JSONResponse
from pathlib import Path
from celery import Celery
from celery.schedules import crontab
import celery.beat as beat
import os
from utils.config import ChangeMonitor
from utils.change_tracker import get_URLs_from_name_registry
from routers.shared_funcs import local_repo_path, SCHEDULES_FILE
from routers.add_grants import scrape_n_add_grant

celery_schedule = APIRouter()
celery_app = Celery(
    "my_tasks",
    broker="redis://localhost:6379/0",
    # how do I know that 6379/1 is the backend, can I use 6379/0 as the backend ?
    backend="redis://localhost:6379/1",
)


@celery_app.task
def run_my_script():
    URLs = get_URLs_from_name_registry(
        os.path.join(local_repo_path, ChangeMonitor.NameRegistryFile.value)
    )
    print("Automatic Scraping Starts!!!!!!!!!!!!!")
    for url in URLs:
        _ = scrape_n_add_grant(url=url)
    print("Automatic Scraping Ends!!!!!!!!!!!!!")


def update_celery_beat(schedules):
    """Update the Celery Beat scheduler with the new schedules.

    We need to start celery beat with:
    celery -A celery_schedule beat -l info --pidfile=./redis_celery_artifacts/celerybeat.pid --logfile=./redis_celery_artifacts/celerybeat.log

    and start celery worker with:
    celery -A celery_schedule worker -l info -P gevent -c 4 --pidfile=./redis_celery_artifacts/celeryworker.pid --logfile=./redis_celery_artifacts/celeryworker.log
    """
    beat_schedule = {}
    beat_schedule["run-my-script"] = {
        "task": "run_my_script",
        "schedule": schedules,
    }
    celery_app.conf.beat_schedule = beat_schedule
    celery_app.conf.beat_schedule_filename = (
        "./redis_celery_artifacts/celerybeat_schedule/beatStuff"
    )
    celery_app.conf.timezone = "America/Winnipeg"
    celery_app.conf.update(CELERYBEAT_SCHEDULE=beat_schedule)

    # Attempt to send a signal to refresh the beat schedule dynamically
    try:
        beat.Service(celery_app).send_signal("beat-schedule-updated")
    except Exception as e:
        print(f"Error sending beat update signal: {e}")
        print("Celery Beat might require a restart for changes to take effect.")


@celery_schedule.post("/schedule")
async def schedule_task(
    schedule_value: str = Form(...),
):
    try:
        #  minute hour day_of_month month_of_year day_of_week 0 0 1 15
        parts = schedule_value.split()
        new_schedule = crontab(
            minute=parts[0],
            hour=parts[1],
            day_of_week=parts[2],
            day_of_month=parts[3],
        )

        update_celery_beat(schedules=new_schedule)

        with Path(SCHEDULES_FILE).open("w") as file:
            file.write(schedule_value + "\n")

        # repo = create_or_assign_local_repo(local_repo_path)
        # repo.git.add(A=True)
        # commit_changes2git(repo=repo, url="updated keywords.txt file")
        # upload_to_remote(
        #     local_repo_path=local_repo_path, az_container_client="", az_remote_repo_path=""
        # )
        return JSONResponse(content={"message": "Schedule updated successfully"})
    except:
        return JSONResponse(content={"message": "Error occured!!"})
