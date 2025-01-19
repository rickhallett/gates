import sys
import logging
import time
import os
import json
import openai
import zulip
from pathlib import Path
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
import boto3
from modules.utils import upload_file, download_audio_file, get_s3_url_and_destination
from data_types import Message
from modules.config import create_focus_client
import threading
from datetime import datetime
import dotenv
from modules.secrets import get_secret

dotenv.load_dotenv()

message_logger = logging.getLogger('message_logger')
event_logger = logging.getLogger('event_logger')

def on_event(event):
    event_logger.info(str(event))
    pass

class MessageHandler():
    def __init__(self, client: zulip.Client):
        self.client = client
        self.message = None;
        self.start_countdown()

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
        stream_name = self.message.display_recipient
        topic_name = self.message.subject

        self.process_links(
            links=self.message.youtube_links,
            link_type='video',
            transcribe_method=self.transcribe_youtube_video,
            stream_name=stream_name,
            topic_name=topic_name
        )

        self.process_links(
            links=self.message.audio_links,
            link_type='audio file',
            transcribe_method=self.transcribe_audio_file,
            stream_name=stream_name,
            topic_name=topic_name
        )

    def process_links(self, links, link_type, transcribe_method, stream_name, topic_name):
        if not links:
            return

        transcribed = []
        self.client.send_message({
            "type": "stream",
            "to": stream_name,
            "topic": topic_name,
            "content": f"Transcribing {len(links)} {link_type}{'' if len(links) == 1 else 's'}, please wait."
        })

        for link in links:
            try:
                success = transcribe_method(link, stream_name, topic_name)
                if success:
                    transcribed.append(link)
            except Exception as e:
                self.client.send_message({
                    "type": "stream",
                    "to": stream_name,
                    "topic": topic_name,
                    "content": f"Error transcribing {link}: {str(e)}"
                })

        if (len(transcribed) == len(links)):
            self.client.send_message({
                "type": "stream",
                "to": stream_name,
                "topic": topic_name,
                "content": f"All {link_type}s have been processed."
            })
        else:
            self.client.send_message({
                "type": "stream",
                "to": stream_name,
                "topic": topic_name,
                "content": f"Some {link_type}s failed to process."
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

    def transcribe_audio_file(self, audio_url: str, stream_name: str, topic_name: str) -> bool:
        s3_object_name, destination_dir = get_s3_url_and_destination(audio_url)
        try:
            self.client.send_message({
                "type": "stream",
                "to": stream_name,
                "topic": topic_name,
                "content": f"Downloading audio from {s3_object_name}"
            })
            download_audio_file(s3_object_name, f"{destination_dir}/{Path(audio_url).name}")

            stem = Path(audio_url).stem
            ext = Path(audio_url).suffix

            client = openai.Client(
                api_key=get_secret() if os.getenv("ENVIRONMENT") == "production" else os.getenv("OPENAI_API_KEY")
            )
            with open(f"{destination_dir}/{stem}{ext}", "rb") as audio_file:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                )

            self.client.send_message({
                "type": "stream",
                "to": "voice-notes",
                "topic": "random-thoughts",
                "content": f"Transcribed {stem}{ext} \n\n Raw transcript: {transcript.text} \n\n Processing transcript..."
            })

            self.transcribe_content(
                content=transcript.text,
                prompt_template_path="prompts/memo.xml",
                output_stem=stem,
                stream_name="voice-notes",
                topic_name="random-thoughts"
            )

            return True

        except Exception as e:
            raise Exception(f"Error processing audio file: {str(e)}")

    def transcribe_youtube_video(self, video_url: str, stream_name: str, topic_name: str):
        try:
            video_id = video_url.split("v=")[1]
            data = YouTubeTranscriptApi.get_transcript(video_id)
            concatenated_text = ' '.join(item['text'] for item in data)

            self.transcribe_content(
                content=concatenated_text,
                prompt_template_path="prompts/transcribe.md",
                output_stem=video_id,
                stream_name=stream_name,
                topic_name=topic_name
            )

        except (TranscriptsDisabled, NoTranscriptFound) as e:
            error_message = f"Could not transcribe {video_id}: {str(e)}"
            self.client.send_message({
                "type": "stream",
                "to": stream_name,
                "topic": topic_name,
                "content": self.remove_url_from_content(error_message, video_id)
            })
        except Exception as e:
            error_message = f"Error processing {video_id}: {str(e)}"
            self.client.send_message({
                "type": "stream",
                "to": stream_name,
                "topic": topic_name,
                "content": self.remove_url_from_content(error_message, video_id)
            })

    def remove_url_from_content(self, content, video_id):
        return content.replace(f"https://www.youtube.com/watch?v={video_id}", "")

    def transcribe_content(self, content, prompt_template_path, output_stem, stream_name, topic_name):
        with open(prompt_template_path, "r") as f:
            prompt_template = f.read()

        prompt = prompt_template.replace("{{transcript}}", content)

        client = openai.Client()
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that formats transcripts into well-structured markdown documents."},
                {"role": "user", "content": prompt}
            ]
        )

        output_dir = Path("transcripts")
        output_dir.mkdir(exist_ok=True)
        response_path = output_dir / f"{output_stem}_response.json"
        with open(response_path, "w") as f:
            json.dump(response.model_dump(), f, indent=2)

        markdown_content = response.choices[0].message.content
        final_content = self.wrap_markdown(markdown_content)

        markdown_path = output_dir / f"{output_stem}-{time.strftime('%Y-%m-%d-%H-%M-%S')}.md"
        with open(markdown_path, "w") as f:
            f.write(final_content)

        uploaded = upload_file(markdown_path, 'ark-comms-main', f"{stream_name}/{markdown_path.name}")

        self.client.send_message({
            "type": "stream",
            "to": stream_name,
            "topic": topic_name,
            "content": f"Transcript for {output_stem} has been processed and saved.\n\n```md\n{final_content}\n```"
        })

    def wrap_markdown(self, markdown_content):
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
        return '\n'.join(wrapped_content)
    
    def start_countdown(self):
        def countdown_loop():
            focus_client = create_focus_client()
            deadline = datetime(2025, 1, 22, 13, 0, 0)

            while True:
                now = datetime.now()
                if now >= deadline:
                    focus_client.send_message({
                        "type": "stream",
                        "to": "countdown",
                        "topic": "t-minus",
                        "content": "The deadline has passed. Judging has begun."
                    })
                    break

                # Calculate remaining time
                time_remaining = deadline - now
                days = time_remaining.days
                hours, remainder = divmod(time_remaining.seconds, 3600)
                minutes, _ = divmod(remainder, 60)
                
                # Print remaining time
                focus_client.send_message({
                    "type": "stream",
                    "to": "countdown",
                    "topic": "t-minus",
                    "content": f"Time remaining: {days} days, {hours} hours, {minutes} minutes."
                })
                
                # Wait for 30 minutes
                time.sleep(30 * 60)

        # Start the countdown in a separate thread
        countdown_thread = threading.Thread(target=countdown_loop, name="countdown_thread", daemon=True)
        countdown_thread.start()

