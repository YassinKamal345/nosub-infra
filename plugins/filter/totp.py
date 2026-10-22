"""Filtro TOTP para nosub-infra.

totp_semilla(secreto, etiqueta): semilla TOTP (base32, 160 bits) derivada de un secreto del Vault (HKDF-SHA256).
    Como wg_derivar: cada usuario tiene la suya, sobrevive a una reconstrucción y no hay que guardar más secretos.
totp_semillas(secreto, usuarios, servicio): {usuario: semilla} con etiqueta "<servicio>/<usuario>".
"""
import base64

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF


def totp_semilla(secreto, etiqueta):
    hkdf = HKDF(algorithm=hashes.SHA256(), length=20, salt=b"nosub-infra/totp", info=etiqueta.encode())
    return base64.b32encode(hkdf.derive(secreto.encode())).decode()


def totp_semillas(secreto, usuarios, servicio):
    return {u: totp_semilla(secreto, servicio + "/" + u) for u in usuarios}


class FilterModule:
    def filters(self):
        return {"totp_semilla": totp_semilla, "totp_semillas": totp_semillas}
