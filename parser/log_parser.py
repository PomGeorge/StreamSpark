import re
from typing import List, Tuple

def parse_chat_log(file_path: str) -> List[Tuple[str, str, str]]:
    
    # Parses a Twitch chat log and returns a list of (timestamp, username, message) tuples.
    
    chat_entries = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            match = re.match(r"\[(\d{2}:\d{2}:\d{2})\] (\w+): (.+)", line.strip())
            if match:
                timestamp, username, message = match.groups()
                chat_entries.append((timestamp, username, message))
    return chat_entries
