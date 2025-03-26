# celery_tasks.py
import os
from celery import shared_task
from utils.config import ChangeMonitor
from utils.change_tracker import get_URLs_from_name_registry
from routers.shared_funcs import local_repo_path
from routers.add_grants import scrape_n_add_grant


@shared_task
def run_my_script():
    URLs = get_URLs_from_name_registry(
        os.path.join(local_repo_path, ChangeMonitor.NameRegistryFile.value)
    )
    print("Automatic Scraping Starts!!!!!!!!!!!!!")
    for url in URLs:
        _ = scrape_n_add_grant(url=url)
    print("Automatic Scraping Ends!!!!!!!!!!!!!")
