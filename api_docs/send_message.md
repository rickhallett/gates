Output Markdown
Please enter the URL of a web page

Source Web Page
https://zulip.com/api/send-message
Include Title
Ignore Links
# Send a message | Zulip API documentation
`POST https://yourZulipDomain.zulipchat.com/api/v1/messages`

Send a [channel message](https://zulip.com/help/introduction-to-topics) or a [direct message](https://zulip.com/help/direct-messages).

Usage examples
--------------

*   Python
*   JavaScript
*   curl
*   zulip-send

```
#!/usr/bin/env python3

import zulip

# Pass the path to your zuliprc file here.
client = zulip.Client(config_file="~/zuliprc")

# Send a channel message.
request = {
    "type": "stream",
    "to": "Denmark",
    "topic": "Castle",
    "content": "I come not, friends, to steal away your hearts.",
}
result = client.send_message(request)
# Send a direct message.
request = {
    "type": "private",
    "to": [user_id],
    "content": "With mirth and laughter let old wrinkles come.",
}
result = client.send_message(request)
print(result)

```


More examples and documentation can be found [here](https://github.com/zulip/zulip-js).

```
const zulipInit = require("zulip-js");

// Pass the path to your zuliprc file here.
const config = { zuliprc: "zuliprc" };

(async () => {
    const client = await zulipInit(config);

    // Send a channel message
    let params = {
        to: "social",
        type: "stream",
        topic: "Castle",
        content: "I come not, friends, to steal away your hearts.",
    };
    console.log(await client.messages.send(params));

    // Send a direct message
    const user_id = 9;
    params = {
        to: [user_id],
        type: "direct",
        content: "With mirth and laughter let old wrinkles come.",
    };
    console.log(await client.messages.send(params));
})();

```


```
# For channel messages
curl -X POST https://yourZulipDomain.zulipchat.com/api/v1/messages \
    -u BOT_EMAIL_ADDRESS:BOT_API_KEY \
    --data-urlencode type=stream \
    --data-urlencode 'to="Denmark"' \
    --data-urlencode topic=Castle \
    --data-urlencode 'content=I come not, friends, to steal away your hearts.'

# For direct messages
curl -X POST https://yourZulipDomain.zulipchat.com/api/v1/messages \
    -u BOT_EMAIL_ADDRESS:BOT_API_KEY \
    --data-urlencode type=direct \
    --data-urlencode 'to=[9]' \
    --data-urlencode 'content=With mirth and laughter let old wrinkles come.'

```


You can use `zulip-send` (available after you `pip install zulip`) to easily send Zulips from the command-line, providing the message content via STDIN.

```
# For channel messages
zulip-send --stream Denmark --subject Castle \
    --user othello-bot@example.com --api-key a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5

# For direct messages
zulip-send hamlet@example.com \
    --user othello-bot@example.com --api-key a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5

```


#### Passing in the message on the command-line

If you'd like, you can also provide the message on the command-line with the `-m` or `--message` flag, as follows:

```
zulip-send --stream Denmark --subject Castle \
    --message 'I come not, friends, to steal away your hearts.' \
    --user othello-bot@example.com --api-key a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5

```


You can omit the `user` and `api-key` parameters if you have a `~/.zuliprc` file.

Parameters
----------

**type** string required[](#parameter-type)

Example: `"direct"`

The type of message to be sent.

`"direct"` for a direct message and `"stream"` or `"channel"` for a channel message.

**Changes**: In Zulip 9.0 (feature level 248), `"channel"` was added as an additional value for this parameter to request a channel message.

In Zulip 7.0 (feature level 174), `"direct"` was added as the preferred way to request a direct message, deprecating the original `"private"`. While `"private"` is still supported for requesting direct messages, clients are encouraged to use to the modern convention with servers that support it, because support for `"private"` will eventually be removed.

Must be one of: `"direct"`, `"channel"`, `"stream"`, `"private"`.

* * *

**to** string | integer | (string)\[\] | (integer)\[\] required[](#parameter-to)

Example: `[9, 10]`

For channel messages, either the name or integer ID of the channel. For direct messages, either a list containing integer user IDs or a list containing string Zulip API email addresses.

**Changes**: Support for using user/channel IDs was added in Zulip 2.0.0.

* * *

**content** string required[](#parameter-content)

Example: `"Hello"`

The content of the message.

Clients should use the `max_message_length` returned by the [`POST /register`](https://zulip.com/api/register-queue) endpoint to determine the maximum message size.

* * *

**topic** string optional[](#parameter-topic)

Example: `"Castle"`

The topic of the message. Only required for channel messages (`"type": "stream"` or `"type": "channel"`), ignored otherwise.

Clients should use the `max_topic_length` returned by the [`POST /register`](https://zulip.com/api/register-queue) endpoint to determine the maximum topic length.

**Changes**: New in Zulip 2.0.0. Previous Zulip releases encoded this as `subject`, which is currently a deprecated alias.

* * *

**queue\_id** string optional[](#parameter-queue_id)

Example: `"fb67bf8a-c031-47cc-84cf-ed80accacda8"`

For clients supporting [local echo](https://zulip.readthedocs.io/en/latest/subsystems/sending-messages.html#local-echo), the [event queue](https://zulip.com/api/register-queue) ID for the client. If passed, `local_id` is required. If the message is successfully sent, the server will include `local_id` in the `message` event that the client with this `queue_id` will receive notifying it of the new message via [`GET /events`](https://zulip.com/api/get-events). This lets the client know unambiguously that it should replace the locally echoed message, rather than adding this new message (which would be correct if the user had sent the new message from another device).

* * *

**local\_id** string optional[](#parameter-local_id)

Example: `"100.01"`

For clients supporting local echo, a unique string-format identifier chosen freely by the client; the server will pass it back to the client without inspecting it, as described in the `queue_id` description.

* * *

**read\_by\_sender** boolean optional[](#parameter-read_by_sender)

Example: `true`

Whether the message should be initially marked read by its sender. If unspecified, the server uses a heuristic based on the client name.

**Changes**: New in Zulip 8.0 (feature level 236).

* * *

Response
--------

#### Return values

*   `id`: integer
    
    The unique ID assigned to the sent message.
    
*   `automatic_new_visibility_policy`: integer
    
    If the message's sender had configured their [visibility policy settings](https://zulip.com/help/mute-a-topic) to potentially automatically follow or unmute topics when sending messages, and one of these policies did in fact change the user's visibility policy for the topic where this message was sent, the new value for that user's visibility policy for the recipient topic.
    
    Only present if the sender's visibility was in fact changed.
    
    The value can be either [unmuted or followed](https://zulip.com/api/update-user-topic#parameter-visibility_policy).
    
    Clients will also be notified about the change in policy via a `user_topic` event as usual. This field is intended to be used by clients to explicitly inform the user when a topic's visibility policy was changed automatically due to sending a message.
    
    For example, the Zulip web application uses this field to decide whether to display a warning or notice suggesting to unmute the topic after sending a message to a muted channel. Such a notice would be confusing in the event that the act of sending the message had already resulted in the user automatically unmuting or following the topic in question.
    
    **Changes**: New in Zulip 8.0 (feature level 218).
    

#### Example response(s)

**Changes**: As of Zulip 7.0 (feature level 167), if any parameters sent in the request are not supported by this endpoint, a successful JSON response will include an [`ignored_parameters_unsupported`](https://zulip.com/api/rest-error-handling#ignored-parameters) array.

A typical successful JSON response may look like:

```
{
    "automatic_new_visibility_policy": 2,
    "id": 42,
    "msg": "",
    "result": "success"
}

```


A typical failed JSON response for when a channel message is sent to a channel that does not exist:

```
{
    "code": "STREAM_DOES_NOT_EXIST",
    "msg": "Channel 'nonexistent' does not exist",
    "result": "error",
    "stream": "nonexistent"
}

```


A typical failed JSON response for when a direct message is sent to a user that does not exist:

```
{
    "code": "BAD_REQUEST",
    "msg": "Invalid email 'eeshan@zulip.com'",
    "result": "error"
}

```


An example JSON error response for when the message was rejected because of the organization's `wildcard_mention_policy` and large number of subscribers to the channel.

**Changes**: New in Zulip 8.0 (feature level 229). Previously, this error returned the `"BAD_REQUEST"` code.

```
{
    "code": "STREAM_WILDCARD_MENTION_NOT_ALLOWED",
    "msg": "You do not have permission to use channel wildcard mentions in this channel.",
    "result": "error"
}

```


An example JSON error response for when the message was rejected because the message contains a topic wildcard mention, but the user doesn't have permission to use such a mention in this topic due to the `wildcard_mention_policy` (and large number of participants in this specific topic).

**Changes**: New in Zulip 8.0 (feature level 229). Previously, `wildcard_mention_policy` was not enforced for topic mentions.

```
{
    "code": "TOPIC_WILDCARD_MENTION_NOT_ALLOWED",
    "msg": "You do not have permission to use topic wildcard mentions in this topic.",
    "result": "error"
}

```

Uses heroku, turndown, Readability and jsdom. Source on github.