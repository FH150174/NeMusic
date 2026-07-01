"""AES/RSA encryption for NetEase Cloud Music API requests."""
import base64
import json
import os
from Crypto.Cipher import AES, PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Util.Padding import pad

# NetEase's RSA public key (fixed, from web player source)
NETEASE_RSA_PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCgtRd8U7jDnAaJVBh+z1s0nHj8
XL2Fiz+WbSkLFSodDNG5o6gQ9MaqTUBMR7g/e/yiA4hJjwDH+kWFj6w3TAh2Cz7o
FxL+XlMqUdiT/ZqG1XhjsSK7uQNHDxVZrLRdRVxIW0Lo8mTLzoSZ0Hi/+nSe3J6I
DCoMt3gV1JZZUh+jKQIDAQAB
-----END PUBLIC KEY-----"""

# Fixed IV for AES
AES_IV = b"0102030405060708"

# Nonce for the first AES pass
NONCE = b"0CoJUm6Qyw8W8jud"


def _generate_aes_key():
    """Generate a random 16-byte AES key."""
    return os.urandom(16)


def _aes_encrypt(data, key, iv):
    """AES-128-CBC encrypt with PKCS7 padding."""
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return cipher.encrypt(pad(data, AES.block_size))


def _rsa_encrypt(data):
    """
    RSA encrypt using raw (no padding) encryption.
    NetEase requires RSA_NO_PADDING with 128-byte input (left zero-padded).
    """
    key = RSA.import_key(NETEASE_RSA_PUBLIC_KEY)
    # Raw RSA: c = m^e mod n
    # Convert data to integer, then do modular exponentiation
    m = int.from_bytes(data, byteorder="big")
    c = pow(m, key.e, key.n)
    # Output as 128-byte big-endian
    return c.to_bytes(128, byteorder="big")


def encrypt_request(plain_data):
    """
    Encrypt request data for NetEase API (weapi protocol).

    Returns:
        dict with keys 'params' (base64) and 'encSecKey' (hex).
    """
    text = json.dumps(plain_data)

    # First AES pass: encrypt with nonce key
    first_encrypted = _aes_encrypt(text.encode(), NONCE, AES_IV)
    first_b64 = base64.b64encode(first_encrypted).decode()

    # Second AES pass: encrypt with random key
    sec_key = _generate_aes_key()
    second_encrypted = _aes_encrypt(first_b64.encode(), sec_key, AES_IV)
    params = base64.b64encode(second_encrypted).decode()

    # RSA encrypt: reverse sec_key, left-pad to 128 bytes, raw RSA, then hex
    reversed_key = sec_key[::-1]
    # Left zero-pad to 128 bytes
    padded_key = b"\x00" * (128 - len(reversed_key)) + reversed_key
    enc_sec_key = _rsa_encrypt(padded_key).hex()

    return {"params": params, "encSecKey": enc_sec_key}
