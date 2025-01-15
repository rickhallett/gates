import sys
import subprocess
import logging
import time
import os
import json
import requests
from pathlib import Path
import openai
import zulip
import boto3
from typing import Optional
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

from botocore.exceptions import ClientError


def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        print(f"Uploading {file_name} to {bucket} as {object_name}")
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True

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
{self.message.sender_full_name} - {time.strftime("%Y-%m-%d %H:%M:%S")}:
{self.message.content}
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
            
            self.client.send_message({
                "type": "stream",
                "to": "youtube",
                "topic": "ai",
                "content": f"All videos have been transcribed."
            })
        
        if self.message.audio_links:
            self.client.send_message({
                "type": "stream",
                "to": "voice-notes",
                "topic": "random-thoughts",
                "content": f"Transcribing {len(self.message.audio_links)} audio file{'' if len(self.message.audio_links) == 1 else 's'}, please wait."
            })
            
            for link in self.message.audio_links:
                try:
                    self.transcribe_audio_file(link)
                except Exception as e:
                    self.client.send_message({
                        "type": "stream",
                        "to": "voice-notes",
                        "topic": "random-thoughts",
                        "content": f"Error transcribing {link}: {str(e)}"
                    })

            self.client.send_message({
                "type": "stream",
                "to": "voice-notes",
                "topic": "random-thoughts",
                "content": f"All audio files have been processed."
            })

    def get_s3_url_and_destination(self, audio_link):
        # Create a URL compatible with S3
        s3_object_name = "/".join(audio_link.split("/")[2:])
        
        # Extract the directory path from the S3 object name
        destination_dir = os.path.join("audio", os.path.dirname(s3_object_name))

        # check dir exists
        if not os.path.exists(destination_dir):
            os.makedirs(destination_dir)
        
        return s3_object_name, destination_dir

    def download_audio_file(self, s3_object_name: str):
        """Download audio file from S3"""
        try:
            s3 = boto3.client('s3')
            with open(f"audio/{s3_object_name}", "wb") as f:
                s3.download_fileobj(Bucket='ark-comms-main', Key=s3_object_name, Fileobj=f)
                f.close()
        except Exception as e:
            raise Exception(f"Failed to download audio file: {str(e)}")

    def transcribe_audio_file(self, audio_url: str):
        """Transcribe audio file using OpenAI Whisper API"""
        s3_object_name, destination_dir = self.get_s3_url_and_destination(audio_url)
        try:
            # Create output directory if it doesn't exist
            output_dir = Path("transcripts")
            output_dir.mkdir(exist_ok=True)
            
            # Download the audio file
            self.client.send_message({
                "type": "stream",
                "to": "voice-notes",
                "topic": "random-thoughts",
                "content": f"Downloading audio from {s3_object_name}"
            })
            
            self.download_audio_file(s3_object_name)

            # Get filename from URL
            stem = Path(audio_url).stem
            ext = Path(audio_url).suffix

            # Save the audio file
            # with open(f"{stem}{ext}", "wb") as f:
            #     f.write(audio_data)

            # Run ffmpeg to check if the file is valid and capture the output
            # result = subprocess.run(
            #     ["ffmpeg", "-i", f"{stem}{ext}", "-f", "null", "-"],
            #     capture_output=True,
            #     text=True
            # )
            
            # Print the standard output and standard error
            # print("stdout:", result.stdout)
            # print("stderr:", result.stderr)
            
            
            
            # Transcribe with Whisper
            self.client.send_message({
                "type": "stream",
                "to": "voice-notes",
                "topic": "random-thoughts",
                "content": f"Transcribing {stem}{ext}"
            })
            
            client = openai.Client()
            
            with open(f"{destination_dir}/{stem}{ext}", "rb") as audio_file:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                )
            
            # os.remove(f"{stem}{ext}")

            self.client.send_message({
                "type": "stream",
                "to": "voice-notes",
                "topic": "random-thoughts",
                "content": f"Transcribed {stem}{ext}. Raw response: {transcript}"
            })
            
            # Load the prompt template
            with open("prompts/memo.xml", "r") as f:
                prompt_template = f.read()
            
            # Replace placeholder in prompt template
            prompt = prompt_template.replace("{{transcript}}", transcript.text)
            
            # Process with ChatGPT
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that formats audio transcripts into well-structured markdown documents."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Save raw response
            response_path = output_dir / f"{stem}_response.json"
            with open(response_path, "w") as f:
                json.dump(response.model_dump(), f, indent=2)
            
            # Extract and wrap markdown content
            markdown_content = response.choices[0].message.content
            
            # Wrap markdown content to 70 chars while preserving formatting
            wrapped_content = []
            for line in markdown_content.split('\n'):
                if line.startswith(('#', '-', '*', '>', '```')) or not line.strip():
                    wrapped_content.append(line)
                else:
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
            print("Saving markdown")
            markdown_path = output_dir / f"{stem}-{time.strftime('%Y-%m-%d-%H-%M-%S')}.md"
            with open(markdown_path, "w") as f:
                f.write(final_content)
            
            print("Markdown saved")

            # Upload to S3
            uploaded = upload_file(markdown_path, 'ark-comms-main', f"voice-notes/{markdown_path}")

            if uploaded:
                print("Markdown uploaded to S3")
            else:
                print("Failed to upload markdown to S3")
            
            print("Sending confirmation to Zulip")
            # Send to Zulip
            self.client.send_message({
                "type": "stream",
                "to": "voice-notes",
                "topic": "random-thoughts",
                "content": f"Transcript for {stem} has been processed and saved.\n\n```md\n{final_content}\n```"
            })
            
        except Exception as e:
            raise Exception(f"Error processing audio file: {str(e)}")

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
