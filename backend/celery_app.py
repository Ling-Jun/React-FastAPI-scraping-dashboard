# celery_app.py
from celery import Celery
from celery.schedules import crontab

# import tasks  # Ensure this import is present

app = Celery(
    "my_tasks",
    broker="redis://localhost:6379/0",
    # how do I know that 6379/1 is the backend, can I use 6379/0 as the backend ?
    backend="redis://localhost:6379/1",
    include=["celery_tasks"],  # Add the module containing your tasks
)

app.conf.beat_schedule = {
    "scrape-monday-8am": {  # Unique key
        "task": "celery_tasks.run_my_script",  # Task name
        "schedule": crontab(hour=8, day_of_week="1"),  # Monday at 8 AM
    },
    "scrape-wednesday-6pm": {  # Unique key
        "task": "celery_tasks.run_my_script",  # Task name
        "schedule": crontab(hour=18, day_of_week="3"),  # Wednesday at 6 PM
    },
}

app.conf.beat_schedule_filename = (
    "./redis_celery_artifacts/celerybeat_schedule/beatStuff"
)
app.conf.timezone = "America/Winnipeg"
