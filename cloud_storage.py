
import boto3

BUCKET_NAME = "secure-cloud-project-2026-smit-797035623223-eu-north-1-an"
AWS_REGION = "eu-north-1"


def get_s3_client():
    """Create an S3 client using the configured AWS profile."""
    session = boto3.Session(region_name=AWS_REGION)
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
    s3 = get_s3_client()

    response = s3.get_object(
        Bucket=BUCKET_NAME,
        Key=object_key,
    )

    return response["Body"].read()


def list_stored_files():
    """List objects stored in the project bucket."""
    s3 = get_s3_client()

    response = s3.list_objects_v2(Bucket=BUCKET_NAME)

    return [
        {
            "key": item["Key"],
            "size": item["Size"],
        }
        for item in response.get("Contents", [])
    ]
