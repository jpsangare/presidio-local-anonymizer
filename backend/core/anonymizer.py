"""
Module d’anonymisation des données personnelles utilisant Presidio AnonymizerEngine.
Remplace les entités détectées par les masques définis dans la configuration.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple

from presidio_analyzer import RecognizerResult
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

logger = logging.getLogger("app.anonymizer")


# Mapping: mask label (e.g. "[PERSONNE]") → human-readable prefix for numbering
_ENTITY_LABEL_MAP: Dict[str, str] = {}


def _label_for(entity_type: str, config: Dict[str, Any]) -> str:
    """Return the mask string for an entity type, e.g. ‘[PERSONNE]’."""
    return config[‘entities’].get(entity_type, {}).get(‘mask’, f’[{entity_type}]’)


def anonymize_text(
    text: str,
    analyzer_results: List[RecognizerResult],
    config: Dict[str, Any],
    mapping: Optional[Dict[str, str]] = None,
    ts: Optional[str] = None,
) -> str:
    """
    Anonymise le texte en remplaçant les entités détectées par les masques correspondants.

    Args:
        text: Texte à anonymiser
        analyzer_results: Liste de résultats de Presidio Analyzer
        config: Dictionnaire de configuration des masques par entité

    Returns:
        str: Texte anonymisé

    Args:
        text: Texte à anonymiser
        analyzer_results: Liste de résultats de Presidio Analyzer
        config: Dictionnaire de configuration des masques par entité
        mapping: Si fourni, sera rempli avec {token_numéroté: valeur_originale}
                 pour permettre la désanonymisation ultérieure.

    Returns:
        str: Texte anonymisé avec tokens numérotés si mapping fourni,
             sinon masques génériques.
    """
    if not analyzer_results:
        logger.debug("Aucune entité à anonymiser n’a été détectée.")
        return text

    if mapping is not None:
        return _anonymize_with_mapping(text, analyzer_results, config, mapping, ts)

    # Mode simple sans mapping (rétrocompatible)
    anonymizer = AnonymizerEngine()
    operators = {}
    for entity_name, entity_config in config[‘entities’].items():
        mask = entity_config.get(‘mask’, f"[{entity_name}]")
        operators[entity_name] = OperatorConfig("replace", {"new_value": mask})

    entity_counts = {}
    for result in analyzer_results:
        entity_counts[result.entity_type] = entity_counts.get(result.entity_type, 0) + 1
    logger.info(f"Entités détectées : {entity_counts}")

    anonymized_result = anonymizer.anonymize(
        text=text,
        analyzer_results=analyzer_results,
        operators=operators
    )
    logger.debug(f"Anonymisation terminée. Longueur du texte : {len(text)} -> {len(anonymized_result.text)}")
    return anonymized_result.text


def _anonymize_with_mapping(
    text: str,
    analyzer_results: List[RecognizerResult],
    config: Dict[str, Any],
    mapping: Dict[str, str],
    ts: Optional[str] = None,
) -> str:
    """Anonymise avec tokens horodatés [TYPE_N_TS] et remplit la table de correspondance."""
    sorted_results = sorted(analyzer_results, key=lambda r: r.start, reverse=True)

    counters: Dict[str, int] = {}
    value_to_token: Dict[str, str] = {}

    result_text = text
    for result in sorted_results:
        original_value = text[result.start:result.end]
        if original_value in value_to_token:
            token = value_to_token[original_value]
        else:
            label = _label_for(result.entity_type, config)
            counter_key = label.strip(‘[]’)
            counters[counter_key] = counters.get(counter_key, 0) + 1
            if ts:
                token = f"[{counter_key}_{counters[counter_key]}_{ts}]"
            else:
                token = f"[{counter_key}_{counters[counter_key]}]"
            value_to_token[original_value] = token
            mapping[token] = original_value

        result_text = result_text[:result.start] + token + result_text[result.end:]

    logger.info(f"Anonymisation avec mapping : {len(mapping)} tokens créés (ts={ts})")
    return result_text


def deanonymize_text(anonymized_text: str, mapping: Dict[str, str]) -> str:
    """Remplace les tokens numérotés par leurs valeurs originales."""
    result = anonymized_text
    # Sort by token length desc to avoid partial replacements
    for token, original in sorted(mapping.items(), key=lambda x: -len(x[0])):
        result = result.replace(token, original)
    return result


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
