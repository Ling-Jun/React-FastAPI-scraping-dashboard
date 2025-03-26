from fastapi import HTTPException
from typing import List
from fastapi import APIRouter, Depends
from pydantic import BaseModel
import aiofiles
from routers.shared_funcs import EMAILS_FILE, read_emails_from_file


class EmailsToDelete(BaseModel):  # Pydantic model for request body
    emails: List[str]


delete_emails_route = APIRouter()


@delete_emails_route.post("/delete_emails", status_code=204)
async def delete_emails(
    emails2delete: EmailsToDelete, initial_emails: set = Depends(read_emails_from_file)
):
    try:
        for email in emails2delete.emails:
            if (
                email in initial_emails
            ):  # Removing email directly from the set since it was an issue
                # initial_emails.remove(email)
                # emails.remove(email)  # Remove from original list
                initial_emails.discard(email)  # Use discard to avoid potential KeyError
                print(f"Email {email} removed!!!!!!!!!")

        async with aiofiles.open(EMAILS_FILE, "w", encoding="utf-8") as f:
            await f.writelines(email + "\n" for email in initial_emails)

    except Exception as e:
        print(f"Error removing emails: {e}\n")
        raise HTTPException(status_code=500, detail="Failed to delete emails")
