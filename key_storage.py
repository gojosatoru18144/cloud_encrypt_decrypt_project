
import base64
import hashlib
import json
import os
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt


# Store protected keys outside the project folder.
KEY_DIR = Path.home() / ".secure_cloud_project" / "keys"


def _key_file(object_key):
    """Create a safe, predictable filename for an S3 object key."""
    identifier = hashlib.sha256(object_key.encode("utf-8")).hexdigest()
    return KEY_DIR / f"{identifier}.json"


def _derive_key(password, salt):
    """Derive a wrapping key from the user's password."""
    kdf = Scrypt(
        salt=salt,
        length=32,
        n=2**14,
        r=8,
        p=1,
    )
    return kdf.derive(password.encode("utf-8"))


def save_key(object_key, encryption_key, password):
    """Encrypt an AES file key with a password and save it locally."""
    if len(password) < 5:
        raise ValueError("Use a password of at least 5 characters.")

    KEY_DIR.mkdir(parents=True, exist_ok=True)

    salt = os.urandom(16)
    wrapping_key = _derive_key(password, salt)
    nonce = os.urandom(12)

    protected_key = AESGCM(wrapping_key).encrypt(
        nonce,
        encryption_key,
        object_key.encode("utf-8"),
    )

    record = {
        "salt": base64.b64encode(salt).decode("ascii"),
        "nonce": base64.b64encode(nonce).decode("ascii"),
        "protected_key": base64.b64encode(protected_key).decode("ascii"),
    }

    path = _key_file(object_key)

    # Do not silently overwrite an existing key record.
    if path.exists():
        raise FileExistsError(
            "A saved key already exists for this object. "
            "The existing key was not changed."
        )

    path.write_text(json.dumps(record), encoding="utf-8")


def load_key(object_key, password):
    """Unlock a previously saved AES file key."""
    path = _key_file(object_key)

    if not path.exists():
        raise FileNotFoundError(
            "No saved key was found on this computer for this S3 object."
        )

    record = json.loads(path.read_text(encoding="utf-8"))

    salt = base64.b64decode(record["salt"])
    nonce = base64.b64decode(record["nonce"])
    protected_key = base64.b64decode(record["protected_key"])

    wrapping_key = _derive_key(password, salt)

    # A wrong password or modified record raises an authentication error.
    return AESGCM(wrapping_key).decrypt(
        nonce,
        protected_key,
        object_key.encode("utf-8"),
    )
