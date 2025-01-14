# Get all data exports | Zulip API documentation
This endpoint is only available to organization administrators.

`GET https://yourZulipDomain.zulipchat.com/api/v1/export/realm`

Fetch all the public and standard [data exports](https://zulip.com/help/export-your-organization#export-for-migrating-to-zulip-cloud-or-a-self-hosted-server) of the organization.

**Changes**: Prior to Zulip 10.0 (feature level 304), only public data exports could be fetched using this endpoint.

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

# Get organization's public data exports.
result = client.call_endpoint(url="/export/realm", method="GET")
print(result)

```


```
curl -sSX GET -G https://yourZulipDomain.zulipchat.com/api/v1/export/realm \
    -u BOT_EMAIL_ADDRESS:BOT_API_KEY

```


Parameters
----------

This endpoint does not accept any parameters.

Response
--------

#### Return values

*   `exports`: (object)\[\]
    
    An array of dictionaries where each dictionary contains details about a data export of the organization.
    
    *   `id`: integer
        
        The ID of the data export.
        
    *   `acting_user_id`: integer
        
        The ID of the user who created the data export.
        
    *   `export_time`: number
        
        The UNIX timestamp of when the data export was started.
        
    *   `deleted_timestamp`: number | null
        
        The UNIX timestamp of when the data export was deleted.
        
        Will be `null` if the data export has not been deleted.
        
    *   `failed_timestamp`: number | null
        
        The UNIX timestamp of when the data export failed.
        
        Will be `null` if the data export succeeded, or if it's still being generated.
        
    *   `export_url`: string | null
        
        The URL to download the generated data export.
        
        Will be `null` if the data export failed, or if it's still being generated.
        
    *   `pending`: boolean
        
        Whether the data export is pending, which indicates it is still being generated, or if it succeeded, failed or was deleted before being generated.
        
        Depending on the size of the organization, it can take anywhere from seconds to an hour to generate the data export.
        
    *   `export_type`: integer
        
        Whether the data export is a public or a standard data export.
        
        *   1 = Public data export.
        *   2 = Standard data export.
        
        **Changes**: New in Zulip 10.0 (feature level 304). Previously, the export type was not included in these objects because only public data exports could be created or listed via the API or UI.
        

#### Example response(s)

**Changes**: As of Zulip 7.0 (feature level 167), if any parameters sent in the request are not supported by this endpoint, a successful JSON response will include an [`ignored_parameters_unsupported`](https://zulip.com/api/rest-error-handling#ignored-parameters) array.

A typical successful JSON response may look like:

```
{
    "exports": [
        {
            "acting_user_id": 11,
            "deleted_timestamp": null,
            "export_time": 1722243168.134179,
            "export_type": 1,
            "export_url": "http://example.zulipchat.com/user_avatars/exports/2/FprbwiF0c_sCN0O-rf-ryFtc/zulip-export-p6yuxc45.tar.gz",
            "failed_timestamp": null,
            "id": 323,
            "pending": false
        }
    ],
    "msg": "",
    "result": "success"
}

```
