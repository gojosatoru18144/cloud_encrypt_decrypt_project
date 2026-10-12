
import json
import uuid
import streamlit as st

from file_operations import (
    encrypt_blocks,
    decrypt_blocks,
    generate_key,
)
from cloud_storage import (
    upload_encrypted_data,
    download_encrypted_data,
    list_stored_files,
)
from key_storage import save_key, load_key


def split_file_from_bytes(data, block_size=1024 * 1024):
    """Split file data into blocks of 1 MB."""
    return [
        data[i:i + block_size]
        for i in range(0, len(data), block_size)
    ] or [b""]


st.set_page_config(
    page_title="Secure Cloud File Storage",
    page_icon="🔐",
    layout="centered",
)

st.title("🔐 Secure Cloud File Storage")
st.write(
    "Encrypt files locally and store encrypted data "
    "in private AWS S3."
)

st.info(
    "Encryption keys are protected with a password and stored "
    "locally on this computer. Keep your password safe."
)

# --------------------------------------------------
# SECTION 1: ENCRYPT AND UPLOAD
# --------------------------------------------------

st.header("1. Encrypt and Upload a New File")

uploaded_file = st.file_uploader(
    "Choose a file to encrypt"
)

password = st.text_input(
    "Create a password to protect the encryption key",
    type="password",
    help="Use at least 5 characters. Remember this password.",
    key="upload_password",
)

if st.button("Encrypt and Upload to AWS"):
    if uploaded_file is None:
        st.warning("Please choose a file first.")

    elif len(password) < 5:
        st.warning(
            "Please enter a password of at least 5 characters."
        )

    else:
        object_key = None
        key_saved = False

        try:
            file_data = uploaded_file.getvalue()
            blocks = split_file_from_bytes(file_data)

            # Generate a new encryption key for this upload.
            encryption_key = generate_key()

            # Encrypt the file blocks before uploading.
            encrypted_blocks = encrypt_blocks(
                blocks,
                encryption_key,
            )

            object_id = uuid.uuid4().hex
            object_key = f"encrypted/{object_id}.json"

            encrypted_json = json.dumps(
                encrypted_blocks
            ).encode("utf-8")

            # Save the password-protected key locally.
            save_key(
                object_key,
                encryption_key,
                password,
            )
            key_saved = True

            # Upload only encrypted data to S3.
            s3_location = upload_encrypted_data(
                encrypted_json,
                object_key,
            )

            st.success("File encrypted and uploaded successfully!")

            st.write(f"Original filename: {uploaded_file.name}")
            st.write(f"Number of blocks: {len(blocks)}")

            st.write("S3 object key:")
            st.code(object_key)

            st.caption(
                "Keep the local saved key and remember your password. "
                "You need both to decrypt this file."
            )

        except Exception as error:
            st.error(
                f"Upload failed: {type(error).__name__}: {error}"
            )

            if key_saved:
                st.warning(
                    "A local key was saved. Do not delete it. "
                    "Check the S3 object list before retrying."
                )

# --------------------------------------------------
# SECTION 2: LIST ENCRYPTED FILES
# --------------------------------------------------

st.divider()
st.header("2. Retrieve and Decrypt a Saved File")

if st.button("Refresh Files from S3"):
    try:
        st.session_state["s3_files"] = list_stored_files()
        st.success("S3 file list refreshed.")

    except Exception as error:
        st.error(
            f"Could not list S3 files: "
            f"{type(error).__name__}: {error}"
        )

s3_files = st.session_state.get("s3_files", [])

object_keys = [
    item["key"]
    for item in s3_files
    if item["key"].startswith("encrypted/")
]

if object_keys:
    selected_key = st.selectbox(
        "Select an encrypted object",
        options=object_keys,
        key="selected_encrypted_object",
    )

    unlock_password = st.text_input(
        "Enter the password used when uploading this file",
        type="password",
        key="unlock_password",
    )

    if st.button("Download and Decrypt"):
        if len(unlock_password) < 5:
            st.warning(
                "Please enter the password you used during upload."
            )

        else:
            try:
                # Step 1: Unlock the local encryption key.
                encryption_key = load_key(
                    selected_key,
                    unlock_password,
                )

                # Step 2: Download encrypted content from S3.
                encrypted_json = download_encrypted_data(
                    selected_key
                )

                # Step 3: Decode the encrypted block data.
                encrypted_blocks = json.loads(
                    encrypted_json.decode("utf-8")
                )

                # Step 4: Decrypt the file blocks.
                original_data = decrypt_blocks(
                    encrypted_blocks,
                    encryption_key,
                )

                # Store decrypted bytes for the download button.
                st.session_state["recovered_data"] = original_data
                st.session_state["recovered_key"] = selected_key

                st.success(
                    "File downloaded and decrypted successfully!"
                )

            except FileNotFoundError as error:
                st.error(
                    f"Local encryption key not found: {error}"
                )

            except Exception as error:
                st.error(
                    f"Decryption failed: "
                    f"{type(error).__name__}: {error}"
                )

else:
    st.info(
        "No encrypted files are loaded. "
        "Click 'Refresh Files from S3' to load them."
    )

# --------------------------------------------------
# SECTION 3: DOWNLOAD RECOVERED FILE
# --------------------------------------------------

if "recovered_data" in st.session_state:
    st.divider()
    st.header("3. Download Your Recovered File")

    st.download_button(
        label="Download Recovered File",
        data=st.session_state["recovered_data"],
        file_name="recovered_file",
        mime="application/octet-stream",
        key="download_recovered_file",
    )
