import os
from fastapi import APIRouter
from utils.csvIO import insert_or_update_row
from utils.change_tracker import match_url2filename, get_diff_N_Commits_Ago
from utils.config import ChangeMonitor, Grant
from routers.shared_funcs import local_repo_path, DB_PATH


prior_diff = APIRouter()


# DONT name the router the same as your async function
@prior_diff.post("/show_prior_diff")
async def show_prior_diff(grant: Grant):

    file_name = await match_url2filename(
        grant.url,
        name_registry_path=os.path.join(
            local_repo_path, ChangeMonitor.NameRegistryFile.value
        ),
    )
    diff = get_diff_N_Commits_Ago(
        local_repo_path=local_repo_path, file_name=file_name, N_commits_back=1
    )
    new_row = await insert_or_update_row(
        diff, "N/A", grant.url, DB_PATH, similarity_threshold=0.5
    )
    return new_row
