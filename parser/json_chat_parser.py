import json
from typing import List, Tuple

def parse_json_chat(path: str) -> List[Tuple[int, str, str]]:
    """
    Parses Twitch chat JSON (from twitch-dl) into (timestamp, username, message) tuples.
    """
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    chat_entries = []
    for msg in data['comments']:
        seconds = int(msg['content_offset_seconds'])
        user = msg['commenter']['display_name']
        message = msg['message']['body']
        chat_entries.append((seconds, user, message))

    return chat_entries
