import yt_dlp
import sys

def list_captions(url):
    ydl_opts = {
        "quiet": True,
        "skip_download": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    subtitles = info.get("subtitles", {})
    auto_subs = info.get("automatic_captions", {})

    all_caps = []

    print("\nAvailable captions:\n")

    index = 1
    for lang, tracks in subtitles.items():
        print(f"{index}. {lang} (manual)")
        all_caps.append((lang, False))
        index += 1

    for lang, tracks in auto_subs.items():
        print(f"{index}. {lang} (auto-generated)")
        all_caps.append((lang, True))
        index += 1

    if not all_caps:
        print("❌ No captions available.")
        sys.exit()

    return all_caps


def download_caption(url, lang, is_auto):
    ydl_opts = {
        "skip_download": True,
        "writesubtitles": not is_auto,
        "writeautomaticsub": is_auto,
        "subtitleslangs": [lang],
        "subtitlesformat": "srt",
        "outtmpl": "%(title)s.%(ext)s",
        "quiet": False,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


def main():
    url = input("Paste YouTube video URL: ").strip()

    captions = list_captions(url)

    choice = int(input("\nSelect caption number to download: "))
    if choice < 1 or choice > len(captions):
        print("❌ Invalid selection")
        return

    lang, is_auto = captions[choice - 1]
    download_caption(url, lang, is_auto)

    print("\n✅ Caption downloaded successfully!")


if __name__ == "__main__":
    main()
