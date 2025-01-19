import zulip
import os
from dotenv import load_dotenv

load_dotenv()

def _create_client_with_config(config_file: str, api_key_var: str, api_key_template: str) -> zulip.Client:
    # Read the template
    with open(config_file, "r") as f:
        config = f.read()
    
    # Replace the template variable
    config = config.replace(api_key_template, os.getenv(api_key_var))
    
    # Write to temporary file
    with open("temp.zuliprc", "w") as f:
        f.write(config)

    client = zulip.Client(config_file="temp.zuliprc")
    os.remove("temp.zuliprc")
    return client

def create_client(config_file="zuliprc.gates.bot") -> zulip.Client:
    return _create_client_with_config(
        config_file,
        "GATES_ZULIP_API_KEY",
        "{{GATES_ZULIP_API_KEY}}"
    )

def create_focus_client(config_file="zuliprc.focus.bot") -> zulip.Client:
    return _create_client_with_config(
        config_file,
        "FOCUS_ZULIP_API_KEY",
        "{{FOCUS_ZULIP_API_KEY}}"
    )
