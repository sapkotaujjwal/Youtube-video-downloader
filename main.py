import yt_dlp
import os
import sys

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def format_filesize(bytes):
    """Convert bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024.0:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024.0
    return f"{bytes:.2f} TB"

def format_duration(seconds):
    """Convert seconds to HH:MM:SS format"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"

def get_video_info(url):
    """Fetch all available video information and formats"""
    print("\n[*] Fetching video information...")
    
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return info
    except Exception as e:
        print(f"\n[ERROR] Failed to fetch video info: {str(e)}")
        return None

def display_video_info(info):
    """Display video information in a nice format"""
    print("\n" + "="*70)
    print("VIDEO INFORMATION")
    print("="*70)
    print(f"Title: {info.get('title', 'N/A')}")
    print(f"Uploader: {info.get('uploader', 'N/A')}")
    print(f"Duration: {format_duration(info.get('duration', 0))}")
    print(f"Views: {info.get('view_count', 'N/A'):,}")
    print(f"Upload Date: {info.get('upload_date', 'N/A')}")
    print("="*70)

def display_formats(info):
    """Display available video formats with quality, size, and format info"""
    print("\n" + "="*70)
    print("AVAILABLE FORMATS")
    print("="*70)
    
    formats = info.get('formats', [])
    
    # Filter and organize formats
    video_formats = []
    audio_formats = []
    
    for f in formats:
        format_id = f.get('format_id')
        ext = f.get('ext')
        resolution = f.get('resolution', 'audio only')
        filesize = f.get('filesize') or f.get('filesize_approx', 0)
        vcodec = f.get('vcodec', 'none')
        acodec = f.get('acodec', 'none')
        fps = f.get('fps', 0)
        
        if vcodec != 'none' and acodec != 'none':  # Video with audio
            video_formats.append({
                'id': format_id,
                'ext': ext,
                'resolution': resolution,
                'size': filesize,
                'fps': fps,
                'type': 'video+audio'
            })
        elif vcodec != 'none':  # Video only
            video_formats.append({
                'id': format_id,
                'ext': ext,
                'resolution': resolution,
                'size': filesize,
                'fps': fps,
                'type': 'video only'
            })
        elif acodec != 'none':  # Audio only
            audio_formats.append({
                'id': format_id,
                'ext': ext,
                'resolution': resolution,
                'size': filesize,
                'type': 'audio only'
            })
    
    # Display video formats
    print("\n[VIDEO FORMATS]")
    print(f"{'No.':<5} {'Format ID':<12} {'Quality':<20} {'Size':<12} {'Type':<15}")
    print("-"*70)
    
    for idx, fmt in enumerate(video_formats, 1):
        size_str = format_filesize(fmt['size']) if fmt['size'] > 0 else 'Unknown'
        fps_str = f"{fmt['fps']}fps" if fmt['fps'] else ""
        quality = f"{fmt['resolution']} {fps_str}".strip()
        print(f"{idx:<5} {fmt['id']:<12} {quality:<20} {size_str:<12} {fmt['type']:<15}")
    
    # Display audio formats
    if audio_formats:
        print("\n[AUDIO FORMATS]")
        print(f"{'No.':<5} {'Format ID':<12} {'Quality':<20} {'Size':<12} {'Type':<15}")
        print("-"*70)
        for idx, fmt in enumerate(audio_formats, len(video_formats) + 1):
            size_str = format_filesize(fmt['size']) if fmt['size'] > 0 else 'Unknown'
            print(f"{idx:<5} {fmt['id']:<12} {fmt['resolution']:<20} {size_str:<12} {fmt['type']:<15}")
    
    print("="*70)
    return video_formats + audio_formats

def get_time_input(prompt, max_duration):
    """Get time input from user in MM:SS or HH:MM:SS format"""
    while True:
        time_str = input(prompt).strip()
        if not time_str:
            return None
        
        try:
            parts = time_str.split(':')
            if len(parts) == 2:  # MM:SS
                minutes, seconds = map(int, parts)
                total_seconds = minutes * 60 + seconds
            elif len(parts) == 3:  # HH:MM:SS
                hours, minutes, seconds = map(int, parts)
                total_seconds = hours * 3600 + minutes * 60 + seconds
            else:
                print("[ERROR] Invalid format. Use MM:SS or HH:MM:SS")
                continue
            
            if total_seconds > max_duration:
                print(f"[ERROR] Time exceeds video duration ({format_duration(max_duration)})")
                continue
            
            return total_seconds
        except ValueError:
            print("[ERROR] Invalid time format. Use numbers only (e.g., 01:30 or 00:01:30)")

