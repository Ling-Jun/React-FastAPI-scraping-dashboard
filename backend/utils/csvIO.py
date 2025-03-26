from pathlib import Path
from datetime import datetime
from typing import List, Literal
import asyncio, re
from concurrent.futures import ProcessPoolExecutor
import aiofiles
from aiocsv import AsyncDictReader, AsyncDictWriter
from routers.shared_funcs import KEYWORDS_FILE
from utils.change_tracker import extract_ONLY_diff
from utils.detect_significant_changes import word_embed_relevance
from utils.config import WarningMessages, Grant
from utils.colorize_diffs import colorize_diff


async def grants_status_from_csv(DB_PATH: str) -> List[dict]:
    GRANTS = []
    try:
        async with aiofiles.open(DB_PATH, mode="r", encoding="utf-8") as file:
            reader = AsyncDictReader(file, delimiter=";")
            async for row in reader:
                GRANTS.append(row)
    except FileNotFoundError:
        print(f"File {DB_PATH} not found.")
    return GRANTS


def _parse_scrape_date(scrape_date: str):
    try:
        return datetime.strptime(scrape_date, "%Y-%m-%d  %H-%M-%S")
    except:
        return scrape_date


def split_and_strip2list(
    s: str, delimiters: List[str] = ["\n"], strip_chars: str = ""
) -> List[str]:
    substrings = [s]
    for delimiter in delimiters:
        # For each substring, split it by the current delimiter
        # This results in a list of lists, which we flatten using a list comprehension
        substrings = [
            segment
            for substring in substrings
            for segment in substring.split(delimiter)
        ]
    if strip_chars:
        substrings = [substring.strip(strip_chars) for substring in substrings]
    return [substring for substring in substrings if substring]


async def _status_from_diff(diff: str, similarity_threshold=0):
    if diff in {
        WarningMessages.FirstTimeTracking.value,
        WarningMessages.NoChanges.value,
    }:
        return "No Change!", None
    if diff in {
        WarningMessages.ContentNotValid.value,
        WarningMessages.URLNotValid.value,
    }:
        return "Invalid", None
    if diff == WarningMessages.OnlyOneVersion.value:
        return WarningMessages.OnlyOneVersion.value, None

    if Path(KEYWORDS_FILE).exists():
        keywords = await asyncio.to_thread(Path(KEYWORDS_FILE).read_text)
        keywords_list = split_and_strip2list(
            keywords, delimiters=["\n"], strip_chars='"'
        )
        # print(f"keywords: {keywords}\n")
        # print(f"keywords_list: {keywords_list}\n")
        # print(f"length keywords_list: {len(keywords_list)}\n")

    diff_list = extract_ONLY_diff(diff)
    loop = asyncio.get_running_loop()
    with ProcessPoolExecutor() as executor:
        diff_keyword_pair = await loop.run_in_executor(
            executor,
            word_embed_relevance,
            diff_list,
            keywords_list,
            similarity_threshold,
        )

    if diff_keyword_pair:
        return WarningMessages.SignificantChange.value, diff_keyword_pair
    return WarningMessages.TrivialChange.value, diff_keyword_pair


async def insert_or_update_row(
    diff, scrape_date, url: str, DB_PATH: str, similarity_threshold=0
):
    status, diff_keyword_pair = await _status_from_diff(diff, similarity_threshold)
    print(f"diff_keyword_pair: {diff_keyword_pair}\n")
    table_row = new_row(
        pageURL=url,
        date=_parse_scrape_date(scrape_date),
        status=status,
        diff=colorize_diff(
            diff, [i[0] for i in diff_keyword_pair] if diff_keyword_pair else None
        ),
    )

    if table_row["status"] == "Invalid":
        return table_row

    # ========= Update CSV =========; this is very slow =================
    # ========= Update CSV =========; this is very slow =================
    rows = []
    try:
        async with aiofiles.open(DB_PATH, mode="r", encoding="utf-8") as file:
            async for row in AsyncDictReader(file, delimiter=";"):
                rows.append(row)
    except FileNotFoundError:
        pass

    row_updated = False
    for row in rows:
        if row["page"] == table_row["page"]:
            row.update(table_row)
            row_updated = True
            break
    if not row_updated:
        rows.append(table_row)

    async with aiofiles.open(DB_PATH, mode="w", encoding="utf-8", newline="") as file:
        writer = AsyncDictWriter(
            file, fieldnames=["page", "date", "status", "diff"], delimiter=";"
        )
        await writer.writeheader()
        await writer.writerows(rows)
    return table_row


def new_row(pageURL=None, date=None, status=None, diff=None):
    return {
        "page": pageURL,
        "date": date,
        "status": status,
        "diff": diff,
    }


async def update_grants_CSV(new_row, DB_PATH: str, delete=False):
    old_rows = []
    try:
        async with aiofiles.open(DB_PATH, mode="r", encoding="utf-8") as file:
            async for row in AsyncDictReader(file, delimiter=";"):
                old_rows.append(row)
    except FileNotFoundError:
        print(f"File {DB_PATH} not found.")
        return

    # print(new_row)
    updated_rows = []
    for row in old_rows:
        if row["page"] == new_row["page"]:
            if delete:
                print(f"Deleting row: {row['page']}\n")
                continue  # Skip adding this row to updated_rows if deleting
            elif new_row["status"]:
                print(f"Modifying status of row: {row['page']}\n")
                row["status"] = _update_row_status(row["status"], new_row["status"])
            elif new_row["date"]:
                print(f"Modifying date of row: {row['page']}\n")
                row["date"] = new_row["date"]
        updated_rows.append(row)

    async with aiofiles.open(DB_PATH, mode="w", encoding="utf-8", newline="") as file:
        writer = AsyncDictWriter(
            file, fieldnames=["page", "date", "status", "diff"], delimiter=";"
        )
        await writer.writeheader()
        await writer.writerows(updated_rows)


def _update_row_status(row_status, new_row_status):
    """Updates the status. Replaces "Reviewed at..." if found, otherwise appends."""
    if "Reviewed at" in new_row_status and "Reviewed at" in row_status:
        row_status = re.sub(r"Reviewed at.*", new_row_status, row_status)
    elif "Reviewed at" in new_row_status and not "Reviewed at" in row_status:
        row_status = row_status + new_row_status
    else:
        row_status = new_row_status  # replace if not found
    return row_status
