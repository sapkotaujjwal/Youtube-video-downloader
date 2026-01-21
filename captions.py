import os
import subprocess
import json
import re

CHANNEL_URL = "https://www.youtube.com/@veritasium"
CHANNEL_NAME = "Veritasium"
BASE_DIR = os.path.join(os.getcwd(), CHANNEL_NAME)

os.makedirs(BASE_DIR, exist_ok=True)


def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name)


def get_video_list():
    print("Fetching video list...")
    cmd = [
        "yt-dlp",
        "--dump-json",
        "--flat-playlist",
        CHANNEL_URL
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    videos = []

    for line in result.stdout.splitlines():
        data = json.loads(line)
        videos.append({
            "id": data["id"],
            "title": sanitize_filename(data["title"])
        })

    return videos


def download_captions(video):
    video_url = f"https://www.youtube.com/watch?v={video['id']}"
    output_template = os.path.join(BASE_DIR, video["title"])

    cmd = [
        "yt-dlp",
        "--skip-download",
        "--write-subs",
        "--write-auto-subs",
        "--sub-lang", "en",
        "--sub-format", "vtt",
        "-o", output_template,
        video_url
    ]

    subprocess.run(cmd, capture_output=True)


def vtt_to_text(vtt_path):
    text = []
    with open(vtt_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or "-->" in line or line.isdigit():
                continue
            line = re.sub(r"<.*?>", "", line)
            text.append(line)
    return " ".join(text)


def process_subtitles(video):
    for file in os.listdir(BASE_DIR):
        if file.startswith(video["title"]) and file.endswith(".vtt"):
            vtt_path = os.path.join(BASE_DIR, file)
            text = vtt_to_text(vtt_path)

            txt_path = os.path.join(BASE_DIR, f"{video['title']}.txt")
            with open(txt_path, "w", encoding="utf-8") as out:
                out.write(f"Title: {video['title']}\n")
                out.write(f"URL: https://www.youtube.com/watch?v={video['id']}\n\n")
                out.write(text)

            os.remove(vtt_path)
            print(f"Saved captions: {video['title']}")


def main():
    videos = get_video_list()
    print(f"Found {len(videos)} videos")

    for video in videos:
        print(f"Processing: {video['title']}")
        download_captions(video)
        process_subtitles(video)

    print("✅ ALL CAPTIONS SCRAPED SUCCESSFULLY")


if __name__ == "__main__":
    main()
