import os
import logging
import boto3
from botocore.exceptions import ClientError

def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket"""
    if object_name is None:
        object_name = os.path.basename(file_name)

    s3_client = boto3.client('s3')
    try:
        print(f"Uploading {file_name} to {bucket} as {object_name}")
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True

def download_audio_file(s3_object_name, destination):
    """Download audio file from S3"""
    try:
        s3 = boto3.client('s3')
        with open(destination, "wb") as f:
            s3.download_fileobj(Bucket='ark-comms-main', Key=s3_object_name, Fileobj=f)
            f.close()
    except Exception as e:
        raise Exception(f"Failed to download audio file: {str(e)}")

def get_s3_url_and_destination(audio_link):
    """Create a URL compatible with S3 and extract the directory path"""
    s3_object_name = "/".join(audio_link.split("/")[2:])
    destination_dir = os.path.join("audio", os.path.dirname(s3_object_name))

    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)

    return s3_object_name, destination_dir
