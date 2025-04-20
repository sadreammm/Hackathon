from __future__ import annotations

import base64
import binascii
import os

import secp256k1
from hdwallet import HDWallet

from .keypair import Keypair
from .publickey import SignatureScheme
from .secp256k1_publickey import Secp256k1PublicKey

__all__ = ["Secp256k1Keypair"]


class Secp256k1Keypair(Keypair):
    def __init__(self, seed: bytes) -> None:
        self._signing_key = secp256k1.PrivateKey(seed)
        self.seed = seed
        self.private_key = self._signing_key.private_key
        self.public_key = self._signing_key.pubkey.serialize()  # 33 bytes

    @classmethod
    def generate(cls) -> Secp256k1Keypair:
        """Generate a new random Secp256k1 keypair."""
        seed = os.urandom(32)
        return cls(seed)

    @classmethod
    def from_seed(cls, seed: bytes) -> Secp256k1Keypair:
        """Generate a Secp256k1 keypair from a 32 byte seed."""
        return cls(seed)

    @classmethod
    def from_private_key(cls, private_key: bytes) -> Secp256k1Keypair:
        """Generate a Secp256k1 keypair from a 32 byte private key."""
        seed = private_key
        return cls(seed)

    def get_public_key(self) -> Secp256k1PublicKey:
        """Return the public key for this keypair."""
        return Secp256k1PublicKey(self.public_key)

    def sign_data(self, data: bytes) -> bytes:
        """Return the signature for the provided data using Secp256k1."""
        pass

    def get_key_scheme(self) -> SignatureScheme:
        """Get the key scheme of the keypair Secp256k1."""
        return SignatureScheme.Secp256k1

    @classmethod
    def derive_keypair(
        cls,
        mnemonic: str,
        account_index: int = 0,
        change_index: int = 0,
        address_index: int = 0,
        passphrase: str = "",
    ):
        """Derive Secp256k1 keypair from mnemonics and path.

        path format: m/54'/784'/{account_index}'/{change_index}/{address_index}
        """
        hd_wallet = HDWallet()
        hd_wallet.from_mnemonic(mnemonic=mnemonic, passphrase=passphrase)
        hd_wallet.from_path(
            f"m/54'/784'/{account_index}'/{change_index}/{address_index}"
        )
        seed = binascii.unhexlify(hd_wallet.private_key())
        return cls.from_seed(seed)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.seed == other.seed

    def __repr__(self):
        return f"<Secp256k1Keypair {base64.b64encode(self.public_key)!r}>"
