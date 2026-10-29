"""Validation de backend/config/entities.yaml (sans modèles NLP)."""

import re

from core.analyzer import SUPPORTED_LANGUAGES, get_supported_entities


def test_entities_declared(entities_config):
    assert entities_config["entities"]


def test_each_entity_is_well_formed(entities_config):
    for name, entity in entities_config["entities"].items():
        assert isinstance(entity.get("description"), str) and entity["description"], name
        assert isinstance(entity.get("enabled"), bool), name
        assert isinstance(entity.get("mask"), str) and entity["mask"], name


def test_masks_are_unique(entities_config):
    masks = [e["mask"] for e in entities_config["entities"].values()]
    assert len(masks) == len(set(masks))


def test_patterns_compile_and_have_valid_scores(entities_config):
    for name, entity in entities_config["entities"].items():
        for pattern in entity.get("patterns", []):
            assert pattern["name"], name
            re.compile(pattern["regex"])
            assert 0 < pattern["score"] <= 1, f"{name}/{pattern['name']}"


def test_global_settings(entities_config):
    assert 0 <= entities_config["threshold"] <= 1
    assert entities_config["language"] in SUPPORTED_LANGUAGES


def test_get_supported_entities_returns_only_enabled(entities_config):
    enabled = get_supported_entities(entities_config)
    expected = [n for n, e in entities_config["entities"].items() if e["enabled"]]
    assert enabled == expected
    assert "EMAIL_ADDRESS" in enabled
    assert "US_SSN" not in enabled
