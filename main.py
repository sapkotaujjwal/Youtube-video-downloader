import argparse
import sys
from yt_downloader import list_formats, download_video, download_subtitles, check_ffmpeg_available


def main():
    parser = argparse.ArgumentParser(description="YouTube video & captions downloader (supports section downloads)")
    parser.add_argument("url", help="YouTube video URL")
    parser.add_argument("-f", "--format", help="Format id or yt-dlp format selector (e.g. best, mp4, 137+bestaudio)")
    parser.add_argument("-i", "--interactive", action="store_true", help="Interactively choose a format from available formats")
    parser.add_argument("--start", help="Start time (seconds or HH:MM:SS) for section download")
    parser.add_argument("--end", help="End time (seconds or HH:MM:SS) for section download")
    parser.add_argument("--captions", action="store_true", help="Download captions (if available). If used without --captions-only, captions will be saved alongside video")
    parser.add_argument("--captions-only", action="store_true", help="Only download captions, skip video download")
    parser.add_argument("--lang", default="all", help="Subtitle language (ISO code) or 'all' (default: all)")
    parser.add_argument("--auto", action="store_true", help="Also try automatic subtitles (when available)")
    parser.add_argument("-o", "--output", default="%(title)s.%(ext)s", help="Output template (default: %(title)s.%(ext)s)")

    args = parser.parse_args()

    if not check_ffmpeg_available():
        print("Install ffmpeg and come back")
        return

    if args.interactive:
        formats = list_formats(args.url)
        print("Available formats (format_id / ext / resolution / note):")
        for f in formats:
            print(f"{f['format_id']}  {f['ext']}  {f['resolution']}  {f['note']}")
        chosen = input("Enter desired format_id (or 'best' to pick best): ").strip()
        if chosen:
            args.format = chosen

    if args.captions_only:
        # only subtitles
        download_subtitles(args.url, lang=args.lang, write_english_automatic=args.auto, output_template=args.output)
        sys.exit(0)

    # if captions requested but not only, do video then subtitles (subtitles saved alongside)
    fmt = args.format or "best"
    download_video(args.url, format_selector=fmt, start=args.start, end=args.end, output_template=args.output)

    if args.captions:
        download_subtitles(args.url, lang=args.lang, write_english_automatic=args.auto, output_template=args.output)


if __name__ == "__main__":
    main()
