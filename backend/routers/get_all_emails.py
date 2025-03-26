from typing import List
from fastapi import APIRouter, Depends
from routers.shared_funcs import read_emails_from_file, deduplicate_emails_in_file


get_emails_route = APIRouter()


@get_emails_route.get("/get_emails", response_model=List[str])
async def get_emails(initial_emails: set = Depends(read_emails_from_file)):
    await deduplicate_emails_in_file()
    return list(initial_emails)
