"""
Détection heuristique de la langue du texte (langdetect).

Objectif : ne faire tourner le modèle NER que dans la langue du texte,
ce qui réduit les faux positifs inter-langues (ex. un mot anglais pris
pour une personne par le modèle français).
"""

import logging

from langdetect import DetectorFactory, LangDetectException, detect_langs

from core.analyzer import SUPPORTED_LANGUAGES

logger = logging.getLogger("app.language_detector")

# Résultats déterministes d'une exécution à l'autre
DetectorFactory.seed = 0

# En dessous de cette longueur, seule une confiance très élevée est acceptée
MIN_TEXT_LENGTH = 20
SHORT_TEXT_MIN_CONFIDENCE = 0.99


def detect_language(text: str) -> str | None:
    """
    Détecte la langue du texte parmi les langues prises en charge.

    Returns:
        str | None: code langue ("fr"/"en") si la détection est fiable et prise
        en charge, sinon None (le texte sera analysé dans toutes les langues).
    """
    cleaned = text.strip()
    if not cleaned:
        return None

    try:
        best = detect_langs(cleaned)[0]
    except LangDetectException:
        return None

    short = len(cleaned) < MIN_TEXT_LENGTH
    if short and best.prob < SHORT_TEXT_MIN_CONFIDENCE:
        logger.debug(f"Texte court ({len(cleaned)} car.), confiance insuffisante : {best}")
        return None

    if best.lang in SUPPORTED_LANGUAGES:
        logger.debug(f"Langue détectée : {best.lang} (confiance {best.prob:.2f})")
        return best.lang

    # Autre langue (ex. polonais, espagnol) : on analyse dans toutes les langues connues
    logger.debug(f"Langue non prise en charge détectée : {best.lang}")
    return None
