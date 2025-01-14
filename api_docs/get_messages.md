# Get messages | Zulip API documentation
`GET https://yourZulipDomain.zulipchat.com/api/v1/messages`

This endpoint is the primary way to fetch a messages. It is used by all official Zulip clients (e.g. the web, desktop, mobile, and terminal clients) as well as many bots, API clients, backup scripts, etc.

Most queries will specify a [narrow filter](https://zulip.com/api/get-messages#parameter-narrow), to fetch the messages matching any supported [search query](https://zulip.com/help/search-for-messages). If not specified, it will return messages corresponding to the user's [combined feed](https://zulip.com/help/combined-feed). There are two ways to specify which messages matching the narrow filter to fetch:

*   A range of messages, described by an `anchor` message ID (or a string-format specification of how the server should computer an anchor to use) and a maximum number of messages in each direction from that anchor.
    
*   A rarely used variant (`message_ids`) where the client specifies the message IDs to fetch.
    

The server returns the matching messages, sorted by message ID, as well as some metadata that makes it easy for a client to determine whether there are more messages matching the query that were not returned due to the `num_before` and `num_after` limits.

Note that a user's message history does not contain messages sent to channels before they [subscribe](https://zulip.com/api/subscribe), and newly created bot users are not usually subscribed to any channels.

We recommend requesting at most 1000 messages in a batch, to avoid generating very large HTTP responses. A maximum of 5000 messages can be obtained per request; attempting to exceed this will result in an error.

**Changes**: The `message_ids` option is new in Zulip 10.0 (feature level 300).

Usage examples
--------------

*   Python
*   JavaScript
*   curl

```
#!/usr/bin/env python3

import zulip

# Pass the path to your zuliprc file here.
client = zulip.Client(config_file="~/zuliprc")

# Get the 100 last messages sent by "iago@zulip.com" to
# the channel named "Verona".
request: dict[str, Any] = {
    "anchor": "newest",
    "num_before": 100,
    "num_after": 0,
    "narrow": [
        {"operator": "sender", "operand": "iago@zulip.com"},
        {"operator": "channel", "operand": "Verona"},
    ],
}
result = client.get_messages(request)
print(result)

```


More examples and documentation can be found [here](https://github.com/zulip/zulip-js).

```
const zulipInit = require("zulip-js");

// Pass the path to your zuliprc file here.
const config = { zuliprc: "zuliprc" };

(async () => {
    const client = await zulipInit(config);

    const readParams = {
        anchor: "newest",
        num_before: 100,
        num_after: 0,
        narrow: [
            {operator: "sender", operand: "iago@zulip.com"},
            {operator: "channel", operand: "Verona"},
        ],
    };

    // Get the 100 last messages sent by "iago@zulip.com" to the channel "Verona"
    console.log(await client.messages.retrieve(readParams));
})();

```


```
curl -sSX GET -G https://yourZulipDomain.zulipchat.com/api/v1/messages \
    -u BOT_EMAIL_ADDRESS:BOT_API_KEY \
    --data-urlencode anchor=43 \
    --data-urlencode num_before=4 \
    --data-urlencode num_after=8 \
    --data-urlencode 'narrow=[{"operand": "Denmark", "operator": "channel"}]'

```


Parameters
----------

**anchor** string optional[](#parameter-anchor)

Example: `"43"`

Integer message ID to anchor fetching of new messages. Supports special string values for when the client wants the server to compute the anchor to use:

*   `newest`: The most recent message.
*   `oldest`: The oldest message.
*   `first_unread`: The oldest unread message matching the query, if any; otherwise, the most recent message.

**Changes**: String values are new in Zulip 3.0 (feature level 1). The `first_unread` functionality was supported in Zulip 2.1.x and older by not sending `anchor` and using `use_first_unread_anchor`.

In Zulip 2.1.x and older, `oldest` can be emulated with `"anchor": 0`, and `newest` with `"anchor": 10000000000000000` (that specific large value works around a bug in Zulip 2.1.x and older in the `found_newest` return value).

* * *

**include\_anchor** boolean optional[](#parameter-include_anchor)

Example: `false`

Whether a message with the specified ID matching the narrow should be included.

**Changes**: New in Zulip 6.0 (feature level 155).

Defaults to `true`.

* * *

**num\_before** integer optional[](#parameter-num_before)

Example: `4`

The number of messages with IDs less than the anchor to retrieve. Required if `message_ids` is not provided.

* * *

**num\_after** integer optional[](#parameter-num_after)

Example: `8`

The number of messages with IDs greater than the anchor to retrieve. Required if `message_ids` is not provided.

* * *

**narrow** (object | (string)\[\])\[\] optional[](#parameter-narrow)

Example: `[{"operand": "Denmark", "operator": "channel"}]`

The narrow where you want to fetch the messages from. See how to [construct a narrow](https://zulip.com/api/construct-narrow).

Note that many narrows, including all that lack a `channel`, `channels`, `stream`, or `streams` operator, search the user's personal message history. See [searching shared history](https://zulip.com/help/search-for-messages#searching-shared-history) for details.

For example, if you would like to fetch messages from all public channels instead of only the user's message history, then a specific narrow for messages sent to all public channels can be used: `{"operator": "channels", "operand": "public"}`.

Newly created bot users are not usually subscribed to any channels, so bots using this API should either be subscribed to appropriate channels or use a shared history search narrow with this endpoint.

**Changes**: See [changes section](https://zulip.com/api/construct-narrow#changes) of search/narrow filter documentation.

Defaults to `[]`.

* * *

**client\_gravatar** boolean optional[](#parameter-client_gravatar)

Example: `false`

Whether the client supports computing gravatars URLs. If enabled, `avatar_url` will be included in the response only if there is a Zulip avatar, and will be `null` for users who are using gravatar as their avatar. This option significantly reduces the compressed size of user data, since gravatar URLs are long, random strings and thus do not compress well. The `client_gravatar` field is set to `true` if clients can compute their own gravatars.

**Changes**: The default value of this parameter was `false` prior to Zulip 5.0 (feature level 92).

Defaults to `true`.

* * *

**apply\_markdown** boolean optional[](#parameter-apply_markdown)

Example: `false`

If `true`, message content is returned in the rendered HTML format. If `false`, message content is returned in the raw Markdown-format text that user entered.

Defaults to `true`.

* * *

**message\_ids** (integer)\[\] optional[](#parameter-message_ids)

Example: `[1, 2, 3]`

A list of message IDs to fetch. The server will return messages corresponding to the subset of the requested message IDs that exist and the current user has access to, potentially filtered by the narrow (if that parameter is provided).

It is an error to pass this parameter as well as any of the parameters involved in specifying a range of messages: `anchor`, `include_anchor`, `use_first_unread_anchor`, `num_before`, and `num_after`.

**Changes**: New in Zulip 10.0 (feature level 300). Previously, there was no way to request a specific set of messages IDs.

* * *

**use\_first\_unread\_anchor** boolean optional Deprecated[](#parameter-use_first_unread_anchor)

Example: `true`

Legacy way to specify `"anchor": "first_unread"` in Zulip 2.1.x and older.

Whether to use the (computed by the server) first unread message matching the narrow as the `anchor`. Mutually exclusive with `anchor`.

**Changes**: Deprecated in Zulip 3.0 (feature level 1) and replaced by `"anchor": "first_unread"`.

Defaults to `false`.

* * *

Response
--------

#### Return values

*   `anchor`: integer
    
    The same `anchor` specified in the request (or the computed one, if `use_first_unread_anchor` is `true`).
    
    Only present if `message_ids` is not provided.
    
*   `found_newest`: boolean
    
    Whether the server promises that the `messages` list includes the very newest messages matching the narrow (used by clients that paginate their requests to decide whether there may be more messages to fetch).
    
*   `found_oldest`: boolean
    
    Whether the server promises that the `messages` list includes the very oldest messages matching the narrow (used by clients that paginate their requests to decide whether there may be more messages to fetch).
    
*   `found_anchor`: boolean
    
    Whether the anchor message is included in the response. If the message with the ID specified in the request does not exist, did not match the narrow, or was excluded via `"include_anchor": false`, this will be false.
    
*   `history_limited`: boolean
    
    Whether the message history was limited due to plan restrictions. This flag is set to `true` only when the oldest messages(`found_oldest`) matching the narrow is fetched.
    
*   `messages`: (object)\[\]
    
    An array of `message` objects.
    
    **Changes**: In Zulip 3.1 (feature level 26), the `sender_short_name` field was removed from message objects.
    
    *   `avatar_url`: string | null
        
        The URL of the message sender's avatar. Can be `null` only if the current user has access to the sender's real email address and `client_gravatar` was `true`.
        
        If `null`, then the sender has not uploaded an avatar in Zulip, and the client can compute the gravatar URL by hashing the sender's email address, which corresponds in this case to their real email address.
        
        **Changes**: Before Zulip 7.0 (feature level 163), access to a user's real email address was a realm-level setting. As of this feature level, `email_address_visibility` is a user setting.
        
    *   `client`: string
        
        A Zulip "client" string, describing what Zulip client sent the message.
        
    *   `content`: string
        
        The content/body of the message.
        
    *   `content_type`: string
        
        The HTTP `content_type` for the message content. This will be `text/html` or `text/x-markdown`, depending on whether `apply_markdown` was set.
        
    *   `display_recipient`: string | (object)\[\]
        
        Data on the recipient of the message; either the name of a channel or a dictionary containing basic data on the users who received the message.
        
    *   `edit_history`: (object)\[\]
        
        An array of objects, with each object documenting the changes in a previous edit made to the message, ordered chronologically from most recent to least recent edit.
        
        Not present if the message has never been edited or if the realm has [disabled viewing of message edit history](https://zulip.com/help/disable-message-edit-history).
        
        Every object will contain `user_id` and `timestamp`.
        
        The other fields are optional, and will be present or not depending on whether the channel, topic, and/or message content were modified in the edit event. For example, if only the topic was edited, only `prev_topic` and `topic` will be present in addition to `user_id` and `timestamp`.
        
        **Changes**: In Zulip 10.0 (feature level 284), removed the `prev_rendered_content_version` field as it is an internal server implementation detail not used by any client.
        
        *   `prev_content`: string
            
            Only present if message's content was edited.
            
            The content of the message immediately prior to this edit event.
            
        *   `prev_rendered_content`: string
            
            Only present if message's content was edited.
            
            The rendered HTML representation of `prev_content`.
            
        *   `prev_stream`: integer
            
            Only present if message's channel was edited.
            
            The channel ID of the message immediately prior to this edit event.
            
            **Changes**: New in Zulip 3.0 (feature level 1).
            
        *   `prev_topic`: string
            
            Only present if message's topic was edited.
            
            The topic of the message immediately prior to this edit event.
            
            **Changes**: New in Zulip 5.0 (feature level 118). Previously, this field was called `prev_subject`; clients are recommended to rename `prev_subject` to `prev_topic` if present for compatibility with older Zulip servers.
            
        *   `stream`: integer
            
            Only present if message's channel was edited.
            
            The ID of the channel containing the message immediately after this edit event.
            
            **Changes**: New in Zulip 5.0 (feature level 118).
            
        *   `timestamp`: integer
            
            The UNIX timestamp for the edit.
            
        *   `topic`: string
            
            Only present if message's topic was edited.
            
            The topic of the message immediately after this edit event.
            
            **Changes**: New in Zulip 5.0 (feature level 118).
            
        *   `user_id`: integer | null
            
            The ID of the user that made the edit.
            
            Will be `null` only for edit history events predating March 2017.
            
            Clients can display edit history events where this is `null` as modified by either the sender (for content edits) or an unknown user (for topic edits).
            
    *   `id`: integer
        
        The unique message ID. Messages should always be displayed sorted by ID.
        
    *   `is_me_message`: boolean
        
        Whether the message is a [/me status message](https://zulip.com/help/format-your-message-using-markdown#status-messages)
        
    *   `last_edit_timestamp`: integer
        
        The UNIX timestamp for when the message was last edited, in UTC seconds.
        
        Not present if the message has never been edited.
        
    *   `reactions`: (object)\[\]
        
        Data on any reactions to the message.
        
        *   `emoji_name`: string
            
            Name of the emoji.
            
        *   `emoji_code`: string
            
            A unique identifier, defining the specific emoji codepoint requested, within the namespace of the `reaction_type`.
            
        *   `reaction_type`: string
            
            A string indicating the type of emoji. Each emoji `reaction_type` has an independent namespace for values of `emoji_code`.
            
            Must be one of the following values:
            
            *   `unicode_emoji` : In this namespace, `emoji_code` will be a dash-separated hex encoding of the sequence of Unicode codepoints that define this emoji in the Unicode specification.
                
            *   `realm_emoji` : In this namespace, `emoji_code` will be the ID of the uploaded [custom emoji](https://zulip.com/help/custom-emoji).
                
            *   `zulip_extra_emoji` : These are special emoji included with Zulip. In this namespace, `emoji_code` will be the name of the emoji (e.g. "zulip").
                
        *   `user_id`: integer
            
            The ID of the user who added the reaction.
            
            **Changes**: New in Zulip 3.0 (feature level 2). The `user` object is deprecated and will be removed in the future.
            
        *   `user`: object
            
            Dictionary with data on the user who added the reaction, including the user ID as the `id` field. Note that reactions data received from the [events API](https://zulip.com/api/get-events) has a slightly different `user` dictionary format, with the user ID field called `user_id` instead.
            
            **Changes**: Deprecated and to be removed in a future release once core clients have migrated to use the adjacent `user_id` field, which was introduced in Zulip 3.0 (feature level 2). Clients supporting older Zulip server versions should use the user ID mentioned in the description above as they would the `user_id` field.
            
            *   `id`: integer
                
                ID of the user.
                
            *   `email`: string
                
                Zulip API email of the user.
                
            *   `full_name`: string
                
                Full name of the user.
                
            *   `is_mirror_dummy`: boolean
                
                Whether the user is a mirror dummy.
                
    *   `recipient_id`: integer
        
        A unique ID for the set of users receiving the message (either a channel or group of users). Useful primarily for hashing.
        
        **Changes**: Before Zulip 10.0 (feature level 327), `recipient_id` was the same across all incoming 1:1 direct messages. Now, each incoming message uniquely shares a `recipient_id` with outgoing messages in the same conversation.
        
    *   `sender_email`: string
        
        The Zulip API email address of the message's sender.
        
    *   `sender_full_name`: string
        
        The full name of the message's sender.
        
    *   `sender_id`: integer
        
        The user ID of the message's sender.
        
    *   `sender_realm_str`: string
        
        A string identifier for the realm the sender is in. Unique only within the context of a given Zulip server.
        
        E.g. on `example.zulip.com`, this will be `example`.
        
    *   `stream_id`: integer
        
        Only present for channel messages; the ID of the channel.
        
    *   `subject`: string
        
        The `topic` of the message. Currently always `""` for direct messages, though this could change if Zulip adds support for topics in direct message conversations.
        
        The field name is a legacy holdover from when topics were called "subjects" and will eventually change.
        
    *   `submessages`: (object)\[\]
        
        Data used for certain experimental Zulip integrations.
        
        *   `msg_type`: string
            
            The type of the message.
            
        *   `content`: string
            
            The new content of the submessage.
            
        *   `message_id`: integer
            
            The ID of the message to which the submessage has been added.
            
        *   `sender_id`: integer
            
            The ID of the user who sent the message.
            
        *   `id`: integer
            
            The ID of the submessage.
            
    *   `timestamp`: integer
        
        The UNIX timestamp for when the message was sent, in UTC seconds.
        
    *   `topic_links`: (object)\[\]
        
        Data on any links to be included in the `topic` line (these are generated by [custom linkification filters](https://zulip.com/help/add-a-custom-linkifier) that match content in the message's topic.)
        
        **Changes**: This field contained a list of urls before Zulip 4.0 (feature level 46).
        
        New in Zulip 3.0 (feature level 1). Previously, this field was called `subject_links`; clients are recommended to rename `subject_links` to `topic_links` if present for compatibility with older Zulip servers.
        
        *   `text`: string
            
            The original link text present in the topic.
            
        *   `url`: string
            
            The expanded target url which the link points to.
            
    *   `type`: string
        
        The type of the message: `"stream"` or `"private"`.
        
    *   `flags`: (string)\[\]
        
        The user's [message flags](https://zulip.com/api/update-message-flags#available-flags) for the message.
        
        **Changes**: In Zulip 8.0 (feature level 224), the `wildcard_mentioned` flag was deprecated in favor of the `stream_wildcard_mentioned` and `topic_wildcard_mentioned` flags. The `wildcard_mentioned` flag exists for backwards compatibility with older clients and equals `stream_wildcard_mentioned || topic_wildcard_mentioned`. Clients supporting older server versions should treat this field as a previous name for the `stream_wildcard_mentioned` flag as topic wildcard mentions were not available prior to this feature level.
        
    *   `match_content`: string
        
        Only present if keyword search was included among the narrow parameters.
        
        HTML content of a queried message that matches the narrow, with `<span class="highlight">` elements wrapping the matches for the search keywords.
        
    *   `match_subject`: string
        
        Only present if keyword search was included among the narrow parameters.
        
        HTML-escaped topic of a queried message that matches the narrow, with `<span class="highlight">` elements wrapping the matches for the search keywords.
        

#### Example response(s)

**Changes**: As of Zulip 7.0 (feature level 167), if any parameters sent in the request are not supported by this endpoint, a successful JSON response will include an [`ignored_parameters_unsupported`](https://zulip.com/api/rest-error-handling#ignored-parameters) array.

A typical successful JSON response may look like:

```
{
    "anchor": 21,
    "found_anchor": true,
    "found_newest": true,
    "messages": [
        {
            "avatar_url": "https://secure.gravatar.com/avatar/6d8cad0fd00256e7b40691d27ddfd466?d=identicon&version=1",
            "client": "populate_db",
            "content": "<p>Security experts agree that relational algorithms are an interesting new topic in the field of networking, and scholars concur.</p>",
            "content_type": "text/html",
            "display_recipient": [
                {
                    "email": "hamlet@zulip.com",
                    "full_name": "King Hamlet",
                    "id": 4,
                    "is_mirror_dummy": false
                },
                {
                    "email": "iago@zulip.com",
                    "full_name": "Iago",
                    "id": 5,
                    "is_mirror_dummy": false
                },
                {
                    "email": "prospero@zulip.com",
                    "full_name": "Prospero from The Tempest",
                    "id": 8,
                    "is_mirror_dummy": false
                }
            ],
            "flags": [
                "read"
            ],
            "id": 16,
            "is_me_message": false,
            "reactions": [],
            "recipient_id": 27,
            "sender_email": "hamlet@zulip.com",
            "sender_full_name": "King Hamlet",
            "sender_id": 4,
            "sender_realm_str": "zulip",
            "subject": "",
            "submessages": [],
            "timestamp": 1527921326,
            "topic_links": [],
            "type": "private"
        },
        {
            "avatar_url": "https://secure.gravatar.com/avatar/6d8cad0fd00256e7b40691d27ddfd466?d=identicon&version=1",
            "client": "populate_db",
            "content": "<p>Wait, is this from the frontend js code or backend python code</p>",
            "content_type": "text/html",
            "display_recipient": "Verona",
            "flags": [
                "read"
            ],
            "id": 21,
            "is_me_message": false,
            "reactions": [],
            "recipient_id": 20,
            "sender_email": "hamlet@zulip.com",
            "sender_full_name": "King Hamlet",
            "sender_id": 4,
            "sender_realm_str": "zulip",
            "stream_id": 5,
            "subject": "Verona3",
            "submessages": [],
            "timestamp": 1527939746,
            "topic_links": [],
            "type": "stream"
        }
    ],
    "msg": "",
    "result": "success"
}

```
