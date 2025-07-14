from parser.log_parser import parse_chat_log
from scorer.highlight_scorer import score_chat_activity
import csv
from utils.time_utils import seconds_to_timestamp


if __name__ == "__main__":
    chat_data = parse_chat_log("data/sample_chatlog.txt")
    highlight_windows = score_chat_activity(chat_data)

    for start_time, score in highlight_windows:
        print(f"{start_time}s → score: {score}")

# Print top 5 windows
print("Top Highlight Windows:")
top_windows = sorted(highlight_windows, key=lambda x: x[1], reverse=True)[:5]

for sec, score in top_windows:
    print(f"{seconds_to_timestamp(sec)} → score: {score}")

# Write to CSV
with open("output/highlights.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Time", "Score"])
    for sec, score in top_windows:
        writer.writerow([seconds_to_timestamp(sec), score])
