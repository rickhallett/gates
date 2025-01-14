# Delete an attachment | Zulip API documentation
`DELETE https://yourZulipDomain.zulipchat.com/api/v1/attachments/{attachment_id}`

Delete an uploaded file given its attachment ID.

Note that uploaded files that have been referenced in at least one message are automatically deleted once the last message containing a link to them is deleted (whether directly or via a [message retention policy](https://zulip.com/help/message-retention-policy)).

Uploaded files that are never used in a message are automatically deleted a few weeks after being uploaded.

Attachment IDs can be contained from [GET /attachments](https://zulip.com/api/get-attachments).

Usage examples
--------------

*   Python
*   curl

```
#!/usr/bin/env python3

import zulip

# Pass the path to your zuliprc file here.
client = zulip.Client(config_file="~/zuliprc")

# Delete the attachment given the attachment's ID.
url = "attachments/" + str(attachment_id)
result = client.call_endpoint(
    url=url,
    method="DELETE",
)
print(result)

```


```
curl -sSX DELETE https://yourZulipDomain.zulipchat.com/api/v1/attachments/1 \
    -u BOT_EMAIL_ADDRESS:BOT_API_KEY

```


Parameters
----------

**attachment\_id** integer required in path[](#parameter-attachment_id)

Example: `1`

The ID of the attachment to be deleted.

* * *

Response
--------

#### Example response(s)

**Changes**: As of Zulip 7.0 (feature level 167), if any parameters sent in the request are not supported by this endpoint, a successful JSON response will include an [`ignored_parameters_unsupported`](https://zulip.com/api/rest-error-handling#ignored-parameters) array.

A typical successful JSON response may look like:

```
{
    "msg": "",
    "result": "success"
}

```


A typical failed JSON response for when the `attachment_id` is invalid

```
{
    "code": "BAD_REQUEST",
    "msg": "Invalid attachment",
    "result": "error"
}

```


A typical failed JSON response for when the user is not logged in:

```
{
    "code": "UNAUTHORIZED",
    "msg": "Not logged in: API authentication or user session required",
    "result": "error"
}

```
