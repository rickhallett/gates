# Get all channels | Zulip API documentation
`GET https://yourZulipDomain.zulipchat.com/api/v1/streams`

Get all channels that the user [has access to](https://zulip.com/help/channel-permissions).

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

# Get all channels that the user has access to.
result = client.get_streams()
# You may pass in one or more of the query parameters mentioned above
# as keyword arguments, like so:
result = client.get_streams(include_public=False)
print(result)

```


More examples and documentation can be found [here](https://github.com/zulip/zulip-js).

```
const zulipInit = require("zulip-js");

// Pass the path to your zuliprc file here.
const config = { zuliprc: "zuliprc" };

(async () => {
    const client = await zulipInit(config);

    // Get all channels that the user has access to
    console.log(await client.streams.retrieve());
})();

```


```
curl -sSX GET -G https://yourZulipDomain.zulipchat.com/api/v1/streams \
    -u BOT_EMAIL_ADDRESS:BOT_API_KEY

```


You may pass in one or more of the parameters mentioned below as URL query parameters, like so:

```
curl -sSX GET -G https://yourZulipDomain.zulipchat.com/api/v1/streams \
    -u BOT_EMAIL_ADDRESS:BOT_API_KEY \
    --data-urlencode include_public=false

```


Parameters
----------

**include\_public** boolean optional[](#parameter-include_public)

Example: `false`

Include all public channels.

Defaults to `true`.

* * *

**include\_web\_public** boolean optional[](#parameter-include_web_public)

Example: `true`

Include all web-public channels.

Defaults to `false`.

* * *

**include\_subscribed** boolean optional[](#parameter-include_subscribed)

Example: `false`

Include all channels that the user is subscribed to.

Defaults to `true`.

* * *

**exclude\_archived** boolean optional[](#parameter-exclude_archived)

Example: `true`

Whether to exclude archived streams from the results.

**Changes**: New in Zulip 10.0 (feature level 315).

Defaults to `true`.

* * *

**include\_all\_active** boolean optional[](#parameter-include_all_active)

Example: `true`

Include all active channels. The user must have administrative privileges to use this parameter.

Defaults to `false`.

* * *

**include\_default** boolean optional[](#parameter-include_default)

Example: `true`

Include all default channels for the user's realm.

Defaults to `false`.

* * *

**include\_owner\_subscribed** boolean optional[](#parameter-include_owner_subscribed)

Example: `true`

If the user is a bot, include all channels that the bot's owner is subscribed to.

Defaults to `false`.

* * *

Response
--------

#### Return values

*   `streams`: (object)\[\]
    
    A list of channel objects with details on the requested channels.
    
    *   `stream_id`: integer
        
        The unique ID of the channel.
        
    *   `name`: string
        
        The name of the channel.
        
    *   `is_archived`: boolean
        
        A boolean indicating whether the channel is [archived](https://zulip.com/help/archive-a-channel).
        
        **Changes**: New in Zulip 10.0 (feature level 315). Previously, this endpoint never returned archived channels.
        
    *   `description`: string
        
        The short description of the channel in text/markdown format, intended to be used to prepopulate UI for editing a channel's description.
        
    *   `date_created`: integer
        
        The UNIX timestamp for when the channel was created, in UTC seconds.
        
        **Changes**: New in Zulip 4.0 (feature level 30).
        
    *   `creator_id`: integer | null
        
        The ID of the user who created this channel.
        
        A `null` value means the channel has no recorded creator, which is often because the channel is very old, or because it was created via a data import tool or [management command](https://zulip.readthedocs.io/en/latest/production/management-commands.html).
        
        **Changes**: New in Zulip 9.0 (feature level 254).
        
    *   `invite_only`: boolean
        
        Specifies whether the channel is private or not. Only people who have been invited can access a private channel.
        
    *   `rendered_description`: string
        
        The short description of the channel rendered as HTML, intended to be used when displaying the channel description in a UI.
        
        One should use the standard Zulip rendered\_markdown CSS when displaying this content so that emoji, LaTeX, and other syntax work correctly. And any client-side security logic for user-generated message content should be applied when displaying this HTML as though it were the body of a Zulip message.
        
    *   `is_web_public`: boolean
        
        Whether the channel has been configured to allow unauthenticated access to its message history from the web.
        
        **Changes**: New in Zulip 2.1.0.
        
    *   `stream_post_policy`: integer
        
        [Policy](https://zulip.com/api/roles-and-permissions#permission-levels) for which users can post messages to the channel.
        
        *   1 = Any user can post.
        *   2 = Only administrators can post.
        *   3 = Only [full members](https://zulip.com/api/roles-and-permissions#determining-if-a-user-is-a-full-member) can post.
        *   4 = Only moderators can post.
        
        **Changes**: New in Zulip 3.0 (feature level 1), replacing the previous `is_announcement_only` boolean.
        
    *   `message_retention_days`: integer | null
        
        Number of days that messages sent to this channel will be stored before being automatically deleted by the [message retention policy](https://zulip.com/help/message-retention-policy). There are two special values:
        
        *   `null`, the default, means the channel will inherit the organization level setting.
        *   `-1` encodes retaining messages in this channel forever.
        
        **Changes**: New in Zulip 3.0 (feature level 17).
        
    *   `history_public_to_subscribers`: boolean
        
        Whether the history of the channel is public to its subscribers.
        
        Currently always true for public channels (i.e. `"invite_only": false` implies `"history_public_to_subscribers": true`), but clients should not make that assumption, as we may change that behavior in the future.
        
    *   `first_message_id`: integer | null
        
        The ID of the first message in the channel.
        
        Intended to help clients determine whether they need to display UI like the "show all topics" widget that would suggest the channel has older history that can be accessed.
        
        Is `null` for channels with no message history.
        
        **Changes**: New in Zulip 2.1.0.
        
    *   `is_recently_active`: boolean
        
        Whether the channel has recent message activity. Clients should use this to implement [sorting inactive channels to the bottom](https://zulip.com/help/manage-inactive-channels) if `demote_inactive_streams` is enabled.
        
        **Changes**: New in Zulip 10.0 (feature level 323). Previously, clients implemented the demote\_inactive\_streams from local message history, resulting in a choppy loading experience.
        
    *   `is_announcement_only`: boolean
        
        Whether the given channel is announcement only or not.
        
        **Changes**: Deprecated in Zulip 3.0 (feature level 1). Clients should use `stream_post_policy` instead.
        
    *   `can_remove_subscribers_group`: integer | object
        
        A [group-setting value](https://zulip.com/api/group-setting-values) defining the set of users who have permission to remove subscribers from this channel.
        
        Administrators can always unsubscribe others from a channel.
        
        Note that a user who is a member of the specified user group must also [have access](https://zulip.com/help/channel-permissions) to the channel in order to unsubscribe others.
        
        **Changes**: Prior to Zulip 10.0 (feature level 320), this value was always the integer ID of a system group.
        
        Before Zulip 8.0 (feature level 197), the `can_remove_subscribers_group` setting was named `can_remove_subscribers_group_id`.
        
        New in Zulip 6.0 (feature level 142).
        
        *   The ID of the [user group](https://zulip.com/help/user-groups) with this permission.
            
        *   An object with these fields:
            
            *   `direct_members`: (integer)\[\]
                
                The list of IDs of individual users in the collection of users with this permission.
                
                **Changes**: Prior to Zulip 10.0 (feature level 303), this list would include deactivated users who had the permission before being deactivated.
                
            *   `direct_subgroups`: (integer)\[\]
                
                The list of IDs of the groups in the collection of users with this permission.
                
    *   `can_administer_channel_group`: integer | object
        
        A [group-setting value](https://zulip.com/api/group-setting-values) defining the set of users who have permission to administer this channel.
        
        Note that a user who is a member of the specified user group must also [have access](https://zulip.com/help/channel-permissions) to the channel in order to administer the channel.
        
        Realm admins are allowed to administer a channel they have access to regardless of whether they are present in this group.
        
        Users in this group can edit channel name and description without subscribing to the channel, but they need to be subscribed to edit channel permissions and add users.
        
        **Changes**: New in Zulip 10.0 (feature level 325). Prior to this change, the permission to administer channels was limited to realm administrators.
        
        *   The ID of the [user group](https://zulip.com/help/user-groups) with this permission.
            
        *   An object with these fields:
            
            *   `direct_members`: (integer)\[\]
                
                The list of IDs of individual users in the collection of users with this permission.
                
                **Changes**: Prior to Zulip 10.0 (feature level 303), this list would include deactivated users who had the permission before being deactivated.
                
            *   `direct_subgroups`: (integer)\[\]
                
                The list of IDs of the groups in the collection of users with this permission.
                
    *   `stream_weekly_traffic`: integer | null
        
        The average number of messages sent to the channel per week, as estimated based on recent weeks, rounded to the nearest integer.
        
        If `null`, no information is provided on the average traffic. This can be because the channel was recently created and there is insufficient data to make an estimate, or because the server wishes to omit this information for this client, this realm, or this endpoint or type of event.
        
        **Changes**: New in Zulip 8.0 (feature level 199). Previously, this statistic was available only in subscription objects.
        
    *   `is_default`: boolean
        
        Only present when [`include_default`](https://zulip.com/api/get-streams#parameter-include_default) parameter is `true`.
        
        Whether the given channel is a [default channel](https://zulip.com/help/set-default-channels-for-new-users).
        

#### Example response(s)

**Changes**: As of Zulip 7.0 (feature level 167), if any parameters sent in the request are not supported by this endpoint, a successful JSON response will include an [`ignored_parameters_unsupported`](https://zulip.com/api/rest-error-handling#ignored-parameters) array.

A typical successful JSON response may look like:

```
{
    "msg": "",
    "result": "success",
    "streams": [
        {
            "can_remove_subscribers_group": 10,
            "creator_id": null,
            "date_created": 1691057093,
            "description": "A private channel",
            "first_message_id": 18,
            "history_public_to_subscribers": false,
            "invite_only": true,
            "is_announcement_only": false,
            "is_archived": false,
            "is_default": false,
            "is_recently_active": true,
            "is_web_public": false,
            "message_retention_days": null,
            "name": "management",
            "rendered_description": "<p>A private channel</p>",
            "stream_id": 2,
            "stream_post_policy": 1,
            "stream_weekly_traffic": null
        },
        {
            "can_remove_subscribers_group": 9,
            "creator_id": 12,
            "date_created": 1691057093,
            "description": "A default public channel",
            "first_message_id": 21,
            "history_public_to_subscribers": true,
            "invite_only": false,
            "is_announcement_only": false,
            "is_archived": false,
            "is_default": true,
            "is_recently_active": true,
            "is_web_public": false,
            "message_retention_days": null,
            "name": "welcome",
            "rendered_description": "<p>A default public channel</p>",
            "stream_id": 1,
            "stream_post_policy": 1,
            "stream_weekly_traffic": null
        }
    ]
}

```


An example JSON response for when the user is not authorized to use the `include_all_active` parameter (i.e. because they are not an organization administrator):

```
{
    "code": "BAD_REQUEST",
    "msg": "User not authorized for this query",
    "result": "error"
}

```
