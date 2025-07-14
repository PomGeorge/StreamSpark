def seconds_to_timestamp(seconds: int) -> str:
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes:02d}:{secs:02d}"
