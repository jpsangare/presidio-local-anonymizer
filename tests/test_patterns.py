"""Tests des motifs regex personnalisés (sans modèles NLP)."""

from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from presidio_analyzer import Pattern, PatternRecognizer

from core.analyzer import SUPPORTED_LANGUAGES, _add_custom_recognizers


def _recognizer(config, entity):
    entity_config = config["entities"][entity]
    patterns = [
        Pattern(name=p["name"], regex=p["regex"], score=p["score"])
        for p in entity_config["patterns"]
    ]
    return PatternRecognizer(
        supported_entity=entity,
        patterns=patterns,
        supported_language="fr",
        context=entity_config.get("context"),
    )


def _matches(config, entity, text):
    recognizer = _recognizer(config, entity)
    return [text[r.start:r.end] for r in recognizer.analyze(text, [entity])]


@pytest.mark.parametrize(
    "entity, text, expected",
    [
        ("PL_PESEL", "PESEL 92010212345 ok", ["92010212345"]),
        ("PL_NIP", "NIP 123-456-32-18", ["123-456-32-18"]),
        ("PL_NIP", "NIP 123-45-67-890", ["123-45-67-890"]),
        ("PL_NIP", "NIP 1234567890", ["1234567890"]),
        ("PL_PASSPORT", "passeport AB1234567", ["AB1234567"]),
        ("PL_ID_CARD", "carte ABC123456", ["ABC123456"]),
        ("PL_REGON", "REGON 123456789", ["123456789"]),
        ("PL_REGON", "REGON 12345678901234", ["12345678901234"]),
        ("FR_PLATE", "voiture AB-123-CD", ["AB-123-CD"]),
        ("FR_PLATE", "voiture AB 123 CD", ["AB 123 CD"]),
        ("FR_SECU", "nir 1 85 05 78 006 084 91", ["1 85 05 78 006 084 91"]),
        ("FR_SIREN", "siren 552 100 554", ["552 100 554"]),
        ("FR_SIRET", "siret 552 100 554 00013", ["552 100 554 00013"]),
        ("DATE_TIME", "le 12 mars 2024", ["12 mars 2024"]),
        ("DATE_TIME", "le 05/11/2026", ["05/11/2026"]),
    ],
)
def test_pattern_matches(entities_config, entity, text, expected):
    assert _matches(entities_config, entity, text) == expected


@pytest.mark.parametrize(
    "entity, text",
    [
        ("PL_PESEL", "numéro 1234567890 trop court"),
        ("PL_PESEL", "numéro 123456789012 trop long"),
        ("PL_PASSPORT", "code abcdefg"),
        ("PL_ID_CARD", "mot ABCDEF"),
        ("PL_NIP", "texte sans chiffres"),
        ("FR_PLATE", "code A1-234-BC"),
        ("FR_SECU", "code 3 85 05 78 006 084 91"),
        ("DATE_TIME", "le mois de mars 2024"),
    ],
)
def test_pattern_rejects(entities_config, entity, text):
    assert _matches(entities_config, entity, text) == []


def test_validator_rejects_invalid_checksum(entities_config):
    """Un numéro à la forme correcte mais à la somme de contrôle invalide est écarté."""
    from core.analyzer import ValidatedPatternRecognizer
    from core.validators import VALIDATORS

    recognizer = ValidatedPatternRecognizer(
        supported_entity="FR_SIREN",
        patterns=[Pattern(name="S", regex=r"\b\d{9}\b", score=0.4)],
        supported_language="fr",
        validator=VALIDATORS["luhn"],
    )

    assert recognizer.analyze("SIREN 123456789", ["FR_SIREN"]) == []


def test_context_words_are_wired(entities_config):
    """Les mots de contexte YAML sont transmis au recognizer (le renforcement
    lui-même est appliqué par Presidio via les artefacts NLP, cf. test API)."""
    recognizer = _recognizer(entities_config, "FR_PLATE")

    assert recognizer.context == entities_config["entities"]["FR_PLATE"]["context"]
    assert "immatriculation" in recognizer.context


def test_custom_recognizers_registered_for_every_language(entities_config):
    analyzer = SimpleNamespace(registry=Mock())

    _add_custom_recognizers(analyzer, entities_config)

    with_patterns = [e for e in entities_config["entities"].values() if e.get("patterns")]
    assert analyzer.registry.add_recognizer.call_count == len(with_patterns) * len(SUPPORTED_LANGUAGES)
    languages = {c.args[0].supported_language for c in analyzer.registry.add_recognizer.call_args_list}
    assert languages == set(SUPPORTED_LANGUAGES)
