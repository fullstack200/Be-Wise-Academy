import boto3
import os
from botocore.exceptions import ClientError
import environ

# Load environment variables
env = environ.Env()
environ.Env.read_env()  # Ensure .env is loaded

# Fetch environment variables correctly
bucket_name = env("AWS_STORAGE_BUCKET_NAME", default=None)
aws_access_key = env("AWS_ACCESS_KEY_ID", default=None)
aws_secret_key = env("AWS_SECRET_ACCESS_KEY", default=None)

# Debugging - Print Environment Variables
print(f"🔹 AWS_STORAGE_BUCKET_NAME: {bucket_name}")  # Should not be None
print(f"🔹 AWS_ACCESS_KEY_ID: {aws_access_key}")  # Should not be None

# Validate that variables are set
if not bucket_name or not aws_access_key or not aws_secret_key:
    print("❌ ERROR: Missing environment variables! Check your .env file.")
    exit(1)  # Stop execution if env variables are missing

# Initialize S3 client with credentials
s3 = boto3.client(
    "s3",
    aws_access_key_id=aws_access_key,
    aws_secret_access_key=aws_secret_key,
    region_name="ap-south-1"
)

# Define file path in S3
template_s3_key = "static/invoice_template.pdf"  # Corrected path

try:
    # 🔹 Step 1: Check if the file exists in S3
    s3.head_object(Bucket=bucket_name, Key=template_s3_key)
    print("✅ File exists in S3!")

    # 🔹 Step 2: Download the file
    download_path = "downloaded_invoice_template.pdf"
    s3.download_file(bucket_name, template_s3_key, download_path)
    print(f"✅ File downloaded successfully: {download_path}")

except ClientError as e:
    print(f"❌ Error accessing file: {e}")

