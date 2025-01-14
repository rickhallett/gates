# Real-time events API | Zulip API documentation
Zulip's real-time events API lets you write software that reacts immediately to events happening in Zulip. This API is what powers the real-time updates in the Zulip web and mobile apps. As a result, the events available via this API cover all changes to data displayed in the Zulip product, from new messages to channel descriptions to emoji reactions to changes in user or organization-level settings.

Using the events API
--------------------

The simplest way to use Zulip's real-time events API is by using `call_on_each_event` from our Python bindings. You just need to write a Python function (in the examples below, the `lambda`s) and pass it into `call_on_each_event`; your function will be called whenever a new event matching the specified parameters (`event_types`, `narrow`, etc.) occurs in Zulip.

`call_on_each_event` takes care of all the potentially tricky details of long-polling, error handling, exponential backoff in retries, etc. It's cousin, `call_on_each_message`, provides an even simpler interface for processing Zulip messages.

More complex applications (like a Zulip terminal client) may need to instead use the raw [register](https://zulip.com/api/register-queue) and [events](https://zulip.com/api/get-events) endpoints.

Usage examples
--------------

*   Python

```
#!/usr/bin/env python

import sys
import zulip

# Pass the path to your zuliprc file here.
client = zulip.Client(config_file="~/zuliprc")

# Print every message the current user would receive
# This is a blocking call that will run forever
client.call_on_each_message(lambda msg: sys.stdout.write(str(msg) + "\n"))

# Print every event relevant to the user
# This is a blocking call that will run forever
client.call_on_each_event(lambda event: sys.stdout.write(str(event) + "\n"))

```


Parameters
----------

You may also pass in the following keyword arguments to `call_on_each_event`:

**event\_types** (string)\[\] optional[](#parameter-event_types)

Example: `["message"]`

A JSON-encoded array indicating which types of events you're interested in. Values that you might find useful include:

*   **message** (messages)
*   **subscription** (changes in your subscriptions)
*   **realm\_user** (changes to users in the organization and their properties, such as their name).

If you do not specify this parameter, you will receive all events, and have to filter out the events not relevant to your client in your client code. For most applications, one is only interested in messages, so one specifies: `"event_types": ["message"]`

Event types not supported by the server are ignored, in order to simplify the implementation of client apps that support multiple server versions.

* * *

**narrow** ((string)\[\])\[\] optional[](#parameter-narrow)

Example: `[["channel", "Denmark"]]`

A JSON-encoded array of arrays of length 2 indicating the [narrow filter(s)](https://zulip.com/api/construct-narrow) for which you'd like to receive events for.

For example, to receive events for direct messages (including group direct messages) received by the user, one can use `"narrow": [["is", "dm"]]`.

Unlike the API for [fetching messages](https://zulip.com/api/get-messages), this narrow parameter is simply a filter on messages that the user receives through their channel subscriptions (or because they are a recipient of a direct message).

This means that a client that requests a `narrow` filter of `[["channel", "Denmark"]]` will receive events for new messages sent to that channel while the user is subscribed to that channel. The client will not receive any message events at all if the user is not subscribed to `"Denmark"`.

Newly created bot users are not usually subscribed to any channels, so bots using this API need to be [subscribed](https://zulip.com/api/subscribe) to any channels whose messages you'd like them to process using this endpoint.

See the `all_public_streams` parameter for how to process all public channel messages in an organization.

**Changes**: See [changes section](https://zulip.com/api/construct-narrow#changes) of search/narrow filter documentation.

Defaults to `[]`.

* * *

**all\_public\_streams** boolean optional[](#parameter-all_public_streams)

Example: `true`

Whether you would like to request message events from all public channels. Useful for workflow bots that you'd like to see all new messages sent to public channels. (You can also subscribe the user to private channels).

Defaults to `false`.

* * *

See the [GET /events](https://zulip.com/api/get-events) documentation for more details on the format of individual events.