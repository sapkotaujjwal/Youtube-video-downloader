import os
import re
from typing import Optional, List
from yt_dlp import YoutubeDL


def parse_time(t: Optional[str]) -> Optional[str]:
    """Accepts seconds (int/float) or HH:MM:SS and returns HH:MM:SS or None."""
    if not t:
        return None
    t = str(t).strip()

    # digits only (seconds)
    if re.fullmatch(r"\d+(\.\d+)?", t):
        s = float(t)
        h = int(s // 3600)
        m = int((s % 3600) // 60)
        sec = int(s % 60)
        return f"{h:02d}:{m:02d}:{sec:02d}"

    # hh:mm:ss or mm:ss
    parts = t.split(":")
    parts = [int(float(p)) for p in parts]

    if len(parts) == 1:
        return f"00:00:{parts[0]:02d}"
    if len(parts) == 2:
        m, s = parts
        return f"00:{m:02d}:{s:02d}"
    if len(parts) >= 3:
        h, m, s = parts[-3], parts[-2], parts[-1]
        return f"{h:02d}:{m:02d}:{s:02d}"

    return None


def list_formats(url: str) -> List[dict]:
    ydl_opts = {"quiet": True, "no_warnings": True}
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    formats = info.get("formats", [])
    seen = set()
    out = []

    for f in formats:
        fid = f.get("format_id")
        if fid in seen:
            continue
        seen.add(fid)

        out.append({
            "format_id": fid,
            "ext": f.get("ext"),
            "resolution": f.get("resolution") or f.get("height") or "-",
            "fps": f.get("fps"),
            "note": f.get("format_note"),
            "filesize": f.get("filesize") or f.get("filesize_approx"),
            "acodec": f.get("acodec"),
            "vcodec": f.get("vcodec"),
        })

    return out


def download_video(
    url: str,
    format_selector: str = "best",
    start: Optional[str] = None,
    end: Optional[str] = None,
    output_template: str = "%(title)s.%(ext)s",
    merge_output_format: str = "mp4",
):
    ydl_opts = {
        "format": format_selector,
        "outtmpl": output_template,
        "postprocessors": [],
        "merge_output_format": merge_output_format,
    }

    # Trim / partial download
    if start or end:
        s = parse_time(start) if start else None
        e = parse_time(end) if end else None

        if not s and not e:
            raise ValueError("Invalid start/end time")

        # Python API requires dict format — not CLI-style strings
        ydl_opts["download_sections"] = {
            "*": [
                {
                    "start_time": s if s else None,
                    "end_time": e if e else None,
                }
            ]
        }

    print(f"Starting download: format={format_selector}, sections={ydl_opts.get('download_sections')}")

    if not check_ffmpeg_available():
        print("⚠️ FFmpeg not found — merging and trimming may fail.")
        print("Install FFmpeg and ensure it's in PATH.")

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


def download_subtitles(
    url: str,
    lang: Optional[str] = None,
    write_english_automatic: bool = False,
    output_template: str = "%(title)s.%(ext)s",
    subtitles_format: str = "srt",
):
    ydl_opts = {
        "skip_download": True,
        "writesubtitles": True,
        "subtitlesformat": subtitles_format,
        "outtmpl": output_template,
        "quiet": False,
    }

    if lang and lang.lower() != "all":
        ydl_opts["subtitleslangs"] = [lang]

    if write_english_automatic:
        ydl_opts["writeautomaticsub"] = True

    print(f"Downloading subtitles: lang={lang}, auto={write_english_automatic}")

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


def check_ffmpeg_available() -> bool:
    """yt-dlp needs FFmpeg on PATH to merge/trim."""
    return any(
        os.access(os.path.join(path, "ffmpeg" + (".exe" if os.name == "nt" else "")), os.X_OK)
        for path in os.environ.get("PATH", "").split(os.pathsep)
    )
