from fastapi import HTTPException
from fastapi import APIRouter, Depends
from pydantic import BaseModel
import aiofiles
from routers.shared_funcs import EMAILS_FILE, read_emails_from_file

# from utils.change_tracker import add_content_to_file


class EmailToAdd(BaseModel):  # Pydantic model for request body
    email: str


add_email_route = APIRouter()


@add_email_route.post("/add_email", status_code=201)
async def add_email(
    email2add: EmailToAdd, initial_emails: set = Depends(read_emails_from_file)
):
    if email2add.email not in initial_emails:
        try:
            # Update the in-memory set to avoid unnecessary file reads.
            initial_emails.add(email2add.email)
            print(f"Added email: {email2add.email}\n")

            # update the file on disc
            async with aiofiles.open(EMAILS_FILE, mode="a", encoding="utf-8") as file:
                await file.write(f"{email2add.email}\n")
        except Exception as e:
            print(f"Error adding email: {e}\n")
            raise HTTPException(
                status_code=500, detail="Failed to add email"
            )  # More appropriate status code
    else:
        raise HTTPException(status_code=400, detail="Email already exists")
