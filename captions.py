from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter, SRTFormatter, JSONFormatter
import sys

def download_captions(video_url, output_format='txt', language='en'):
    """
    Download captions from a YouTube video.
    
    Args:
        video_url: YouTube video URL or video ID
        output_format: 'txt', 'srt', or 'json'
        language: Language code (e.g., 'en', 'es', 'fr')
    """
    # Extract video ID from URL
    if 'youtube.com' in video_url or 'youtu.be' in video_url:
        if 'youtu.be/' in video_url:
            video_id = video_url.split('youtu.be/')[-1].split('?')[0]
        else:
            video_id = video_url.split('v=')[-1].split('&')[0]
    else:
        video_id = video_url
    
    print(f"Downloading captions for video ID: {video_id}")
    
    try:
        # Create API instance
        ytt_api = YouTubeTranscriptApi()
        
        # Try to get transcript list and find the requested language
        transcript_list = ytt_api.list(video_id)
        
        # Try to find transcript in the requested language
        try:
            transcript_obj = transcript_list.find_transcript([language])
        except:
            print(f"Language '{language}' not found. Trying English...")
            transcript_obj = transcript_list.find_transcript(['en'])
        
        # Fetch the transcript data
        transcript = transcript_obj.fetch()
        
        # Format based on desired output
        if output_format == 'txt':
            formatter = TextFormatter()
            formatted = formatter.format_transcript(transcript)
            filename = f'{video_id}_captions.txt'
        elif output_format == 'srt':
            formatter = SRTFormatter()
            formatted = formatter.format_transcript(transcript)
            filename = f'{video_id}_captions.srt'
        elif output_format == 'json':
            formatter = JSONFormatter()
            formatted = formatter.format_transcript(transcript, indent=2)
            filename = f'{video_id}_captions.json'
        else:
            print(f"Unknown format: {output_format}")
            return
        
        # Save to file
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(formatted)
        
        print(f"✓ Captions saved to: {filename}")
        print(f"✓ Language: {transcript_obj.language}")
        print(f"✓ Is auto-generated: {transcript_obj.is_generated}")
        
    except Exception as e:
        print(f"Error: {e}")
        print("\nTrying to list available transcripts...")
        
        try:
            ytt_api = YouTubeTranscriptApi()
            transcript_list = ytt_api.list(video_id)
            
            print("\nAvailable transcripts:")
            for transcript in transcript_list:
                print(f"  - {transcript.language} ({transcript.language_code})")
                print(f"    Auto-generated: {transcript.is_generated}")
                print(f"    Translatable: {transcript.is_translatable}")
        except Exception as e2:
            print(f"Could not list transcripts: {e2}")
            print("\nPossible issues:")
            print("1. The video may not have captions available")
            print("2. The video may be age-restricted or private")
            print("3. Try: pip install --upgrade youtube-transcript-api")

if __name__ == "__main__":
    # Example usage
    if len(sys.argv) > 1:
        video_url = sys.argv[1]
        output_format = sys.argv[2] if len(sys.argv) > 2 else 'txt'
        language = sys.argv[3] if len(sys.argv) > 3 else 'en'
    else:
        # Interactive mode
        video_url = input("Enter YouTube URL or video ID: ")
        output_format = input("Enter format (txt/srt/json) [txt]: ") or 'txt'
        language = input("Enter language code [en]: ") or 'en'
    
    download_captions(video_url, output_format, language)