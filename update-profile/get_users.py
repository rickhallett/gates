#!/usr/bin/env python3

import zulip

config_file = "/Users/oceanheart/Documents/code/ark-ai/gates/zuliprc.gates.bot"
# Pass the path to your zuliprc file here.
client = zulip.Client(config_file=config_file)

# Get all users in the organization.
result = client.get_members()
# You may pass the `client_gravatar` query parameter as follows:
result = client.get_members({"client_gravatar": False})
# You may pass the `include_custom_profile_fields` query parameter as follows:
result = client.get_members({"include_../custom_profile_fields": True})

print(result)
