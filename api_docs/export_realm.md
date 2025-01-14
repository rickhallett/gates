# Create a data export | Zulip API documentation
This endpoint is only available to organization administrators.

`POST https://yourZulipDomain.zulipchat.com/api/v1/export/realm`

Create a public or a standard [data export](https://zulip.com/help/export-your-organization#export-for-migrating-to-zulip-cloud-or-a-self-hosted-server) of the organization.

**Changes**: Prior to Zulip 10.0 (feature level 304), only public data exports could be created using this endpoint.

New in Zulip 2.1.

Usage examples
--------------

*   Python
*   curl

```
#!/usr/bin/env python

import zulip

# The user for this zuliprc file must be an organization administrator
client = zulip.Client(config_file="~/zuliprc-admin")

# Create a public data export of the organization.
result = client.call_endpoint(url="/export/realm", method="POST")
print(result)

```


```
curl -sSX POST https://yourZulipDomain.zulipchat.com/api/v1/export/realm \
    -u BOT_EMAIL_ADDRESS:BOT_API_KEY \
    --data-urlencode export_type=2

```


Parameters
----------

**export\_type** integer optional[](#parameter-export_type)

Example: `2`

Whether to create a public or a standard data export.

*   1 = Public data export.
*   2 = Standard data export.

If not specified, defaults to 1.

**Changes**: New in Zulip 10.0 (feature level 304). Previously, all export requests were public data exports.

Must be one of: `1`, `2`. Defaults to `1`.

* * *

Response
--------

#### Return values

*   `id`: integer
    
    The ID of the data export created.
    
    **Changes**: New in Zulip 7.0 (feature level 182).
    

#### Example response(s)

**Changes**: As of Zulip 7.0 (feature level 167), if any parameters sent in the request are not supported by this endpoint, a successful JSON response will include an [`ignored_parameters_unsupported`](https://zulip.com/api/rest-error-handling#ignored-parameters) array.

A typical successful JSON response may look like:

```
{
    "id": 1,
    "msg": "",
    "result": "success"
}

```


An example JSON error response for when the data export exceeds the maximum allowed data export size.

```
{
    "code": "BAD_REQUEST",
    "msg": "Please request a manual export from zulip-admin@example.com.",
    "result": "error"
}

```
