import abc
from enum import Enum, IntEnum

__all__ = ["SignatureScheme"]


class SignatureScheme(IntEnum):
    ED25519 = 0
    Secp256k1 = 1


class SignatureSchemeToFlag(Enum):
    ED25519 = b"\x00"
    Secp256k1 = b"\x01"


class PublicKey(metaclass=abc.ABCMeta):
    """A public key"""

    @abc.abstractmethod
    def to_base64(self) -> bytes:
        """Return the base-64 representation of the public key."""
        pass

    @abc.abstractmethod
    def to_sui_address(self) -> str:
        """Return the Sui address associated with this public key."""
        pass
