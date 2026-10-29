"""
Module d’analyse des données personnelles utilisant Presidio AnalyzerEngine.
Configure le moteur NLP pour le polonais et ajoute des recognizers personnalisés.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any
import logging

from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern
from presidio_analyzer.nlp_engine import SpacyNlpEngine, NlpEngineProvider
from presidio_analyzer import RecognizerResult
from presidio_analyzer.entity_recognizer import EntityRecognizer

logger = logging.getLogger("app.analyzer")


def build_analyzer() -> tuple[AnalyzerEngine, Dict[str, Any]]:
    """
    Construit et configure Presidio AnalyzerEngine avec un modèle NLP polonais.

    Returns:
        tuple: (analyzer, config) - analyseur configuré et configuration chargée
    """
    # Rechercher le chemin du fichier de configuration
    config_path = Path(__file__).parent.parent / "config" / "entities.yaml"

    if not config_path.exists():
        raise FileNotFoundError(f"Fichier de configuration introuvable : {config_path}")

    # Charger la configuration
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    logger.info(f"Configuration chargée depuis : {config_path}")

    # Configuration du modèle SpaCy pour le polonais
    nlp_configuration = {
        "nlp_engine_name": "spacy",
        "models": [
            {
                "lang_code": "pl",
                "model_name": "pl_core_news_md"
            }
        ]
    }

    # Inicjalizacja silnika NLP
    try:
        nlp_engine = NlpEngineProvider(nlp_configuration=nlp_configuration).create_engine()
        logger.info("Moteur NLP SpaCy initialisé pour le polonais")
    except Exception as e:
        logger.error(f"Erreur lors de l’initialisation du moteur NLP : {e}")
        raise RuntimeError(
            "Impossible d’initialiser le modèle SpaCy. "
            "Vérifiez que le modèle pl_core_news_md est installé : "
            "python -m spacy download pl_core_news_md"
        ) from e

    # Créer AnalyzerEngine
    analyzer = AnalyzerEngine(nlp_engine=nlp_engine, supported_languages=["pl"])

    # Ajouter des recognizers personnalisés pour les entités polonaises
    _add_custom_recognizers(analyzer, config)

    # Ajouter le recognizer SpaCy pour les étiquettes NER polonaises
    _add_polish_spacy_recognizer(analyzer, nlp_engine)

    logger.info(f"Analyseur prêt. Entités prises en charge : {list(config['entities'].keys())}")

    return analyzer, config


def _add_custom_recognizers(analyzer: AnalyzerEngine, config: Dict[str, Any]) -> None:
    """
    Ajoute des recognizers personnalisés basés sur des motifs pour les entités configurées.

    Args:
        analyzer: AnalyzerEngine auquel ajouter les recognizers
        config: Dictionnaire de configuration chargé depuis YAML
    """
    for entity_name, entity_config in config['entities'].items():
        patterns = entity_config.get('patterns')

        if not patterns:
            continue  # Ignorer les entités sans motif regex

        # Préparer la liste de motifs pour PatternRecognizer
        pattern_list = []
        for pattern in patterns:
            pattern_list.append(Pattern(
                name=pattern['name'],
                regex=pattern['regex'],
                score=pattern['score']
            ))

        # Créer le recognizer
        recognizer = PatternRecognizer(
            supported_entity=entity_name,
            patterns=pattern_list,
            supported_language="pl"
        )

        # Ajouter au registre de l’analyseur
        analyzer.registry.add_recognizer(recognizer)

        logger.info(f"Recognizer personnalisé ajouté pour : {entity_name} ({len(pattern_list)} motifs)")


def _add_polish_spacy_recognizer(analyzer: AnalyzerEngine, nlp_engine) -> None:
    """
    Ajoute un recognizer SpaCy personnalisé pour les étiquettes NER polonaises.
    Associe les étiquettes polonaises (persName, placeName) aux entités Presidio (PERSON, LOCATION).

    Args:
        analyzer: AnalyzerEngine auquel ajouter le recognizer
        nlp_engine: Moteur NLP SpaCy configuré
    """

    class PolishSpacyRecognizer(EntityRecognizer):
        """Recognizer associant les étiquettes SpaCy polonaises aux entités Presidio."""

        POLISH_TO_PRESIDIO_MAPPING = {
            "persName": "PERSON",        # Prénoms et noms polonais
            "placeName": "LOCATION",      # Noms de lieux polonais
            "geogName": "LOCATION",       # Noms géographiques
            "orgName": "ORGANIZATION",    # Noms d’organisations
        }

        def __init__(self):
            # Les entités prises en charge correspondent aux valeurs du mappage
            supported_entities = list(set(self.POLISH_TO_PRESIDIO_MAPPING.values()))
            super().__init__(
                supported_entities=supported_entities,
                supported_language="pl",
                name="PolishSpacyRecognizer"
            )

        def load(self) -> None:
            """Charger le modèle — non requis pour ce recognizer."""
            pass

        def analyze(self, text: str, entities: list, nlp_artifacts=None):
            """
            Analyse le texte avec SpaCy et associe les étiquettes polonaises aux entités Presidio.

            Args:
                text: Texte à analyser
                entities: Liste des entités à détecter
                nlp_artifacts: Résultats NLP de SpaCy

            Returns:
                Liste de RecognizerResult
            """
            results = []

            if not nlp_artifacts or not hasattr(nlp_artifacts, 'entities'):
                return results

            # Parcourir les entités détectées par SpaCy
            for ent in nlp_artifacts.entities:
                # Vérifier si l’étiquette SpaCy correspond à une entité Presidio
                presidio_entity = self.POLISH_TO_PRESIDIO_MAPPING.get(ent.label_)

                if presidio_entity and presidio_entity in entities:
                    # Créer un résultat de reconnaissance
                    result = RecognizerResult(
                        entity_type=presidio_entity,
                        start=ent.start_char,
                        end=ent.end_char,
                        score=0.85  # Niveau de confiance élevé
                    )
                    results.append(result)

            return results

    # Ajouter le recognizer à l’analyseur
    polish_recognizer = PolishSpacyRecognizer()
    analyzer.registry.add_recognizer(polish_recognizer)
    logger.info("Recognizer des étiquettes SpaCy polonaises ajouté (persName->PERSON, placeName->LOCATION)")


def get_supported_entities(config: Dict[str, Any]) -> list[str]:
    """
    Renvoie la liste des noms d’entités activées dans la configuration.

    Args:
        config: Dictionnaire de configuration

    Returns:
        list: Liste des noms d’entités activées
    """
    enabled_entities = []
    for entity_name, entity_config in config['entities'].items():
        if entity_config.get('enabled', True):
            enabled_entities.append(entity_name)
    return enabled_entities
