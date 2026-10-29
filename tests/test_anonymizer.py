"""Tests du remplacement par masques (sans modèles NLP)."""

from presidio_analyzer import RecognizerResult

from core.anonymizer import anonymize_text


def _result(entity, start, end, score=0.9):
    return RecognizerResult(entity_type=entity, start=start, end=end, score=score)


def test_returns_text_unchanged_without_entities(entities_config):
    assert anonymize_text("Bonjour", [], entities_config) == "Bonjour"


def test_replaces_entities_with_configured_masks(entities_config):
    text = "Jean Dupont: jean@example.com"
    results = [_result("PERSON", 0, 11), _result("EMAIL_ADDRESS", 13, 29)]

    assert anonymize_text(text, results, entities_config) == "[PERSONNE]: [EMAIL]"


def test_keeps_surrounding_unicode_text(entities_config):
    text = "Écrire à jean@example.com très vite"
    start = text.index("jean")
    results = [_result("EMAIL_ADDRESS", start, start + len("jean@example.com"))]

    assert anonymize_text(text, results, entities_config) == "Écrire à [EMAIL] très vite"


def test_original_value_is_removed(entities_config):
    text = "PESEL 92010212345"
    results = [_result("PL_PESEL", 6, 17)]

    assert "92010212345" not in anonymize_text(text, results, entities_config)
