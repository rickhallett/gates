import boto3
import os

# Initialize an S3 client
s3 = boto3.client('s3')

# Define your bucket name and search prefix
bucket_name = 'ark-comms-main'
prefix = ''  # Replace with the desired prefix or use '' for all objects

# List objects in the bucket with the prefix
response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)

# Check if there are contents in the response
if 'Contents' in response:
    # Filter and display object keys
    for obj in response['Contents']:
        print(obj['Key'])
else:
    print("No objects found.")
