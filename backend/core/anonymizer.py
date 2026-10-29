"""
Module d’anonymisation des données personnelles utilisant Presidio AnonymizerEngine.
Remplace les entités détectées par les masques définis dans la configuration.
"""

import logging
from typing import Dict, Any, List

from presidio_analyzer import RecognizerResult
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

logger = logging.getLogger("app.anonymizer")


def anonymize_text(
    text: str,
    analyzer_results: List[RecognizerResult],
    config: Dict[str, Any]
) -> str:
    """
    Anonymise le texte en remplaçant les entités détectées par les masques correspondants.

    Args:
        text: Texte à anonymiser
        analyzer_results: Liste de résultats de Presidio Analyzer
        config: Dictionnaire de configuration des masques par entité

    Returns:
        str: Texte anonymisé

    Example:
        >>> text = "Jan Kowalski, email: jan@example.com"
        >>> results = analyzer.analyze(text, ...)
        >>> anonymized = anonymize_text(text, results, config)
        >>> print(anonymized)
        [PERSONNE], email: [EMAIL]
    """
    if not analyzer_results:
        logger.debug("Aucune entité à anonymiser n’a été détectée.")
        return text

    # Créer le moteur d’anonymisation
    anonymizer = AnonymizerEngine()

    # Associer les entités aux opérateurs (masques)
    operators = {}
    for entity_name, entity_config in config['entities'].items():
        mask = entity_config.get('mask', f"[{entity_name}]")
        operators[entity_name] = OperatorConfig("replace", {"new_value": mask})

    # Consigner les entités détectées (sans enregistrer les valeurs personnelles)
    entity_counts = {}
    for result in analyzer_results:
        entity_counts[result.entity_type] = entity_counts.get(result.entity_type, 0) + 1

    logger.info(f"Entités détectées : {entity_counts}")

    # Effectuer l’anonymisation
    anonymized_result = anonymizer.anonymize(
        text=text,
        analyzer_results=analyzer_results,
        operators=operators
    )

    logger.debug(f"Anonymisation terminée. Longueur du texte : {len(text)} -> {len(anonymized_result.text)}")

    return anonymized_result.text


def prepare_anonymization_report(
    analyzer_results: List[RecognizerResult],
    config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Prépare un rapport sur les entités détectées (sans leurs valeurs personnelles).

    Args:
        analyzer_results: Liste de résultats de Presidio Analyzer
        config: Dictionnaire de configuration

    Returns:
        dict: Rapport contenant les statistiques des entités détectées
    """
    if not analyzer_results:
        return {"total_detections": 0, "entities": {}}

    # Compter les détections par type
    entity_stats = {}
    for result in analyzer_results:
        entity_type = result.entity_type

        if entity_type not in entity_stats:
            entity_stats[entity_type] = {
                "count": 0,
                "mask": config['entities'].get(entity_type, {}).get('mask', f"[{entity_type}]"),
                "avg_score": 0.0,
                "scores": []
            }

        entity_stats[entity_type]["count"] += 1
        entity_stats[entity_type]["scores"].append(result.score)

    # Calculer le score moyen
    for entity_type in entity_stats:
        scores = entity_stats[entity_type]["scores"]
        entity_stats[entity_type]["avg_score"] = sum(scores) / len(scores)
        del entity_stats[entity_type]["scores"]  # Retirer les scores détaillés du rapport

    total_detections = sum(stats["count"] for stats in entity_stats.values())

    report = {
        "total_detections": total_detections,
        "entities": entity_stats,
        "threshold_used": config.get('threshold', 0.35)
    }

    logger.info(f"Rapport généré : {total_detections} entités détectées")

    return report
