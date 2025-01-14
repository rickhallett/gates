from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import re

class Message(BaseModel):
    id: int
    sender_id: int
    content: str
    recipient_id: int
    timestamp: int
    client: str
    subject: str
    topic_links: List
    is_me_message: bool
    reactions: List
    submessages: List
    sender_full_name: str
    sender_email: str
    sender_realm_str: str
    display_recipient: str
    type: str
    stream_id: int
    avatar_url: str
    content_type: str
    links: Optional[List[str]] = None
    audio_links: Optional[List[str]] = None
    youtube_links: Optional[List[str]] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.links = self.extract_links()
        self.audio_links = self.extract_audio_links()
        self.youtube_links = self.extract_youtube_links()

    def extract_links(self) -> List[str]:
        # Regex pattern to match Markdown links
        markdown_link_pattern = r'\[.*?\]\((.*?)\)'
        # Find all matches in the content
        links = re.findall(markdown_link_pattern, self.content)
        return links
    
    def extract_audio_links(self) -> List[str]:
        filetypes = ["mp3", "wav", "ogg", "m4a", "aac", "flac", "wma", "aiff", "au", "amr", "aac", "m4a", "m4b", "m4p", "m4r", "m4v", "mp2", "mpa", "mpc", "mpd", "mpf", "mpg", "mpv", "oga", "ogg", "opus", "ra", "rm", "wav", "wma"]
        audio_links = []
        for link in self.links:
            if any(filetype in link for filetype in filetypes):
                audio_links.append(link)
        return audio_links
    
    def extract_youtube_links(self) -> List[str]:
        youtube_link_pattern = r'https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+'
        youtube_links = re.findall(youtube_link_pattern, self.content)
        return youtube_links
    
    def get_youtube_id(self, link: str) -> str:
        youtube_id_pattern = r'https?://(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})'
        youtube_id = re.search(youtube_id_pattern, link)
        return youtube_id.group(1) if youtube_id else None

class OpenAIResponse(BaseModel):
    id: str
    object: str
    created: int
    model: str
    choices: List[Dict[str, Any]]
    usage: Dict[str, int]
