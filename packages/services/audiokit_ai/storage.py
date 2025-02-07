import boto3

# Configure boto3 client to interact with MinIO/S3
s3_client = boto3.client(
    's3',
    endpoint_url="http://localhost:9000",
    aws_access_key_id="minio",
    aws_secret_access_key="minio123",
    region_name="us-east-1"
)

def upload_audio(bucket_name: str, file_name: str, file_data):
    # Upload file to specified bucket
    s3_client.upload_fileobj(file_data, bucket_name, file_name)
    return f"s3://{bucket_name}/{file_name}" 