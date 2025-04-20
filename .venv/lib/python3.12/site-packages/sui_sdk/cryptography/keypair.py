import abc

from .publickey import SignatureScheme, PublicKey


class Keypair(metaclass=abc.ABCMeta):
    """A keypair used for signing transactions."""

    @abc.abstractmethod
    def get_public_key(self) -> PublicKey:
        """The public key for this keypair."""
        pass

    @abc.abstractmethod
    def sign_data(self, data: bytes) -> bytes:
        """Return the signature for the data."""
        pass

    @abc.abstractmethod
    def get_key_scheme(self) -> SignatureScheme:
        """Get the key scheme of the keypair."""
        pass
