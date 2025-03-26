import re
from typing import List
from utils.change_tracker import extract_ONLY_diff


def highlight_text(line: str, keywords: List[str]) -> str:
    """Highlight keywords in the given line using regex."""
    if not keywords:
        return line
    for keyword in keywords:
        line = re.sub(
            rf"({re.escape(keyword)})",
            r'<span style="background-color: yellow;">\1</span>',
            line,
            flags=re.IGNORECASE,
        )
    return line


def colorize_diff(diff: str, diff2highlight: List[str] = None) -> str:
    diff_list = extract_ONLY_diff(diff)
    if not diff_list:
        return diff

    formatted_lines = []
    for line in diff_list:
        if line.startswith("+"):
            highlighted_line = f"<span style='color: green;'>{highlight_text(line, diff2highlight)}</span>"
        elif line.startswith("-"):
            highlighted_line = f"<span style='color: red;'>{highlight_text(line, diff2highlight)}</span>"
        else:
            highlighted_line = ""  # or line if you want to keep unchanged lines

        # Bold datetimes and numbers
        bolded_line = re.sub(
            r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}|[\d]+)",  # Match datetimes OR numbers
            r"<b style='color: black;'>\1</b>",
            highlighted_line,
        )

        formatted_lines.append(bolded_line)

    return "<br>".join(formatted_lines)
