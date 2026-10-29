"""Tests des validateurs par somme de contrôle."""

import pytest

from core.validators import luhn_ok, nir_ok


@pytest.mark.parametrize(
    "value",
    [
        "552100554",          # SIREN valide
        "552 100 554",        # avec espaces
        "55210055400013",     # SIRET valide
        "4111 1111 1111 1111",  # carte bancaire de test
    ],
)
def test_luhn_accepts_valid_numbers(value):
    assert luhn_ok(value)


@pytest.mark.parametrize(
    "value",
    [
        "123456789",          # SIREN invalide
        "552100555",          # un chiffre modifié
        "12345678",           # trop court
        "abc",                # aucun chiffre exploitable
    ],
)
def test_luhn_rejects_invalid_numbers(value):
    assert not luhn_ok(value)


@pytest.mark.parametrize(
    "value",
    [
        "185057800608491",                # NIR valide
        "1 85 05 78 006 084 91",          # avec espaces
    ],
)
def test_nir_accepts_valid_numbers(value):
    assert nir_ok(value)


@pytest.mark.parametrize(
    "value",
    [
        "185057800608499",     # mauvaise clé
        "185057800608490",     # clé modifiée
        "185057800608",        # trop court (13 chiffres)
        "18505780060849122",   # trop long
    ],
)
def test_nir_rejects_invalid_numbers(value):
    assert not nir_ok(value)


def test_regon_validation():
    from core.validators import regon_ok

    assert regon_ok("123456785")           # REGON 9 chiffres valide
    assert regon_ok("12345678512347")      # REGON 14 chiffres valide
    assert not regon_ok("123456789")       # somme de contrôle invalide
    assert not regon_ok("12345")


def test_nip_validation():
    from core.validators import nip_ok

    assert nip_ok("123-456-32-18")
    assert nip_ok("1234563218")
    assert not nip_ok("1234567890")
    assert not nip_ok("123456789")
