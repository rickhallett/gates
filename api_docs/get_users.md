# Get all users | Zulip API documentation
`GET https://yourZulipDomain.zulipchat.com/api/v1/users`

Retrieve details on all users in the organization. Optionally includes values of [custom profile fields](https://zulip.com/help/custom-profile-fields).

You can also [fetch details on a single user](https://zulip.com/api/get-user).

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

# Get all users in the organization.
result = client.get_members()
# You may pass the `client_gravatar` query parameter as follows:
result = client.get_members({"client_gravatar": False})
# You may pass the `include_custom_profile_fields` query parameter as follows:
result = client.get_members({"include_custom_profile_fields": True})
print(result)

```


More examples and documentation can be found [here](https://github.com/zulip/zulip-js).

```
const zulipInit = require("zulip-js");

// Pass the path to your zuliprc file here.
const config = { zuliprc: "zuliprc" };

(async () => {
    const client = await zulipInit(config);

    // Get all users in the realm
    console.log(await client.users.retrieve());

    // You may pass the `client_gravatar` query parameter as follows:
    console.log(await client.users.retrieve({client_gravatar: true}));
})();

```


```
curl -sSX GET -G https://yourZulipDomain.zulipchat.com/api/v1/users \
    -u BOT_EMAIL_ADDRESS:BOT_API_KEY

```


You may pass the `client_gravatar` query parameter as follows:

```
curl -sSX GET -G https://yourZulipDomain.zulipchat.com/api/v1/users \
    -u BOT_EMAIL_ADDRESS:BOT_API_KEY \
    --data-urlencode client_gravatar=false \
    --data-urlencode include_custom_profile_fields=true

```


Parameters
----------

**client\_gravatar** boolean optional[](#parameter-client_gravatar)

Example: `false`

Whether the client supports computing gravatars URLs. If enabled, `avatar_url` will be included in the response only if there is a Zulip avatar, and will be `null` for users who are using gravatar as their avatar. This option significantly reduces the compressed size of user data, since gravatar URLs are long, random strings and thus do not compress well. The `client_gravatar` field is set to `true` if clients can compute their own gravatars.

**Changes**: The default value of this parameter was `false` prior to Zulip 5.0 (feature level 92).

Defaults to `true`.

* * *

**include\_custom\_profile\_fields** boolean optional[](#parameter-include_custom_profile_fields)

Example: `true`

Whether the client wants [custom profile field](https://zulip.com/help/custom-profile-fields) data to be included in the response.

**Changes**: New in Zulip 2.1.0. Previous versions do not offer these data via the API.

Defaults to `false`.

* * *

Response
--------

#### Return values

*   `members`: (object)\[\]
    
    A list of `user` objects, each containing details about a user in the organization.
    
    *   `user_id`: integer
        
        The unique ID of the user.
        
    *   `delivery_email`: string | null
        
        The user's real email address. This value will be `null` if you cannot access user's real email address. For bot users, this field is always set to the real email of the bot, because bot users always have `email_address_visibility` set to everyone.
        
        **Changes**: Prior to Zulip 7.0 (feature level 163), this field was present only when `email_address_visibility` was restricted and you had access to the user's real email. As of this feature level, this field is always present, including the case when `email_address_visibility` is set to everyone (and therefore not restricted).
        
    *   `email`: string
        
        The Zulip API email address of the user or bot.
        
        If you do not have permission to view the email address of the target user, this will be a fake email address that is usable for the Zulip API but nothing else.
        
    *   `full_name`: string
        
        Full name of the user or bot, used for all display purposes.
        
    *   `date_joined`: string
        
        The time the user account was created.
        
    *   `is_active`: boolean
        
        A boolean specifying whether the user account has been deactivated.
        
    *   `is_owner`: boolean
        
        A boolean specifying whether the user is an organization owner. If true, `is_admin` will also be true.
        
        **Changes**: New in Zulip 3.0 (feature level 8).
        
    *   `is_admin`: boolean
        
        A boolean specifying whether the user is an organization administrator.
        
    *   `is_guest`: boolean
        
        A boolean specifying whether the user is a guest user.
        
    *   `is_billing_admin`: boolean
        
        A boolean specifying whether the user is a billing administrator.
        
        **Changes**: New in Zulip 5.0 (feature level 73).
        
    *   `is_bot`: boolean
        
        A boolean specifying whether the user is a bot or full account.
        
    *   `bot_type`: integer | null
        
        An integer describing the type of bot:
        
        *   `null` if the user isn't a bot.
        *   `1` for a `Generic` bot.
        *   `2` for an `Incoming webhook` bot.
        *   `3` for an `Outgoing webhook` bot.
        *   `4` for an `Embedded` bot.
    *   `bot_owner_id`: integer | null
        
        If the user is a bot (i.e. `is_bot` is true), then `bot_owner_id` is the user ID of the bot's owner (usually, whoever created the bot).
        
        Will be `null` for legacy bots that do not have an owner.
        
        **Changes**: New in Zulip 3.0 (feature level 1). In previous versions, there was a `bot_owner` field containing the email address of the bot's owner.
        
    *   `role`: integer
        
        [Organization-level role](https://zulip.com/api/roles-and-permissions) of the user. Possible values are:
        
        *   100 = Organization owner
        *   200 = Organization administrator
        *   300 = Organization moderator
        *   400 = Member
        *   600 = Guest
        
        **Changes**: New in Zulip 4.0 (feature level 59).
        
    *   `timezone`: string
        
        The time zone of the user.
        
    *   `avatar_url`: string | null
        
        URL for the user's avatar.
        
        Will be `null` if the `client_gravatar` query parameter was set to `true`, the current user has access to this user's real email address, and this user's avatar is hosted by the Gravatar provider (i.e. this user has never uploaded an avatar).
        
        **Changes**: Before Zulip 7.0 (feature level 163), access to a user's real email address was a realm-level setting. As of this feature level, `email_address_visibility` is a user setting.
        
        In Zulip 3.0 (feature level 18), if the client has the `user_avatar_url_field_optional` capability, this will be missing at the server's sole discretion.
        
    *   `avatar_version`: integer
        
        Version for the user's avatar. Used for cache-busting requests for the user's avatar. Clients generally shouldn't need to use this; most avatar URLs sent by Zulip will already end with `?v={avatar_version}`.
        
    *   `profile_data`: object
        
        Only present if `is_bot` is false; bots can't have custom profile fields.
        
        A dictionary containing custom profile field data for the user. Each entry maps the integer ID of a custom profile field in the organization to a dictionary containing the user's data for that field. Generally the data includes just a single `value` key; for those custom profile fields supporting Markdown, a `rendered_value` key will also be present.
        
        *   `{id}`: object
            
            Object with data about what value the user filled in the custom profile field with that ID.
            
            *   `value`: string
                
                User's personal value for this custom profile field.
                
            *   `rendered_value`: string
                
                The `value` rendered in HTML. Will only be present for custom profile field types that support Markdown rendering.
                
                This user-generated HTML content should be rendered using the same CSS and client-side security protections as are used for message content.
                

#### Example response(s)

**Changes**: As of Zulip 7.0 (feature level 167), if any parameters sent in the request are not supported by this endpoint, a successful JSON response will include an [`ignored_parameters_unsupported`](https://zulip.com/api/rest-error-handling#ignored-parameters) array.

A typical successful JSON response may look like:

```
{
    "members": [
        {
            "avatar_url": "https://secure.gravatar.com/avatar/818c212b9f8830dfef491b3f7da99a14?d=identicon&version=1",
            "bot_type": null,
            "date_joined": "2019-10-20T07:50:53.728864+00:00",
            "delivery_email": null,
            "email": "AARON@zulip.com",
            "full_name": "aaron",
            "is_active": true,
            "is_admin": false,
            "is_billing_admin": false,
            "is_bot": false,
            "is_guest": false,
            "is_owner": false,
            "profile_data": {},
            "role": 400,
            "timezone": "",
            "user_id": 7
        },
        {
            "avatar_url": "https://secure.gravatar.com/avatar/6d8cad0fd00256e7b40691d27ddfd466?d=identicon&version=1",
            "bot_type": null,
            "date_joined": "2019-10-20T07:50:53.729659+00:00",
            "delivery_email": null,
            "email": "hamlet@zulip.com",
            "full_name": "King Hamlet",
            "is_active": true,
            "is_admin": false,
            "is_billing_admin": false,
            "is_bot": false,
            "is_guest": false,
            "is_owner": false,
            "profile_data": {
                "1": {
                    "rendered_value": "<p>+0-11-23-456-7890</p>",
                    "value": "+0-11-23-456-7890"
                },
                "2": {
                    "rendered_value": "<p>I am:</p>\n<ul>\n<li>The prince of Denmark</li>\n<li>Nephew to the usurping Claudius</li>\n</ul>",
                    "value": "I am:\n* The prince of Denmark\n* Nephew to the usurping Claudius"
                },
                "3": {
                    "rendered_value": "<p>Dark chocolate</p>",
                    "value": "Dark chocolate"
                },
                "4": {
                    "value": "0"
                },
                "5": {
                    "value": "1900-01-01"
                },
                "6": {
                    "value": "https://blog.zulig.org"
                },
                "7": {
                    "value": "[11]"
                },
                "8": {
                    "value": "zulipbot"
                }
            },
            "role": 400,
            "timezone": "",
            "user_id": 10
        },
        {
            "avatar_url": "https://secure.gravatar.com/avatar/7328586831cdbb1627649bd857b1ee8c?d=identicon&version=1",
            "bot_owner_id": 11,
            "bot_type": 1,
            "date_joined": "2019-10-20T12:52:17.862053+00:00",
            "delivery_email": "iago-bot@zulipdev.com",
            "email": "iago-bot@zulipdev.com",
            "full_name": "Iago's Bot",
            "is_active": true,
            "is_admin": false,
            "is_billing_admin": false,
            "is_bot": true,
            "is_guest": false,
            "is_owner": false,
            "role": 400,
            "timezone": "",
            "user_id": 23
        }
    ],
    "msg": "",
    "result": "success"
}

```
