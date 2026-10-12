
import os
import json
import base64
from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def split_file(file_path, block_size=1024 * 1024):
    """Split a file into blocks of 1 MB each."""
    blocks = []

    with open(file_path, "rb") as file:
        while True:
            block = file.read(block_size)
            if not block:
                break
            blocks.append(block)

    return blocks


def encrypt_blocks(blocks, key):
    """Encrypt each block using AES-GCM."""
    aes = AESGCM(key)
    encrypted_blocks = []

    for block in blocks:
        nonce = os.urandom(12)
        encrypted_block = aes.encrypt(nonce, block, None)

        encrypted_blocks.append({
            "nonce": base64.b64encode(nonce).decode("utf-8"),
            "data": base64.b64encode(encrypted_block).decode("utf-8")
        })

    return encrypted_blocks


def decrypt_blocks(encrypted_blocks, key):
    """Decrypt encrypted blocks and return the original bytes."""
    aes = AESGCM(key)
    original_data = []

    for block in encrypted_blocks:
        nonce = base64.b64decode(block["nonce"])
        encrypted_data = base64.b64decode(block["data"])
        original_data.append(aes.decrypt(nonce, encrypted_data, None))

    return b"".join(original_data)


def save_encrypted_blocks(encrypted_blocks, output_path):
    """Save encrypted blocks to a JSON file."""
    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(encrypted_blocks, file)


def load_encrypted_blocks(input_path):
    """Load encrypted blocks from a JSON file."""
    with open(input_path, "r", encoding="utf-8") as file:
        return json.load(file)


def generate_key():
    """Generate a new 256-bit AES encryption key."""
    return AESGCM.generate_key(bit_length=256)
