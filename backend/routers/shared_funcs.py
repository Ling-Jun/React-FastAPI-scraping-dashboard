from pathlib import Path
from fastapi.templating import Jinja2Templates
from utils.change_tracker import *


root_dir = Path(__file__).resolve().parent.parent
print(f"root_dir: {root_dir}\n")
local_repo_path = os.path.join(root_dir, ChangeMonitor.WebTrackingRepo.value)
DB_PATH = os.path.join(local_repo_path, ChangeMonitor.GRANTS_DB.value)
KEYWORDS_FILE = os.path.join(local_repo_path, ChangeMonitor.KEYWORDS.value)
SCHEDULES_FILE = os.path.join(local_repo_path, ChangeMonitor.SCHEDULES.value)
EMAILS_FILE = os.path.join(local_repo_path, ChangeMonitor.EmailsFile.value)
templates_dir = os.path.join(root_dir, "templates")
templates = Jinja2Templates(directory=templates_dir)
static_dir = os.path.join(root_dir, "static")


async def read_emails_from_file():
    """This only reads when the server startes and updates the list"""
    try:
        async with aiofiles.open(EMAILS_FILE, "r", encoding="utf-8") as file:
            contents = await file.read()  # Read the entire file content
            # Return a set, dedpulicated
            emails = {line.strip() for line in contents.splitlines()}
            return emails
    except FileNotFoundError:  # Handle file not found error
        return set()
    except Exception as e:
        print(f"Error reading emails: {e}")
        return set()


async def deduplicate_emails_in_file():
    """Removes duplicate emails from the emails file."""
    deduped_emails = await read_emails_from_file()
    deduped_lines = [email + "\n" for email in deduped_emails]
    # print(f"dedupe_lines: {deduped_lines}\n")
    async with aiofiles.open(EMAILS_FILE, mode="w", encoding="utf-8") as file:
        await file.writelines(deduped_lines)
    print("Deduplicated emails file.")
