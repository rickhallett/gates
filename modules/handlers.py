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
from typing import Any

dotenv.load_dotenv()

message_logger = logging.getLogger("message_logger")
event_logger = logging.getLogger("event_logger")


def on_event(event):
    event_logger.info(str(event))
    pass


class MessageHandler:
    def __init__(self, client: zulip.Client):
        self.client = client
        self.openai_client = openai.Client(
            api_key=get_secret()
            if os.getenv("ENVIRONMENT") == "production"
            else os.getenv("OPENAI_API_KEY")
        )
        self.message = None
        self.start_countdown()
        self.run_standup_monitoring()

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
"""
        )

    def on_message(self, message):
        self.create_message(message)
        self.log_message_to_file()
        self.log_message_to_console()
        self.handle_message()

    def handle_message(self):
        stream_name = self.message.display_recipient
        topic_name = self.message.subject

        if os.getenv("ENVIRONMENT") != "production":
            self.process_links(
                links=self.message.youtube_links,
                link_type="video",
                transcribe_method=self.transcribe_youtube_video,
                stream_name=stream_name,
                topic_name=topic_name,
            )

        self.process_links(
            links=self.message.audio_links,
            link_type="audio file",
            transcribe_method=self.transcribe_audio_file,
            stream_name=stream_name,
            topic_name=topic_name,
        )

    def process_links(
        self, links, link_type, transcribe_method, stream_name, topic_name
    ):
        if not links:
            return

        transcribed = []
        self.client.send_message(
            {
                "type": "stream",
                "to": stream_name,
                "topic": topic_name,
                "content": f"Transcribing {len(links)} {link_type}{'' if len(links) == 1 else 's'}, please wait.",
            }
        )

        for link in links:
            try:
                success = transcribe_method(link, stream_name, topic_name)
                if success:
                    transcribed.append(link)
                if os.getenv("ENVIRONMENT") == "production":
                    transcribed.append(link)
            except Exception as e:
                self.client.send_message(
                    {
                        "type": "stream",
                        "to": stream_name,
                        "topic": topic_name,
                        "content": f"Error transcribing {link}: {str(e)}",
                    }
                )

        if len(transcribed) == len(links):
            self.client.send_message(
                {
                    "type": "stream",
                    "to": stream_name,
                    "topic": topic_name,
                    "content": f"All {link_type}s have been processed.",
                }
            )
        else:
            self.client.send_message(
                {
                    "type": "stream",
                    "to": stream_name,
                    "topic": topic_name,
                    "content": f"Some {link_type}s failed to process.",
                }
            )

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
            s3 = boto3.client("s3")
            with open(f"audio/{s3_object_name}", "wb") as f:
                s3.download_fileobj(
                    Bucket="ark-comms-main", Key=s3_object_name, Fileobj=f
                )
                f.close()
        except Exception as e:
            raise Exception(f"Failed to download audio file: {str(e)}")

    def transcribe_audio_file(
        self, audio_url: str, stream_name: str, topic_name: str
    ) -> bool:
        s3_object_name, destination_dir = get_s3_url_and_destination(audio_url)
        try:
            self.client.send_message(
                {
                    "type": "stream",
                    "to": stream_name,
                    "topic": topic_name,
                    "content": f"Downloading audio from {s3_object_name}",
                }
            )
            download_audio_file(
                s3_object_name, f"{destination_dir}/{Path(audio_url).name}"
            )

            stem = Path(audio_url).stem
            ext = Path(audio_url).suffix

            with open(f"{destination_dir}/{stem}{ext}", "rb") as audio_file:
                transcript = self.openai_client.audio.transcriptions.create(
                    model="whisper-1", file=audio_file
                )

            self.client.send_message(
                {
                    "type": "stream",
                    "to": "voice-notes",
                    "topic": "random-thoughts",
                    "content": f"Transcribed {stem}{ext} \n\n Raw transcript: {transcript.text} \n\n Processing transcript...",
                }
            )

            self.transcribe_content(
                content=transcript.text,
                prompt_template_path="prompts/memo.xml",
                output_stem=stem,
                stream_name="voice-notes",
                topic_name="random-thoughts",
            )

            return True

        except Exception as e:
            raise Exception(f"Error processing audio file: {str(e)}")

    def transcribe_youtube_video(
        self, video_url: str, stream_name: str, topic_name: str
    ):
        try:
            video_id = video_url.split("v=")[1]
            data = YouTubeTranscriptApi.get_transcript(video_id)
            concatenated_text = " ".join(item["text"] for item in data)

            self.transcribe_content(
                content=concatenated_text,
                prompt_template_path="prompts/transcribe.md",
                output_stem=video_id,
                stream_name=stream_name,
                topic_name=topic_name,
            )

        except (TranscriptsDisabled, NoTranscriptFound) as e:
            error_message = f"Could not transcribe {video_id}: {str(e)}"
            self.client.send_message(
                {
                    "type": "stream",
                    "to": stream_name,
                    "topic": topic_name,
                    "content": self.remove_url_from_content(error_message, video_id),
                }
            )
        except Exception as e:
            error_message = f"Error processing {video_id}: {str(e)}"
            self.client.send_message(
                {
                    "type": "stream",
                    "to": stream_name,
                    "topic": topic_name,
                    "content": self.remove_url_from_content(error_message, video_id),
                }
            )

    def remove_url_from_content(self, content, video_id):
        return content.replace(f"https://www.youtube.com/watch?v={video_id}", "")

    def transcribe_content(
        self, content, prompt_template_path, output_stem, stream_name, topic_name
    ):
        with open(prompt_template_path, "r") as f:
            prompt_template = f.read()

        prompt = prompt_template.replace("{{transcript}}", content)

        client = openai.Client()
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that formats transcripts into well-structured markdown documents.",
                },
                {"role": "user", "content": prompt},
            ],
        )

        output_dir = Path("transcripts")
        output_dir.mkdir(exist_ok=True)
        response_path = output_dir / f"{output_stem}_response.json"
        with open(response_path, "w") as f:
            json.dump(response.model_dump(), f, indent=2)

        markdown_content = response.choices[0].message.content
        final_content = self.wrap_markdown(markdown_content)

        markdown_path = (
            output_dir / f"{output_stem}-{time.strftime('%Y-%m-%d-%H-%M-%S')}.md"
        )
        with open(markdown_path, "w") as f:
            f.write(final_content)

        uploaded = upload_file(
            markdown_path, "ark-comms-main", f"{stream_name}/{markdown_path.name}"
        )

        self.client.send_message(
            {
                "type": "stream",
                "to": stream_name,
                "topic": topic_name,
                "content": f"Transcript for {output_stem} has been processed and saved.\n\n```md\n{final_content}\n```",
            }
        )

    def wrap_markdown(self, markdown_content):
        wrapped_content = []
        for line in markdown_content.split("\n"):
            if line.startswith(("#", "-", "*", ">", "```")) or not line.strip():
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
                        wrapped_content.append(" ".join(current_line))
                        current_line = [word]
                        current_length = len(word)
                if current_line:
                    wrapped_content.append(" ".join(current_line))
        return "\n".join(wrapped_content)

    def start_countdown(self):
        def countdown_loop():
            focus_client = create_focus_client()
            deadline = datetime(2025, 1, 22 + 7, 13, 0, 0)

            while True:
                now = datetime.now()
                if now >= deadline:
                    focus_client.send_message(
                        {
                            "type": "stream",
                            "to": "countdown",
                            "topic": "t-minus",
                            "content": "The deadline has passed. Judging has begun.",
                        }
                    )
                    break

                # Calculate remaining time
                time_remaining = deadline - now
                days = time_remaining.days
                hours, remainder = divmod(time_remaining.seconds, 3600)
                minutes, _ = divmod(remainder, 60)

                # Print remaining time
                focus_client.send_message(
                    {
                        "type": "stream",
                        "to": "countdown",
                        "topic": "t-minus",
                        "content": f"Time remaining: {days} days, {hours} hours, {minutes} minutes.",
                    }
                )

                # Wait for 30 minutes
                time.sleep(30 * 60)

        # Start the countdown in a separate thread
        countdown_thread = threading.Thread(
            target=countdown_loop, name="countdown_thread", daemon=True
        )
        countdown_thread.start()

    def get_week_and_quarter(self):
        current_date = datetime.now()
        week = current_date.isocalendar().week

        # Calculate quarter (1-4) based on month
        month = current_date.month
        quarter = (month - 1) // 3 + 1

        return quarter, week

    def create_standup_logs(self):
        # if the day is not a sunday, return
        if datetime.now().weekday() != 6:
            return

        Q, week = self.get_week_and_quarter()
        print(f"Creating standup logs for Q{Q} Week{week}")

        users = ["kai@oceanheart.ai", "blakout1@icloud.com"]
        for user in users:
            request: dict[str, Any] = {
                "anchor": "newest",
                "num_before": 100,
                "num_after": 0,
                "narrow": [
                    {"operator": "sender", "operand": user},
                    {"operator": "channel", "operand": "accountability"},
                    {"operator": "topic", "operand": f"Q{Q}:Week-{week}"},
                ],
            }
            messages = self.client.get_messages(request)
            with open(
                f"logs/accountability-logs/accountability-Q{Q}-Week{week}-{user}.json",
                "w",
            ) as f:
                json.dump(messages, f, indent=2)

    def create_standup_reports(self):
        if datetime.now().weekday() != 6:
            return

        Q, week = self.get_week_and_quarter()
        users = ["kai@oceanheart.ai", "blakout1@icloud.com"]
        for user in users:
            with open(
                f"logs/accountability-logs/accountability-Q{Q}-Week{week}-{user}.json",
                "r",
            ) as f:
                messages = json.load(f)

            with open("prompts/accountability_summary.xml", "r") as f:
                prompt_template = f.read()

            prompt = prompt_template.replace("{{json}}", json.dumps(messages))

            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that creates accountability reports from chat room message logs",
                    },
                    {"role": "user", "content": prompt},
                ],
            )

            content = response.choices[0].message.content

            with open(
                f"logs/standup-reports/accountability-Q{Q}-Week{week}-{user}.md", "w"
            ) as f:
                f.write(content)

            self.client.send_message(
                {
                    "type": "stream",
                    "to": "accountability",
                    "topic": f"Q{Q}:Week-{week}",
                    "content": f"Standup report for {user} has been created.",
                }
            )

            self.client.send_message(
                {
                    "type": "stream",
                    "to": "accountability",
                    "topic": f"Q{Q}:Week-{week}",
                    "content": f"```md\n{content}\n```",
                }
            )

    def run_standup_monitoring(self):
        def start_monitor_process():
            while True:
                self.create_standup_logs()
                self.create_standup_reports()
                time.sleep(60 * 60 * 24)

        monitor_thread = threading.Thread(
            target=start_monitor_process, name="monitor_thread", daemon=True
        )
        monitor_thread.start()
        print("Standup monitoring thread started")
