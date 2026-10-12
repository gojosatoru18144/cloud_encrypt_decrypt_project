
import os
import boto3
import streamlit as st

BUCKET_NAME = "secure-cloud-project-2026-smit-797035623223-eu-north-1-an"
AWS_REGION = "eu-north-1"


def get_s3_client():
    """Use Streamlit Secrets online or the local AWS profile."""
    try:
        access_key = st.secrets.get("AWS_ACCESS_KEY_ID")
        secret_key = st.secrets.get("AWS_SECRET_ACCESS_KEY")
        session_token = st.secrets.get("AWS_SESSION_TOKEN")
    except Exception:
        access_key = None
        secret_key = None
        session_token = None

    if access_key and secret_key:
        session_args = {
            "aws_access_key_id": access_key,
            "aws_secret_access_key": secret_key,
            "region_name": AWS_REGION,
        }

        if session_token:
            session_args["aws_session_token"] = session_token

        session = boto3.Session(**session_args)
    else:
        # Locally, boto3 uses your configured AWS profile/environment.
        session = boto3.Session(
            profile_name=os.getenv("AWS_PROFILE") or None,
            region_name=AWS_REGION,
        )

    return session.client("s3")


def upload_encrypted_data(data, object_key):
    """Upload encrypted bytes to the private S3 bucket."""
    s3 = get_s3_client()

    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=object_key,
        Body=data,
        ContentType="application/octet-stream",
        ServerSideEncryption="AES256",
    )

    return f"s3://{BUCKET_NAME}/{object_key}"


def download_encrypted_data(object_key):
    """Download encrypted bytes from S3."""
    response = get_s3_client().get_object(
        Bucket=BUCKET_NAME,
        Key=object_key,
    )
    return response["Body"].read()


def list_stored_files():
    """List objects stored in the project bucket."""
    s3 = get_s3_client()
    paginator = s3.get_paginator("list_objects_v2")

    files = []
    for page in paginator.paginate(Bucket=BUCKET_NAME):
        files.extend(
            {
                "key": item["Key"],
                "size": item["Size"],
            }
            for item in page.get("Contents", [])
        )

    return files
