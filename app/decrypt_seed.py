import base64
import re
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding

def load_private_key():
    """Load student private key from PEM file."""
    with open("student_private.pem", "rb") as f:
        key_data = f.read()
    return serialization.load_pem_private_key(key_data, password=None)

def decrypt_seed(encrypted_seed_b64: str, private_key) -> str:
    """
    Decrypt base64-encoded encrypted seed using RSA/OAEP (SHA-256)
    Returns: 64-character hex string
    """

    # 1. Base64 decode
    try:
        encrypted_bytes = base64.b64decode(encrypted_seed_b64)
    except Exception:
        raise ValueError("Invalid Base64-encoded encrypted seed")

    # 2. RSA-OAEP decrypt
    try:
        decrypted_bytes = private_key.decrypt(
            encrypted_bytes,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
    except Exception:
        raise ValueError("RSA decryption failed. Check key and parameters.")

    # 3. Convert bytes → string
    decrypted_seed = decrypted_bytes.decode("utf-8").strip()

    # 4. Validate 64-char hex string
    if len(decrypted_seed) != 64:
        raise ValueError("Decrypted seed must be 64 characters")

    if not re.fullmatch(r"[0-9a-f]{64}", decrypted_seed):
        raise ValueError("Seed is not valid lowercase hex")

    return decrypted_seed


# Example usage:
if __name__ == "__main__":
    private_key = load_private_key()

    with open("encrypted_seed.txt", "r") as f:
        encrypted_seed_b64 = f.read().strip()

    seed = decrypt_seed(encrypted_seed_b64, private_key)
    
    print("Decrypted Seed:", seed)
