import base64
import hashlib

from .publickey import PublicKey, SignatureSchemeToFlag

__all__ = ["Secp256k1PublicKey"]

SECP256K1_PUBLIC_KEY_SIZE = 33


class Secp256k1PublicKey(PublicKey):
    def __init__(self, public_key: bytes):
        self.public_key = public_key

    def to_base64(self) -> bytes:
        return base64.b64encode(self.public_key)

    def to_sui_address(self) -> str:
        tmp = SignatureSchemeToFlag.Secp256k1.value + self.public_key
        return hashlib.sha3_256(tmp).digest().hex()[:40]

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.public_key == other.public_key

    def __repr__(self):
        return f"<Secp256k1PublicKey {self.to_base64().decode()!r}>"
