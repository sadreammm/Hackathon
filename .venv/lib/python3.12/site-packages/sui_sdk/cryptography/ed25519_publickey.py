import base64
import hashlib

from .publickey import PublicKey, SignatureSchemeToFlag

__all__ = ["Ed25519PublicKey"]

ED25519_PUBLIC_KEY_SIZE = 32


class Ed25519PublicKey(PublicKey):
    def __init__(self, public_key: bytes):
        self.public_key = public_key

    def to_base64(self) -> bytes:
        return base64.b64encode(self.public_key)

    def to_sui_address(self) -> str:
        tmp = SignatureSchemeToFlag.ED25519.value + self.public_key
        return hashlib.sha3_256(tmp).digest().hex()[:40]

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.public_key == other.public_key

    def __repr__(self):
        return f"<Ed25519PublicKey {self.to_base64().decode()!r}>"
