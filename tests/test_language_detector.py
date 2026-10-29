"""Tests de la détection de langue (sans modèles NLP)."""

from core.language_detector import detect_language


def test_detects_french():
    text = "Je voudrais signaler un problème avec ma commande passée hier matin."
    assert detect_language(text) == "fr"


def test_detects_english():
    text = "I would like to report an issue with the order I placed yesterday morning."
    assert detect_language(text) == "en"


def test_unsupported_language_returns_none():
    text = "Nazywam się Jan Kowalski i mieszkam w Warszawie od kilku lat"
    assert detect_language(text) is None


def test_short_text_with_high_confidence_is_detected():
    assert detect_language("He lives in London") == "en"
    assert detect_language("Thank you") == "en"


def test_short_text_with_low_confidence_returns_none():
    assert detect_language("06 12 34 56 78") is None
    assert detect_language("bonjour") is None  # détecté « hr » à 43 %


def test_empty_text_returns_none():
    assert detect_language("   ") is None
    assert detect_language("") is None


def test_detection_is_deterministic():
    text = "Le client souhaite modifier son adresse de livraison pour demain."
    assert {detect_language(text) for _ in range(5)} == {"fr"}