def progress_hook(d):
    """Display download progress"""
    if d['status'] == 'downloading':
        percent = d.get('_percent_str', 'N/A')
        speed = d.get('_speed_str', 'N/A')
        eta = d.get('_eta_str', 'N/A')
        print(f"\r[*] Downloading: {percent} | Speed: {speed} | ETA: {eta}", end='')
    elif d['status'] == 'finished':
        print("\n[*] Download finished, processing...")

def download_video(url, format_id, output_name, start_time=None, end_time=None):
    """Download video with specified parameters"""
    output_path = 'downloads'
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    ydl_opts = {
        'format': format_id,
        'outtmpl': os.path.join(output_path, f'{output_name}.%(ext)s'),
        'progress_hooks': [progress_hook],
    }
    
    # Add time range if specified
    if start_time is not None or end_time is not None:
        postprocessor_args = []
        if start_time is not None:
            postprocessor_args.extend(['-ss', str(start_time)])
        if end_time is not None:
            postprocessor_args.extend(['-to', str(end_time)])
        
        ydl_opts['postprocessor_args'] = postprocessor_args
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }]
    
    try:
        print("\n[*] Starting download...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print(f"\n[SUCCESS] Video downloaded successfully to '{output_path}' folder!")
        return True
    except Exception as e:
        print(f"\n[ERROR] Download failed: {str(e)}")
        return False

def main():
    clear_screen()
    print("="*70)
    print(" "*20 + "YOUTUBE VIDEO DOWNLOADER")
    print("="*70)
    
    # Step 1: Get video URL
    url = input("\n[1] Enter YouTube video URL: ").strip()
    if not url:
        print("[ERROR] No URL provided!")
        return
    
    # Step 2: Fetch video info
    info = get_video_info(url)
    if not info:
        return
    
    # Step 3: Display video information
    display_video_info(info)
    
    # Step 4: Display available formats
    formats = display_formats(info)
    
    # Step 5: Select quality
    while True:
        try:
            choice = input("\n[2] Select format number (or press Enter for best quality): ").strip()
            if not choice:
                format_id = 'best'
                break
            choice_num = int(choice)
            if 1 <= choice_num <= len(formats):
                format_id = formats[choice_num - 1]['id']
                break
            else:
                print(f"[ERROR] Please enter a number between 1 and {len(formats)}")
        except ValueError:
            print("[ERROR] Please enter a valid number")
    
    # Step 6: Select time range
    duration = info.get('duration', 0)
    print(f"\n[3] Video duration: {format_duration(duration)}")
    print("     Download options:")
    print("     1. Full video")
    print("     2. Custom time range")
    
    time_choice = input("     Select option (1 or 2): ").strip()
    
    start_time = None
    end_time = None
    
    if time_choice == '2':
        print("\n     Enter time in MM:SS or HH:MM:SS format (or press Enter to skip)")
        start_time = get_time_input("     Start time (e.g., 01:30): ", duration)
        end_time = get_time_input("     End time (e.g., 05:45): ", duration)
        
        if start_time and end_time and start_time >= end_time:
            print("[ERROR] Start time must be before end time!")
            return
    
    # Step 7: Get output filename
    default_title = info.get('title', 'video')
    # Clean filename
    default_title = "".join(c for c in default_title if c.isalnum() or c in (' ', '-', '_')).strip()
    
    print(f"\n[4] Default filename: {default_title}")
    custom_name = input("     Enter custom filename (or press Enter to use default): ").strip()
    output_name = custom_name if custom_name else default_title
    
    # Step 8: Confirm and download
    print("\n" + "="*70)
    print("DOWNLOAD SUMMARY")
    print("="*70)
    print(f"Video: {info.get('title')}")
    print(f"Quality: {format_id}")
    if start_time or end_time:
        start_str = format_duration(start_time) if start_time else "00:00"
        end_str = format_duration(end_time) if end_time else format_duration(duration)
        print(f"Time range: {start_str} to {end_str}")
    else:
        print(f"Time range: Full video")
    print(f"Output filename: {output_name}")
    print("="*70)
    
    download_video(url, format_id, output_name, start_time, end_time)
    # confirm = input("\nProceed with download? (y/n): ").strip().lower()
    # if confirm == 'y':
    # else:
    #     print("[*] Download cancelled.")

    

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[*] Download cancelled by user.")
        sys.exit(0)