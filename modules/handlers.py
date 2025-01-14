import sys
import logging
import time
import os
import json
from pathlib import Path
import openai
import zulip
from langchain_community.document_loaders import YoutubeLoader
from langchain_community.document_loaders.youtube import TranscriptFormat
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
from pytube import YouTube
# the base class to inherit from when creating your own formatter.
from youtube_transcript_api.formatters import Formatter

# some provided subclasses, each outputs a different string format.
from youtube_transcript_api.formatters import JSONFormatter
from youtube_transcript_api.formatters import TextFormatter
from youtube_transcript_api.formatters import WebVTTFormatter
from youtube_transcript_api.formatters import SRTFormatter
from youtube_transcript_api.formatters import PrettyPrintFormatter

from data_types import Message

message_logger = logging.getLogger('message_logger')
event_logger = logging.getLogger('event_logger')

def on_event(event):
    event_logger.info(str(event))
    pass



def act_on_message(message):
    if message.youtube_links:
        for link in message.youtube_links:
            print(link)
    if message.audio_links:
        for link in message.audio_links:
            print(link)

class MessageHandler():
    def __init__(self, client: zulip.Client):
        self.client = client
        self.message = None;

    def create_message(self, message):
        self.message = Message(**message)
        return self.message
    
    def log_message_to_file(self):
        message_logger.info(str(self.message) + "\n\n")

    def log_message_to_console(self):
        sys.stdout.write(
        f"""
        {self.message.sender_full_name}:
        {self.message.content}
        {len(self.message.youtube_links)} youtube links
        """)

    def on_message(self, message):
        self.create_message(message)
        self.log_message_to_file()
        self.log_message_to_console()
        self.handle_message()

    def handle_message(self):
        if self.message.youtube_links:
            self.client.send_message({
                "type": "stream",
                "to": "youtube",
                "topic": "ai",
                "content": f"Transcribing {len(self.message.youtube_links)} video{'' if len(self.message.youtube_links) == 1 else 's'}, please wait."
            })
            for link in self.message.youtube_links:
                video_id = link.split('?v=')[1]
                self.client.send_message({
                    "type": "stream",
                    "to": "youtube",
                    "topic": "ai",
                    "content": f"{video_id} is being transcribed."
                })
                self.transcribe_youtube_video(video_id)
                time.sleep(2)
            self.client.send_message({
                "type": "stream",
                "to": "youtube",
                "topic": "ai",
                "content": f"All videos have been transcribed."
            })

    def transcribe_youtube_video(self, video_id: str):
        try:
            # Create output directory if it doesn't exist
            output_dir = Path("transcripts")
            output_dir.mkdir(exist_ok=True)
            
            # Load the prompt template
            with open("prompts/transcribe.md", "r") as f:
                prompt_template = f.read()
            
            # Get transcript
            data = YouTubeTranscriptApi.get_transcript(video_id)
            concatenated_text = ' '.join(item['text'] for item in data)
            
            # Replace placeholder in prompt template
            prompt = prompt_template.replace("{{transcript}}", concatenated_text)
            
            # Call OpenAI API
            client = openai.Client()
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that formats YouTube transcripts into well-structured markdown documents."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Save raw response
            response_path = output_dir / f"{video_id}_response.json"
            with open(response_path, "w") as f:
                json.dump(response.model_dump(), f, indent=2)
            
            # Extract markdown content and wrap to 70 chars
            markdown_content = response.choices[0].message.content
            
            # Wrap markdown content to 70 chars while preserving formatting
            wrapped_content = []
            for line in markdown_content.split('\n'):
                # Preserve headers, lists, and other markdown formatting
                if line.startswith(('#', '-', '*', '>', '```')) or not line.strip():
                    wrapped_content.append(line)
                else:
                    # Wrap normal text to 70 chars
                    words = line.split()
                    current_line = []
                    current_length = 0
                    
                    for word in words:
                        if current_length + len(word) + 1 <= 70:
                            current_line.append(word)
                            current_length += len(word) + 1
                        else:
                            wrapped_content.append(' '.join(current_line))
                            current_line = [word]
                            current_length = len(word)
                    
                    if current_line:
                        wrapped_content.append(' '.join(current_line))
            
            final_content = '\n'.join(wrapped_content)
            
            # Save markdown
            markdown_path = output_dir / f"{video_id}.md"
            with open(markdown_path, "w") as f:
                f.write(final_content)
            
            # Send to Zulip
            self.client.send_message({
                "type": "stream",
                "to": "youtube",
                "topic": "ai",
                "content": f"Transcript for {video_id} has been processed and saved.\n\n{markdown_content}"
            })
            
        except (TranscriptsDisabled, NoTranscriptFound) as e:
            error_message = f"Could not transcribe {video_id}: {str(e)}"
            self.client.send_message({
                "type": "stream",
                "to": "youtube",
                "topic": "ai",
                "content": error_message
            })
        except Exception as e:
            error_message = f"Error processing {video_id}: {str(e)}"
            self.client.send_message({
                "type": "stream",
                "to": "youtube",
                "topic": "ai",
                "content": error_message
            })
