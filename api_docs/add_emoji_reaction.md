# Add an emoji reaction | Zulip API documentation
`POST https://yourZulipDomain.zulipchat.com/api/v1/messages/{message_id}/reactions`

Add an [emoji reaction](https://zulip.com/help/emoji-reactions) to a message.

Usage examples
--------------

*   Python
*   curl

```
#!/usr/bin/env python3

import zulip

# Pass the path to your zuliprc file here.
client = zulip.Client(config_file="~/zuliprc")

# Add an emoji reaction.
request = {
    "message_id": message_id,
    "emoji_name": "octopus",
}
result = client.add_reaction(request)
print(result)

```


```
curl -sSX POST https://yourZulipDomain.zulipchat.com/api/v1/messages/43/reactions \
    -u BOT_EMAIL_ADDRESS:BOT_API_KEY \
    --data-urlencode emoji_name=octopus

```


Parameters
----------

**message\_id** integer required in path[](#parameter-message_id)

Example: `43`

The target message's ID.

* * *

**emoji\_name** string required[](#parameter-emoji_name)

Example: `"octopus"`

The target emoji's human-readable name.

To find an emoji's name, hover over a message to reveal three icons on the right, then click the smiley face icon. Images of available reaction emojis appear. Hover over the emoji you want, and note that emoji's text name.

* * *

**emoji\_code** string optional[](#parameter-emoji_code)

Example: `"1f419"`

A unique identifier, defining the specific emoji codepoint requested, within the namespace of the `reaction_type`.

For most API clients, you won't need this, but it's important for Zulip apps to handle rare corner cases when adding/removing votes on an emoji reaction added previously by another user.

If the existing reaction was added when the Zulip server was using a previous version of the emoji data mapping between Unicode codepoints and human-readable names, sending the `emoji_code` in the data for the original reaction allows the Zulip server to correctly interpret your upvote as an upvote rather than a reaction with a "different" emoji.

* * *

**reaction\_type** string optional[](#parameter-reaction_type)

Example: `"unicode_emoji"`

A string indicating the type of emoji. Each emoji `reaction_type` has an independent namespace for values of `emoji_code`.

If an API client is adding/removing a vote on an existing reaction, it should pass this parameter using the value the server provided for the existing reaction for specificity. Supported values:

*   `unicode_emoji` : In this namespace, `emoji_code` will be a dash-separated hex encoding of the sequence of Unicode codepoints that define this emoji in the Unicode specification.
    
*   `realm_emoji` : In this namespace, `emoji_code` will be the ID of the uploaded [custom emoji](https://zulip.com/help/custom-emoji).
    
*   `zulip_extra_emoji` : These are special emoji included with Zulip. In this namespace, `emoji_code` will be the name of the emoji (e.g. "zulip").
    

**Changes**: In Zulip 3.0 (feature level 2), this parameter became optional for [custom emoji](https://zulip.com/help/custom-emoji); previously, this endpoint assumed `unicode_emoji` if this parameter was not specified.

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


An example JSON error response for when the emoji code is invalid:

```
{
    "code": "BAD_REQUEST",
    "msg": "Invalid emoji code",
    "result": "error"
}

```


An example JSON error response for when the reaction already exists.

**Changes**: New in Zulip 8.0 (feature level 193). Previously, this error returned the `"BAD_REQUEST"` code.

```
{
    "code": "REACTION_ALREADY_EXISTS",
    "msg": "Reaction already exists.",
    "result": "error"
}

```
