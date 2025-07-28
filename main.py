from parser.json_chat_parser import parse_json_chat
from parser.log_parser import parse_chat_log
from scorer.highlight_scorer import score_chat_activity
from utils.time_utils import seconds_to_timestamp
import csv
import os
import subprocess

def parse_auto(path: str):
    if path.endswith(".json"):
        return parse_json_chat(path)
    else:
        return parse_chat_log(path)

def clip_highlights(video_path: str, timestamps: list[int], duration: int = 15):
    os.makedirs("output/clips", exist_ok=True)
    for i, start_sec in enumerate(timestamps):
        output_file = f"output/clips/highlight_{i+1}.mp4"
        cmd = [
            "ffmpeg",
            "-ss", str(start_sec),
            "-i", video_path,
            "-t", str(duration),
            "-c", "copy",
            "-y",  # Overwrite if exists
            output_file
        ]
        print(f"Clipping {output_file} at {seconds_to_timestamp(start_sec)}...")
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

if __name__ == "__main__":
    CHAT_PATH = "chat.json"
    VIDEO_PATH = "vod.mp4"

    chat_data = parse_auto(CHAT_PATH)
    highlight_windows = score_chat_activity(chat_data)

    for start_time, score in highlight_windows:
        print(f"{start_time}s → score: {score}")

    print("Top Highlight Windows:")
    top_windows = sorted(highlight_windows, key=lambda x: x[1], reverse=True)[:5]

    for sec, score in top_windows:
        print(f"{seconds_to_timestamp(sec)} → score: {score}")

    os.makedirs("output", exist_ok=True)
    with open("output/highlights.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Time", "Score"])
        for sec, score in top_windows:
            writer.writerow([seconds_to_timestamp(sec), score])

    top_timestamps = [sec for sec, _ in top_windows]
    clip_highlights(VIDEO_PATH, top_timestamps)
