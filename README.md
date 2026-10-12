
# Secure Cloud File Storage Using AWS

## Project Overview

This project demonstrates secure file storage using file segmentation,
AES-GCM encryption, and Amazon S3 cloud storage.

Users can upload a file, divide it into blocks, encrypt the blocks,
store the encrypted data in a private S3 bucket, and retrieve and
decrypt the file.

## Technologies Used

- Python
- Streamlit
- AES-GCM authenticated encryption
- AWS S3
- Boto3
- Cryptography
- AWS CloudFront (planned; account verification pending)

## Features

- File splitting into 1 MB blocks
- Encryption before cloud upload
- Encrypted object storage in a private S3 bucket
- Password-protected local storage of encryption keys
- Download and decrypt stored files
- Browser-based Streamlit interface
- Project documentation website

## How to Run

1. Open a terminal in the project directory.
2. Activate the virtual environment:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

3. Install dependencies:

   ```powershell
   python -m pip install -r requirements.txt
   ```

4. Select the configured AWS profile:

   ```powershell
   $env:AWS_PROFILE = "securecloud"
   ```

5. Run the application:

   ```powershell
   python -m streamlit run app.py
   ```

## Security Notes

- Keep the S3 storage bucket private.
- Never commit AWS credentials or encryption keys.
- Back up password-protected key files securely.
- Losing a key or its password can prevent file recovery.

## Project Status

The local encryption/decryption workflow and AWS S3 upload/download
workflow have been tested successfully.

The project website can be previewed locally. CloudFront deployment
is pending AWS account verification.
