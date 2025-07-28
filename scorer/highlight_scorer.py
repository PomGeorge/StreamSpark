from typing import List, Tuple
from collections import defaultdict
import datetime

EMOTE_KEYWORDS = ["Pog", "LUL", "OMEGALUL", "KEKW", "Kappa", "😂", "😱", "🔥"]

# Helper: convert HH:MM:SS string to seconds
def timestamp_to_seconds(ts: str) -> int:
    h, m, s = map(int, ts.split(":"))
    return h * 3600 + m * 60 + s

def score_chat_activity(chat_data: List[Tuple[str, str, str]], window_size: int = 10) -> List[Tuple[int, int]]:
    
    # Groups chat into time windows and assigns hype scores using:
    # - message content (emotes, caps)
    # - unique user count (burst scoring)
    
    window_scores = defaultdict(int)
    window_users = defaultdict(set)  # maps window → set of usernames

    for timestamp, username, message in chat_data:
        seconds = timestamp_to_seconds(timestamp)
        window_start = (seconds // window_size) * window_size
        score = 1

        # Emoji characters
        for char in message:
            if ord(char) > 1000:
                score += 1

        # Emote words
        for emote in EMOTE_KEYWORDS:
            if emote.lower() in message.lower():
                score += 2

        # All caps words
        words = message.split()
        score += sum(1 for word in words if word.isupper() and len(word) > 2)

        window_scores[window_start] += score
        window_users[window_start].add(username)

    # Boost windows with lots of unique users (burst scoring)
    for window, users in window_users.items():
        window_scores[window] += len(users) * 2  # +2 per unique user

    return sorted(window_scores.items(), key=lambda x: x[0])
