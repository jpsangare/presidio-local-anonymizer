"""
Chiffrement des valeurs d'origine stockées dans les mappings.

La clé Fernet (AES) est générée une fois puis rangée dans le coffre du système
(Gestionnaire d'identification Windows / DPAPI via keyring) : le fichier de
mappings seul ne permet pas de retrouver les données.
"""

import logging
from functools import lru_cache

import keyring
from cryptography.fernet import Fernet, InvalidToken

logger = logging.getLogger("app.crypto")

_SERVICE = "MasqueIA"
_KEY_NAME = "mappings-key"


@lru_cache(maxsize=1)
def _fernet() -> Fernet:
    key = keyring.get_password(_SERVICE, _KEY_NAME)
    if key is None:
        key = Fernet.generate_key().decode()
        keyring.set_password(_SERVICE, _KEY_NAME, key)
        logger.info("Nouvelle clé de chiffrement créée dans le coffre du système")
    return Fernet(key.encode())


PREFIX = "enc:"


def encrypt(value: str) -> str:
    return PREFIX + _fernet().encrypt(value.encode()).decode()


def is_encrypted(value: str) -> bool:
    return value.startswith(PREFIX)


def decrypt(value: str) -> str | None:
    """Renvoie None si la valeur n'est pas déchiffrable (clé perdue ou remplacée)."""
    try:
        return _fernet().decrypt(value[len(PREFIX):].encode()).decode()
    except InvalidToken:
        return None
