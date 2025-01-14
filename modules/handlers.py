import sys
import logging
import time
import zulip
from langchain_community.document_loaders import YoutubeLoader
from langchain_community.document_loaders.youtube import TranscriptFormat
from youtube_transcript_api import YouTubeTranscriptApi
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
        data = YouTubeTranscriptApi.get_transcript(video_id)

        concatenated_text = ' '.join(item['text'] for item in data)

        print(concatenated_text)
