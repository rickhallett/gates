import zulip

def create_client(config_file="zuliprc"):
    return zulip.Client(config_file=config_file)
