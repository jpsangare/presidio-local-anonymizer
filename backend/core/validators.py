"""
Validateurs par somme de contrôle pour les recognizers basés sur des motifs.

Un validateur reçoit le texte capturé par le motif et renvoie True/False ;
Presidio ajuste alors le score (1,0 si valide, 0 si invalide), ce qui élimine
la plupart des faux positifs des motifs purement numériques.
"""


def _digits(value: str) -> list[int]:
    return [int(c) for c in value if c.isdigit()]


def luhn_ok(value: str) -> bool:
    """Algorithme de Luhn (SIREN, SIRET, cartes bancaires…)."""
    digits = _digits(value)
    if len(digits) < 9:
        return False
    total = 0
    parity = len(digits) % 2
    for i, digit in enumerate(digits):
        if i % 2 == parity:
            digit *= 2
            total += digit - 9 if digit > 9 else digit
        else:
            total += digit
    return total % 10 == 0


def nir_ok(value: str) -> bool:
    """
    Clé du numéro de sécurité sociale français (NIR) : clé = 97 - (N mod 97).

    Corse : 2A et 2B valent respectivement 19 et 18 pour le calcul de la clé.
    """
    compact = "".join(c for c in value if c.isalnum()).upper()
    if len(compact) != 15:
        return False
    digits = compact[:5] + compact[5:7].replace("2A", "19").replace("2B", "18") + compact[7:]
    if not digits.isdigit():
        return False
    number, key = int(digits[:13]), int(digits[13:])
    return 97 - (number % 97) == key


def _check_digit(number: str, weights: list[int]) -> int:
    """Somme pondérée mod 11 ; un reste de 10 correspond au chiffre 0."""
    total = sum(int(d) * w for d, w in zip(number, weights))
    remainder = total % 11
    return 0 if remainder == 10 else remainder


def regon_ok(value: str) -> bool:
    """Somme de contrôle du REGON polonais (9 ou 14 chiffres)."""
    digits = "".join(c for c in value if c.isdigit())
    if len(digits) == 9:
        return _check_digit(digits[:8], [8, 9, 2, 3, 4, 5, 6, 7]) == int(digits[8])
    if len(digits) == 14:
        if not regon_ok(digits[:9]):
            return False
        weights = [2, 4, 8, 5, 0, 9, 7, 3, 6, 1, 2, 4, 8]
        return _check_digit(digits[:13], weights) == int(digits[13])
    return False


def nip_ok(value: str) -> bool:
    """Somme de contrôle du NIP polonais (10 chiffres ; un reste de 10 est invalide)."""
    digits = "".join(c for c in value if c.isdigit())
    if len(digits) != 10:
        return False
    total = sum(int(d) * w for d, w in zip(digits[:9], [6, 5, 7, 2, 3, 4, 5, 6, 7]))
    remainder = total % 11
    return remainder != 10 and remainder == int(digits[9])


VALIDATORS = {
    "luhn": luhn_ok,
    "nir": nir_ok,
    "regon": regon_ok,
    "nip": nip_ok,
}
