"""Fixtures partagées : accès au backend et à l’application Flask."""

import logging
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))

logging.disable(logging.CRITICAL)

METRICS = {}


def pytest_terminal_summary(terminalreporter):
    if METRICS:
        terminalreporter.section("Qualité de détection (corpus tests/data/corpus.json)")
        terminalreporter.write_line(
            f"Précision : {METRICS['precision']:.2f} | Rappel : {METRICS['recall']:.2f} "
            f"| Cas : {METRICS['cases']}"
        )


@pytest.fixture(scope="session")
def app_module():
    """Importe l’application (construit l’analyseur une seule fois)."""
    import app as app_module
    return app_module


@pytest.fixture(scope="session")
def anonymize_module(app_module):
    import api.anonymize as anonymize_module
    return anonymize_module


@pytest.fixture(scope="session")
def client(app_module):
    app_module.app.config["TESTING"] = True
    # Le serveur n'accepte que l'hôte local et l'origine de l'extension
    app_module.app.config["SERVER_NAME"] = f"localhost:{app_module.PORT}"
    test_client = app_module.app.test_client()
    test_client.environ_base["HTTP_ORIGIN"] = app_module.EXTENSION_ORIGIN
    return test_client


@pytest.fixture(scope="session")
def models_ready(anonymize_module):
    """Saute les tests si les modèles spaCy ne sont pas installés."""
    if anonymize_module.analyzer is None:
        pytest.skip(f"Analyseur indisponible : {anonymize_module.analyzer_error}")


@pytest.fixture
def isolated_store(anonymize_module, tmp_path, monkeypatch):
    """Redirige mappings et espaces de travail vers un dossier temporaire."""
    monkeypatch.setattr(anonymize_module, "_DATA_DIR", str(tmp_path))
    monkeypatch.setattr(anonymize_module, "_MAPPINGS_FILE", str(tmp_path / "mappings.json"))
    monkeypatch.setattr(anonymize_module, "_WORKSPACES_FILE", str(tmp_path / "workspaces.json"))
    return tmp_path


@pytest.fixture
def temp_config(tmp_path, monkeypatch):
    """Copie de entities.yaml pour ne jamais modifier la vraie configuration.

    Les deux modules qui lisent le fichier (api.config pour l’endpoint,
    core.analyzer pour le rechargement de l’analyseur) sont redirigés.
    """
    import api.config as config_api
    import core.analyzer as analyzer_core

    copy = tmp_path / "entities.yaml"
    shutil.copy(analyzer_core.CONFIG_PATH, copy)
    monkeypatch.setattr(config_api, "CONFIG_PATH", copy)
    monkeypatch.setattr(analyzer_core, "CONFIG_PATH", copy)
    return copy


@pytest.fixture(scope="session")
def entities_config():
    import yaml

    with open(BACKEND / "config" / "entities.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)
