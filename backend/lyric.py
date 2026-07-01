"""LRC lyric file parser."""
import re


def parse_lrc(lrc_text):
    """
    Parse LRC-format lyrics into timed lines.

    Args:
        lrc_text: Raw LRC lyric string.

    Returns:
        List of dicts: [{"time": seconds_float, "text": "lyric line"}, ...]
        Sorted by time ascending. Returns empty list if no lyrics.
    """
    if not lrc_text:
        return []

    lines = []
    # Pattern: [mm:ss.xx] or [mm:ss.xxx] followed by text
    pattern = re.compile(r"\[(\d{1,3}):(\d{2})(?:\.(\d{2,3}))?\](.*)")

    for line in lrc_text.strip().split("\n"):
        match = pattern.match(line.strip())
        if not match:
            continue

        minutes = int(match.group(1))
        seconds = int(match.group(2))
        centiseconds = match.group(3) or "0"

        # Normalize to seconds as float
        if len(centiseconds) == 2:
            cs = int(centiseconds) / 100.0
        else:
            cs = int(centiseconds) / 1000.0

        time_sec = minutes * 60 + seconds + cs
        text = match.group(4).strip()

        if text:
            lines.append({"time": time_sec, "text": text})

    # Sort by time
    lines.sort(key=lambda x: x["time"])
    return lines


def find_current_line(lyric_lines, current_time_sec):
    """
    Find the index of the current lyric line based on playback position.

    Args:
        lyric_lines: Parsed lyric lines from parse_lrc().
        current_time_sec: Current playback position in seconds.

    Returns:
        Index of the current line, or -1 if before the first line.
    """
    if not lyric_lines:
        return -1

    current_idx = -1
    for i, line in enumerate(lyric_lines):
        if line["time"] <= current_time_sec:
            current_idx = i
        else:
            break

    return current_idx
