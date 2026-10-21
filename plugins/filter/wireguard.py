"""Filtros de WireGuard para nosub-infra.

wg_derivar(privada, etiqueta): clave privada nueva derivada de otra (HKDF-SHA256). Sirve para que OPNsense
    tenga una clave distinta en cada enlace sin guardar más secretos: todas salen de la del Vault.
wg_publica(privada): clave pública de una clave privada.
"""
import base64

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
from cryptography.hazmat.primitives.kdf.hkdf import HKDF


def wg_derivar(privada, etiqueta):
    hkdf = HKDF(algorithm=hashes.SHA256(), length=32, salt=b"nosub-infra/wireguard", info=etiqueta.encode())
    return base64.b64encode(hkdf.derive(base64.b64decode(privada))).decode()


def wg_publica(privada):
    k = X25519PrivateKey.from_private_bytes(base64.b64decode(privada))
    return base64.b64encode(k.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)).decode()


class FilterModule:
    def filters(self):
        return {"wg_derivar": wg_derivar, "wg_publica": wg_publica}
