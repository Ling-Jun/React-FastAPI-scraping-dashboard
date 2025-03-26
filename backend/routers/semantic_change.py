from fastapi import APIRouter
from pathlib import Path
from utils.detect_significant_changes import word_embed_relevance
from concurrent.futures import ProcessPoolExecutor
from routers.shared_funcs import KEYWORDS_FILE
import asyncio

detect_semantic_change = APIRouter()

async def read_keywords_file(file_path: str) -> str:
    path = Path(file_path)
    if path.exists():
        return await asyncio.to_thread(path.read_text)
    return ""

@detect_semantic_change.post("/detect_semantic_change")
async def semantic_change(diff: str):
    keywords = await read_keywords_file(KEYWORDS_FILE)
    
    loop = asyncio.get_running_loop()
    with ProcessPoolExecutor() as executor:
        change_significance = await loop.run_in_executor(
            executor,
            word_embed_relevance,
            diff,
            keywords,
            3,
            0.9,
            None
        )
    return change_significance
