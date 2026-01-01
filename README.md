# Youtube-video-downloader

A small command-line tool using `yt-dlp` to download YouTube videos or specific time sections (without downloading the full video and trimming). Also supports downloading subtitles/captions.

## Features ✅
- Select format/quality (interactive or via format selector)
- Download a specific time range (start/end) without downloading the entire video
- Download captions/subtitles (specific language or automatic)

## Requirements 🔧
- Python 3.8+
- yt-dlp Python package (install with `pip install yt-dlp`)
- ffmpeg on PATH (used by yt-dlp to merge audio/video and process sections)

## Usage 💡
Examples:

- Download the full video (best quality):

  python main.py "<VIDEO_URL>"

- Download a section (from 60s to 120s) in best format:

  python main.py "<VIDEO_URL>" --start 60 --end 120

- Interactive format selection and download section:

  python main.py "<VIDEO_URL>" --interactive --start 00:01:00 --end 00:02:00

- Download captions only (English automatic fallback):

  python main.py "<VIDEO_URL>" --captions-only --lang en --auto

## Notes ⚠️
- The tool uses `yt-dlp`'s `--download-sections` capability to fetch only the specified parts when possible (this avoids downloading the full video and trimming).
- If ffmpeg is not available in PATH, merging and section extraction may fail; install ffmpeg and ensure it's on your PATH.

---

If you want, I can add a small GUI or integrate this into a larger workflow next.



How to use ?

python main.py -f mp4 --start 00:00:00 --end 00:00:10 -o output.mp4 "https://youtu.be/bR8sE9ubyTI?si=FJNZYPzNrttxRAjp"
