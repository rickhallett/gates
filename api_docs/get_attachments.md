# Get attachments | Zulip API documentation
`GET https://yourZulipDomain.zulipchat.com/api/v1/attachments`

Fetch metadata on files uploaded by the requesting user.

Usage examples
--------------

*   Python
*   curl

```
#!/usr/bin/env python3

import zulip

# Pass the path to your zuliprc file here.
client = zulip.Client(config_file="~/zuliprc")

# Get your attachments.
result = client.get_attachments()
print(result)

```


```
curl -sSX GET -G https://yourZulipDomain.zulipchat.com/api/v1/attachments \
    -u BOT_EMAIL_ADDRESS:BOT_API_KEY

```


Parameters
----------

This endpoint does not accept any parameters.

Response
--------

#### Return values

*   `attachments`: (object)\[\]
    
    A list of `attachment` objects, each containing details about a file uploaded by the user.
    
    *   `id`: integer
        
        The unique ID for the attachment.
        
    *   `name`: string
        
        Name of the uploaded file.
        
    *   `path_id`: string
        
        A representation of the path of the file within the repository of user-uploaded files. If the `path_id` of a file is `{realm_id}/ab/cdef/temp_file.py`, its URL will be: `{server_url}/user_uploads/{realm_id}/ab/cdef/temp_file.py`.
        
    *   `size`: integer
        
        Size of the file in bytes.
        
    *   `create_time`: integer
        
        Time when the attachment was uploaded as a UNIX timestamp multiplied by 1000 (matching the format of getTime() in JavaScript).
        
        **Changes**: Changed in Zulip 3.0 (feature level 22). This field was previously a floating point number.
        
    *   `messages`: (object)\[\]
        
        Contains basic details on any Zulip messages that have been sent referencing this [uploaded file](https://zulip.com/api/upload-file). This includes messages sent by any user in the Zulip organization who sent a message containing a link to the uploaded file.
        
        *   `date_sent`: integer
            
            Time when the message was sent as a UNIX timestamp multiplied by 1000 (matching the format of getTime() in JavaScript).
            
            **Changes**: Changed in Zulip 3.0 (feature level 22). This field was previously strangely called `name` and was a floating point number.
            
        *   `id`: integer
            
            The unique message ID. Messages should always be displayed sorted by ID.
            
*   `upload_space_used`: integer
    
    The total size of all files uploaded by users in the organization, in bytes.
    

#### Example response(s)

**Changes**: As of Zulip 7.0 (feature level 167), if any parameters sent in the request are not supported by this endpoint, a successful JSON response will include an [`ignored_parameters_unsupported`](https://zulip.com/api/rest-error-handling#ignored-parameters) array.

A typical successful JSON response may look like:

```
{
    "attachments": [
        {
            "create_time": 1588145417000,
            "id": 1,
            "messages": [
                {
                    "date_sent": 1588145424000,
                    "id": 102
                },
                {
                    "date_sent": 1588145448000,
                    "id": 103
                }
            ],
            "name": "166050.jpg",
            "path_id": "2/ce/DfOkzwdg_IwlrN3myw3KGtiJ/166050.jpg",
            "size": 571946
        }
    ],
    "msg": "",
    "result": "success",
    "upload_space_used": 571946
}

```
