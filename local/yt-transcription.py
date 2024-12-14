from bs4 import BeautifulSoup
import requests
from youtube_transcript_api import YouTubeTranscriptApi
from googleapiclient.discovery import build
import os
from dotenv import load_dotenv
import re

load_dotenv()

def remove_timestamps(transcript_entries):
    """
    Remove timestamps and return a clean transcript.
    :param transcript_entries: List of transcript dictionaries from YouTubeTranscriptApi.
    :return: String containing the transcript without timestamps.
    """
    transcript_text = " ".join([entry['text'] for entry in transcript_entries])
    return transcript_text

def save_to_file(content, filename):
    """
    Save the given content to a text file.
    :param content: The content to save.
    :param filename: The name of the file to save the content.
    """
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(content)
    print(f"Transcript saved to {filename}")

def transcribe(video_id):
    try:
        # Fetch the transcript
        transcript = YouTubeTranscriptApi.get_transcript(video_id)

        # Process the transcript to remove timestamps
        cleaned_transcript = remove_timestamps(transcript)
        save_to_file(cleaned_transcript, f"./samples/prompt_guides/{video_id}_transcript.txt")
    except Exception as e:
        print("Failure")

def get_vid_ids():
    list_id = "PLkDaE6sCZn6FNC6YRfRQc_FbeQrF8BwGI"
    video_ids = get_video_ids_from_playlist(os.getenv('google_key'), list_id)
    
    for id in video_ids:
        transcribe(id)

def get_video_ids_from_playlist(api_key, playlist_id):
    """
    Retrieve all video IDs from a YouTube playlist.
    :param api_key: Your YouTube Data API key.
    :param playlist_id: The ID of the YouTube playlist.
    :return: List of video IDs.
    """
    youtube = build("youtube", "v3", developerKey=api_key)
    video_ids = []
    next_page_token = None

    while True:
        response = youtube.playlistItems().list(
            part="contentDetails",
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page_token
        ).execute()

        video_ids.extend(item["contentDetails"]["videoId"] for item in response["items"])
        next_page_token = response.get("nextPageToken")

        if not next_page_token:
            break

    return video_ids

def get_video_title(video_id, api_key):
    """
    Fetch the title of a YouTube video using its video ID.
    :param video_id: YouTube video ID
    :param api_key: YouTube Data API key
    :return: Video title as a string
    """
    youtube = build("youtube", "v3", developerKey=api_key)
    
    # Call the API to get video details
    request = youtube.videos().list(
        part="snippet",
        id=video_id
    )
    response = request.execute()
    
    if response['items']:
        # Extract title from the response
        video_title = response['items'][0]['snippet']['title']
        return video_title
    else:
        return None
    
def sanitize_filename(filename):
    """
    Remove invalid characters from a filename.
    :param filename: The filename to sanitize.
    :return: A sanitized filename string.
    """
    # Remove any characters that are not allowed in filenames
    sanitized_filename = re.sub(r'[\\/*?:"<>|]', "", filename)
    return sanitized_filename

get_vid_ids()
