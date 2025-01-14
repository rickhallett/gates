# Upload a file | Zulip API documentation
`POST https://yourZulipDomain.zulipchat.com/api/v1/user_uploads`

[Upload](https://zulip.com/help/share-and-upload-files) a single file and get the corresponding URL.

Initially, only you will be able to access the link. To share the uploaded file, you'll need to [send a message](https://zulip.com/api/send-message) containing the resulting link. Users who can already access the link can reshare it with other users by sending additional Zulip messages containing the link.

The maximum allowed file size is available in the `max_file_upload_size_mib` field in the [`POST /register`](https://zulip.com/api/register-queue) response. Note that large files (25MB+) may fail to upload using this API endpoint due to network-layer timeouts, depending on the quality of your connection to the Zulip server.

For uploading larger files, `/api/v1/tus` is an endpoint implementing the [`tus` resumable upload protocol](https://tus.io/protocols/resumable-upload), which supports uploading arbitrarily large files limited only by the server's `max_file_upload_size_mib` (Configured via `MAX_FILE_UPLOAD_SIZE` in `/etc/zulip/settings.py`). Clients which send authenticated credentials (either via browser-based cookies, or API key via `Authorization` header) may use this endpoint to upload files.

**Changes**: The `api/v1/tus` endpoint supporting resumable uploads was introduced in Zulip 10.0 (feature level 296). Previously, `max_file_upload_size_mib` was typically 25MB.

Usage examples
--------------

*   Python
*   curl

```
#!/usr/bin/env python3

import zulip

# Pass the path to your zuliprc file here.
client = zulip.Client(config_file="~/zuliprc")

# Upload a file.
with open(path_to_file, "rb") as fp:
    result = client.upload_file(fp)
# Share the file by including it in a message.
client.send_message(
    {
        "type": "stream",
        "to": "Denmark",
        "topic": "Castle",
        "content": "Check out [this picture]({}) of my castle!".format(result["url"]),
    }
)
print(result)

```


```
curl -sSX POST https://yourZulipDomain.zulipchat.com/api/v1/user_uploads \
    -u BOT_EMAIL_ADDRESS:BOT_API_KEY \
    -F filename=@/path/to/file

```


Parameters
----------

As described above, the file to upload must be provided in the request's body.

Response
--------

#### Return values

*   `uri`: string
    
    The URL of the uploaded file. Alias of `url`.
    
    **Changes**: Deprecated in Zulip 9.0 (feature level 272). The term "URI" is deprecated in [web standards](https://url.spec.whatwg.org/#goals).
    
*   `url`: string
    
    The URL of the uploaded file.
    
    **Changes**: New in Zulip 9.0 (feature level 272). Previously, this property was only available under the legacy `uri` name.
    
*   `filename`: string
    
    The filename that Zulip stored the upload as. This usually differs from the basename of the URL when HTML escaping is required to generate a valid URL.
    
    Clients generating a Markdown link to a newly uploaded file should do so by combining the `url` and `filename` fields in the response as follows: `[{filename}]({url})`, with care taken to clean `filename` of `[` and `]` characters that might break Markdown rendering.
    
    **Changes**: New in Zulip 10.0 (feature level 285).
    

#### Example response(s)

**Changes**: As of Zulip 7.0 (feature level 167), if any parameters sent in the request are not supported by this endpoint, a successful JSON response will include an [`ignored_parameters_unsupported`](https://zulip.com/api/rest-error-handling#ignored-parameters) array.

A typical successful JSON response may look like:

```
{
    "filename": "zulip.txt",
    "msg": "",
    "result": "success",
    "uri": "/user_uploads/1/4e/m2A3MSqFnWRLUf9SaPzQ0Up_/zulip.txt",
    "url": "/user_uploads/1/4e/m2A3MSqFnWRLUf9SaPzQ0Up_/zulip.txt"
}

```
