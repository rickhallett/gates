# Subscribe to a channel | Zulip API documentation
`POST https://yourZulipDomain.zulipchat.com/api/v1/users/me/subscriptions`

Subscribe one or more users to one or more channels.

If any of the specified channels do not exist, they are automatically created. The initial [channel settings](https://zulip.com/api/update-stream) will be determined by the optional parameters, like `invite_only`, detailed below.

Note that the ability to subscribe oneself and/or other users to a specified channel depends on the [channel's privacy settings](https://zulip.com/help/channel-permissions).

**Changes**: Before Zulip 8.0 (feature level 208), if a user specified by the [`principals`](https://zulip.com/api/subscribe#parameter-principals) parameter was a deactivated user, or did not exist, then an HTTP status code of 403 was returned with `code: "UNAUTHORIZED_PRINCIPAL"` in the error response. As of this feature level, an HTTP status code of 400 is returned with `code: "BAD_REQUEST"` in the error response for these cases.

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

# Create and subscribe to channel "python-test".
result = client.add_subscriptions(
    streams=[
        {
            "name": "python-test",
            "description": "Channel for testing Python",
        },
    ],
)
# To subscribe other users to a channel, you may pass
# the `principals` argument, like so:
result = client.add_subscriptions(
    streams=[
        {"name": "python-test"},
    ],
    principals=[user_id],
)
print(result)

```


More examples and documentation can be found [here](https://github.com/zulip/zulip-js).

```
const zulipInit = require("zulip-js");

// Pass the path to your zuliprc file here.
const config = { zuliprc: "zuliprc" };

(async () => {
    const client = await zulipInit(config);

    // Subscribe to the channels "Verona" and "Denmark"
    const meParams = {
        subscriptions: JSON.stringify([{name: "Verona"}, {name: "Denmark"}]),
    };
    console.log(await client.users.me.subscriptions.add(meParams));

    // To subscribe another user to a channel, you may pass in
    // the `principals` parameter, like so:
    const user_id = 7;
    const anotherUserParams = {
        subscriptions: JSON.stringify([{name: "Verona"}, {name: "Denmark"}]),
        principals: JSON.stringify([user_id]),
    };
    console.log(await client.users.me.subscriptions.add(anotherUserParams));
})();

```


```
curl -sSX POST https://yourZulipDomain.zulipchat.com/api/v1/users/me/subscriptions \
    -u BOT_EMAIL_ADDRESS:BOT_API_KEY \
    --data-urlencode 'subscriptions=[{"description": "Italian city", "name": "Verona"}]'

```


To subscribe another user to a channel, you may pass in the `principals` parameter, like so:

```
curl -sSX POST https://yourZulipDomain.zulipchat.com/api/v1/users/me/subscriptions \
    -u BOT_EMAIL_ADDRESS:BOT_API_KEY \
    --data-urlencode 'subscriptions=[{"description": "Italian city", "name": "Verona"}]' \
    --data-urlencode 'principals=["ZOE@zulip.com"]'

```


Parameters
----------

**subscriptions** (object)\[\] required[](#parameter-subscriptions)

Example: `[{"name": "Verona", "description": "Italian city"}]`

A list of dictionaries containing the key `name` and value specifying the name of the channel to subscribe. If the channel does not exist a new channel is created. The description of the channel created can be specified by setting the dictionary key `description` with an appropriate value.

**subscriptions** object details:

*   `name`: string required
    
    The name of the channel.
    
    Clients should use the `max_stream_name_length` returned by the [`POST /register`](https://zulip.com/api/register-queue) endpoint to determine the maximum channel name length.
    
*   `description`: string optional
    
    The [description](https://zulip.com/help/change-the-channel-description) to use for a new channel being created, in text/markdown format.
    
    Clients should use the `max_stream_description_length` returned by the [`POST /register`](https://zulip.com/api/register-queue) endpoint to determine the maximum channel description length.
    

* * *

**principals** (string)\[\] | (integer)\[\] optional[](#parameter-principals)

Example: `["ZOE@zulip.com"]`

A list of user IDs (preferred) or Zulip API email addresses of the users to be subscribed to or unsubscribed from the channels specified in the `subscriptions` parameter. If not provided, then the requesting user/bot is subscribed.

**Changes**: The integer format is new in Zulip 3.0 (feature level 9).

* * *

**authorization\_errors\_fatal** boolean optional[](#parameter-authorization_errors_fatal)

Example: `false`

A boolean specifying whether authorization errors (such as when the requesting user is not authorized to access a private channel) should be considered fatal or not. When `true`, an authorization error is reported as such. When set to `false`, the response will be a 200 and any channels where the request encountered an authorization error will be listed in the `unauthorized` key.

Defaults to `true`.

* * *

**announce** boolean optional[](#parameter-announce)

Example: `true`

If one of the channels specified did not exist previously and is thus created by this call, this determines whether [notification bot](https://zulip.com/help/configure-automated-notices) will send an announcement about the new channel's creation.

Defaults to `false`.

* * *

**invite\_only** boolean optional[](#parameter-invite_only)

Example: `true`

As described above, this endpoint will create a new channel if passed a channel name that doesn't already exist. This parameters and the ones that follow are used to request an initial configuration of a created channel; they are ignored for channels that already exist.

This parameter determines whether any newly created channels will be private channels.

Defaults to `false`.

* * *

**is\_web\_public** boolean optional[](#parameter-is_web_public)

Example: `true`

This parameter determines whether any newly created channels will be web-public channels.

Note that creating web-public channels requires the `WEB_PUBLIC_STREAMS_ENABLED` [server setting](https://zulip.readthedocs.io/en/stable/production/settings.html) to be enabled on the Zulip server in question, the organization to have enabled the `enable_spectator_access` realm setting, and the current use to have permission under the organization's `can_create_web_public_channel_group` realm setting.

**Changes**: New in Zulip 5.0 (feature level 98).

Defaults to `false`.

* * *

**is\_default\_stream** boolean optional[](#parameter-is_default_stream)

Example: `true`

This parameter determines whether any newly created channels will be added as [default channels](https://zulip.com/help/set-default-channels-for-new-users) for new users joining the organization.

**Changes**: New in Zulip 8.0 (feature level 200). Previously, default channel status could only be changed using the [dedicated API endpoint](https://zulip.com/api/add-default-stream).

Defaults to `false`.

* * *

**history\_public\_to\_subscribers** boolean optional[](#parameter-history_public_to_subscribers)

Example: `false`

Whether the channel's message history should be available to newly subscribed members, or users can only access messages they actually received while subscribed to the channel.

Corresponds to the [shared history](https://zulip.com/help/channel-permissions) option in documentation.

* * *

**stream\_post\_policy** integer optional[](#parameter-stream_post_policy)

Example: `2`

[Policy](https://zulip.com/api/roles-and-permissions#permission-levels) for which users can post messages to the channel.

*   1 = Any user can post.
*   2 = Only administrators can post.
*   3 = Only [full members](https://zulip.com/api/roles-and-permissions#determining-if-a-user-is-a-full-member) can post.
*   4 = Only moderators can post.

**Changes**: New in Zulip 3.0 (feature level 1), replacing the previous `is_announcement_only` boolean.

Defaults to `1`.

* * *

**message\_retention\_days** string | integer optional[](#parameter-message_retention_days)

Example: `"20"`

Number of days that messages sent to this channel will be stored before being automatically deleted by the [message retention policy](https://zulip.com/help/message-retention-policy). Two special string format values are supported:

*   `"realm_default"`: Return to the organization-level setting.
*   `"unlimited"`: Retain messages forever.

**Changes**: Prior to Zulip 5.0 (feature level 91), retaining messages forever was encoded using `"forever"` instead of `"unlimited"`.

New in Zulip 3.0 (feature level 17).

* * *

**can\_remove\_subscribers\_group** integer | object optional[](#parameter-can_remove_subscribers_group)

Example: `null`

A [group-setting value](https://zulip.com/api/group-setting-values) defining the set of users who have permission to remove subscribers from this channel.

Administrators can always unsubscribe others from a channel.

Note that a user who is a member of the specified user group must also [have access](https://zulip.com/help/channel-permissions) to the channel in order to unsubscribe others.

**Changes**: Prior to Zulip 10.0 (feature level 320), this value was always the integer ID of a system group.

Before Zulip 8.0 (feature level 197), the `can_remove_subscribers_group` setting was named `can_remove_subscribers_group_id`.

New in Zulip 6.0 (feature level 142).

This parameter must be one of the following:

1.  The ID of the [user group](https://zulip.com/help/user-groups) with this permission.
    
2.  An object with the following fields:
    
    *   `direct_members`: (integer)\[\]
        
        The list of IDs of individual users in the collection of users with this permission.
        
        **Changes**: Prior to Zulip 10.0 (feature level 303), this list would include deactivated users who had the permission before being deactivated.
        
    *   `direct_subgroups`: (integer)\[\]
        
        The list of IDs of the groups in the collection of users with this permission.
        

* * *

**can\_administer\_channel\_group** integer | object optional[](#parameter-can_administer_channel_group)

Example: `null`

A [group-setting value](https://zulip.com/api/group-setting-values) defining the set of users who have permission to administer this channel.

Note that a user who is a member of the specified user group must also [have access](https://zulip.com/help/channel-permissions) to the channel in order to administer the channel.

Realm admins are allowed to administer a channel they have access to regardless of whether they are present in this group.

Users in this group can edit channel name and description without subscribing to the channel, but they need to be subscribed to edit channel permissions and add users.

**Changes**: New in Zulip 10.0 (feature level 325). Prior to this change, the permission to administer channels was limited to realm administrators.

This parameter must be one of the following:

1.  The ID of the [user group](https://zulip.com/help/user-groups) with this permission.
    
2.  An object with the following fields:
    
    *   `direct_members`: (integer)\[\]
        
        The list of IDs of individual users in the collection of users with this permission.
        
        **Changes**: Prior to Zulip 10.0 (feature level 303), this list would include deactivated users who had the permission before being deactivated.
        
    *   `direct_subgroups`: (integer)\[\]
        
        The list of IDs of the groups in the collection of users with this permission.
        

* * *

Response
--------

#### Return values

*   `subscribed`: object
    
    A dictionary where the key is the ID of the user and the value is a list of the names of the channels that user was subscribed to as a result of the request.
    
    **Changes**: Before Zulip 10.0 (feature level 289), the user keys were Zulip API email addresses, not user ID.
    
    *   `{id}`: (string)\[\]
        
        List of the names of the channels that were subscribed to as a result of the query.
        
*   `already_subscribed`: object
    
    A dictionary where the key is the ID of the user and the value is a list of the names of the channels that where the user was not added as a subscriber in this request, because they were already a subscriber.
    
    **Changes**: Before Zulip 10.0 (feature level 289), the user keys were Zulip API email addresses, not user IDs.
    
    *   `{id}`: (string)\[\]
        
        List of the names of the channels that the user is already subscribed to.
        
*   `unauthorized`: (string)\[\]
    
    A list of names of channels that the requesting user/bot was not authorized to subscribe to. Only present if `"authorization_errors_fatal": false`.
    

#### Example response(s)

**Changes**: As of Zulip 7.0 (feature level 167), if any parameters sent in the request are not supported by this endpoint, a successful JSON response will include an [`ignored_parameters_unsupported`](https://zulip.com/api/rest-error-handling#ignored-parameters) array.

A typical successful JSON response may look like:

```
{
    "already_subscribed": {
        "1": [
            "testing-help"
        ]
    },
    "msg": "",
    "result": "success",
    "subscribed": {
        "2": [
            "testing-help"
        ]
    }
}

```


An example JSON response for when the requesting user does not have access to a private channel and `"authorization_errors_fatal": true`:

```
{
    "code": "BAD_REQUEST",
    "msg": "Unable to access channel (private).",
    "result": "error"
}

```
