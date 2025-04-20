from __future__ import annotations

import base64
import hashlib
import hmac
import os
import struct

import nacl.signing as ed25519
from mnemonic import Mnemonic

from .ed25519_publickey import Ed25519PublicKey
from .keypair import Keypair
from .publickey import SignatureScheme

__all__ = ["Ed25519Keypair"]


class Ed25519Keypair(Keypair):
    def __init__(self, seed: bytes) -> None:
        self._signing_key = ed25519.SigningKey(seed)
        self.seed = seed
        self.secret_key = self._signing_key
        self.public_key = bytes(self._signing_key.verify_key)

    @classmethod
    def generate(cls) -> Ed25519Keypair:
        """Generate a new random Ed25519 keypair."""
        seed = os.urandom(32)
        return cls(seed)

    @classmethod
    def from_seed(cls, seed: bytes) -> Ed25519Keypair:
        """Generate an Ed25519 keypair from a 32 byte seed."""
        return cls(seed)

    @classmethod
    def from_private_key(cls, private_key: bytes) -> Ed25519Keypair:
        """Generate an Ed25519 keypair from a 64 byte private key."""
        seed = private_key[:32]
        return cls(seed)

    def get_public_key(self) -> Ed25519PublicKey:
        """Return the public key for this keypair."""
        return Ed25519PublicKey(self.public_key)

    def sign_data(self, data: bytes) -> bytes:
        """Return the signature for the provided data using Ed25519."""
        return self._signing_key.sign(data).signature

    def get_key_scheme(self) -> SignatureScheme:
        """Get the key scheme of the keypair ED25519."""
        return SignatureScheme.ED25519

    @classmethod
    def derive_keypair(
        cls,
        mnemonic: str,
        change_index: int = 0,
        address_index: int = 0,
        passphrase: str = "",
    ):
        """Derive Ed25519 keypair from mnemonics and path.

        path format: m/44'/784'/0'/{change_index}'/{address_index}'
        """
        seed = Mnemonic.to_seed(mnemonic, passphrase)
        derived_seed = _derive(seed, 0, change_index, address_index)
        return cls.from_seed(derived_seed)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.seed == other.seed

    def __repr__(self):
        return f"<Ed25519Keypair {base64.b64encode(self.public_key)!r}>"


_SEED_MODIFIER = b"ed25519 seed"
_FIRST_HARDENED_INDEX = 0x80000000
_ED25519_PATH_FORMAT = "m/44'/784'/%d'/%d'/%d'"


def _derive(
    seed: bytes, account_index: int, change_index: int, address_index: int
) -> bytes:
    # References https://github.com/satoshilabs/slips/blob/master/slip-0010.md
    master_hmac = hmac.new(_SEED_MODIFIER, digestmod=hashlib.sha512)
    master_hmac.update(seed)
    il = master_hmac.digest()[:32]
    ir = master_hmac.digest()[32:]
    path = _ED25519_PATH_FORMAT % (account_index, change_index, address_index)
    for x in path.split("/")[1:]:
        data = (
            struct.pack("x")
            + il
            + struct.pack(">I", _FIRST_HARDENED_INDEX + int(x[:-1]))
        )
        i = hmac.new(ir, digestmod=hashlib.sha512)
        i.update(data)
        il = i.digest()[:32]
        ir = i.digest()[32:]
    return il
