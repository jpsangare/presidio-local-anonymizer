"""
Anonymization endpoint - core functionality
"""

from flask import Blueprint, jsonify, request
import logging
import json
import os
import time
import threading
from datetime import datetime, timedelta
from collections import deque
from core.analyzer import build_analyzer, get_supported_entities, SUPPORTED_LANGUAGES
from core.anonymizer import anonymize_text, deanonymize_text

logger = logging.getLogger(__name__)
anonymize_bp = Blueprint('anonymize', __name__)

NER_ENTITIES = {"PERSON", "LOCATION", "ORGANIZATION"}

# Fichier de persistance des mappings (survit aux redémarrages)
_DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
_MAPPINGS_FILE = os.path.join(_DATA_DIR, 'mappings.json')
_MAPPINGS_LOCK = threading.Lock()
_RETENTION_DAYS = 30  # purge auto après 30 jours


def _load_mappings() -> dict:
    try:
        with open(_MAPPINGS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _save_mappings(data: dict):
    os.makedirs(_DATA_DIR, exist_ok=True)
    with open(_MAPPINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _purge_old_mappings(data: dict) -> dict:
    """Supprime les entrées de plus de _RETENTION_DAYS jours."""
    cutoff = datetime.now() - timedelta(days=_RETENTION_DAYS)
    to_delete = []
    for ts_key in data:
        try:
            # Format: YY_MM_DD_HH_MM_SS
            dt = datetime.strptime(ts_key, "%y_%m_%d_%H_%M_%S")
            if dt < cutoff:
                to_delete.append(ts_key)
        except ValueError:
            pass
    for k in to_delete:
        del data[k]
    return data


def _add_mapping(ts: str, mapping: dict):
    with _MAPPINGS_LOCK:
        data = _load_mappings()
        data = _purge_old_mappings(data)
        data[ts] = mapping
        _save_mappings(data)


def _get_mapping(ts: str) -> dict:
    with _MAPPINGS_LOCK:
        data = _load_mappings()
        return data.get(ts, {})


def _make_ts() -> str:
    """Génère un timestamp unique YY_MM_DD_HH_MM_SS (+ micro si collision)."""
    return datetime.now().strftime("%y_%m_%d_%H_%M_%S")


def _merge_results(results):
    kept = []
    ordered = sorted(results, key=lambda r: (r.entity_type in NER_ENTITIES, -r.score, r.start))
    for result in ordered:
        if all(result.end <= k.start or result.start >= k.end for k in kept):
            kept.append(result)
    return sorted(kept, key=lambda r: r.start)


def _analyze_all_languages(text, entities, requested_language=None, threshold=0.0):
    from core.language_detector import detect_language
    language = requested_language if requested_language in SUPPORTED_LANGUAGES else detect_language(text)
    languages = [language] if language else SUPPORTED_LANGUAGES
    results = []
    for language in languages:
        results.extend(analyzer.analyze(
            text=text, language=language, entities=entities, score_threshold=threshold
        ))
    return _merge_results(results)

# In-memory logs storage (max 100 entries)
anonymization_logs = deque(maxlen=100)

# Initialize analyzer once at startup (expensive operation)
try:
    analyzer, config = build_analyzer()
    logger.info("Presidio Analyzer initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Presidio Analyzer: {e}")
    analyzer = None
    config = None
    analyzer_error = str(e)
else:
    analyzer_error = None

@anonymize_bp.route('/anonymize', methods=['POST'])
def anonymize():
    """
    Anonymize text endpoint

    Request JSON:
        {
            "text": "Jan Kowalski, PESEL: 92010212345",
            "entities": ["PERSON", "PL_PESEL"]  # Optional, default: all
        }

    Response JSON:
        {
            "original_text": "Jan Kowalski, PESEL: 92010212345",
            "anonymized_text": "[PERSONNE], PESEL: [PESEL]",
            "entities_found": [
                {
                    "type": "PERSON",
                    "start": 0,
                    "end": 13,
                    "score": 0.95,
                    "text": "Jan Kowalski"
                },
                {
                    "type": "PL_PESEL",
                    "start": 22,
                    "end": 33,
                    "score": 0.9,
                    "text": "92010212345"
                }
            ],
            "stats": {
                "total_entities": 2,
                "processing_time_ms": 45
            }
        }
    """

    # Check if analyzer is initialized
    if analyzer is None or config is None:
        return jsonify({
            'error': 'Service not ready',
            'message': analyzer_error or 'Presidio Analyzer failed to initialize'
        }), 503

    # Get request data
    data = request.get_json()

    if not data or 'text' not in data:
        return jsonify({
            'error': 'Invalid request',
            'message': 'Missing "text" field in request body'
        }), 400

    text = data.get('text', '')
    entities_filter = data.get('entities', None)  # Optional filter

    # Validate text
    if not text or not text.strip():
        return jsonify({
            'error': 'Invalid request',
            'message': 'Text cannot be empty'
        }), 400

    try:
        import time
        start_time = time.time()

        # Get enabled entities from config
        enabled_entities = get_supported_entities(config)

        # If user provided entities filter, use intersection with enabled entities
        if entities_filter:
            entities_to_use = list(set(entities_filter) & set(enabled_entities))
        else:
            entities_to_use = enabled_entities

        logger.info(f"Analyzing with entities: {entities_to_use}")

        # An empty list would make Presidio analyze every entity, including disabled ones
        if not entities_to_use:
            results = []
        else:
            threshold = float(config.get('threshold', 0.35))
            results = _analyze_all_languages(text, entities_to_use, data.get('language'), threshold)

        # Générer timestamp horodatant tous les tokens de ce prompt
        ts = _make_ts()

        # Anonymize text — build reversible mapping with timestamped tokens
        mapping: dict = {}
        anonymized_text = anonymize_text(text, results, config, mapping if results else None, ts)

        # Persister le mapping dans le fichier JSON
        if mapping:
            _add_mapping(ts, mapping)

        # Calculate processing time
        processing_time = int((time.time() - start_time) * 1000)  # milliseconds

        # Build response with detailed entity information
        entities_found = []
        for result in results:
            entity_info = {
                'type': result.entity_type,
                'start': result.start,
                'end': result.end,
                'score': round(result.score, 2),
                'text': text[result.start:result.end]
            }
            entities_found.append(entity_info)

        response = {
            'original_text': text,
            'anonymized_text': anonymized_text,
            'entities_found': entities_found,
            'session_id': ts if mapping else None,  # rétrocompat extension
            'ts': ts if mapping else None,
            'stats': {
                'total_entities': len(results),
                'processing_time_ms': processing_time
            }
        }

        # Save to logs
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'original_text': text,
            'anonymized_text': anonymized_text,
            'entities_count': len(results),
            'entities_found': entities_found,
            'processing_time_ms': processing_time
        }
        anonymization_logs.append(log_entry)

        logger.info(f"Anonymized text: {len(results)} entities found, {processing_time}ms")

        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error during anonymization: {e}", exc_info=True)
        return jsonify({
            'error': 'Anonymization failed',
            'message': str(e)
        }), 500

@anonymize_bp.route('/logs', methods=['GET'])
def get_logs():
    """
    Get anonymization logs

    Query Parameters:
        limit: int - Maximum number of logs to return (default: 20, max: 100)

    Response JSON:
        {
            "logs": [
                {
                    "timestamp": "2025-11-15T12:30:45.123456",
                    "original_text": "Jan Kowalski, PESEL: 92010212345",
                    "anonymized_text": "[PERSONNE], PESEL: [PESEL]",
                    "entities_count": 2,
                    "entities_found": [...],
                    "processing_time_ms": 45
                },
                ...
            ],
            "total": 100
        }
    """
    try:
        # Get limit parameter
        limit = request.args.get('limit', 20, type=int)
        limit = min(limit, 100)  # Cap at 100

        # Get logs (most recent first)
        logs_list = list(anonymization_logs)
        logs_list.reverse()  # Most recent first

        # Apply limit
        limited_logs = logs_list[:limit]

        return jsonify({
            'logs': limited_logs,
            'total': len(anonymization_logs)
        }), 200

    except Exception as e:
        logger.error(f"Error retrieving logs: {e}", exc_info=True)
        return jsonify({
            'error': 'Failed to retrieve logs',
            'message': str(e)
        }), 500

@anonymize_bp.route('/logs/clear', methods=['POST'])
def clear_logs():
    """Clear all anonymization logs"""
    try:
        anonymization_logs.clear()
        logger.info("Anonymization logs cleared")
        return jsonify({
            'message': 'Logs cleared successfully'
        }), 200
    except Exception as e:
        logger.error(f"Error clearing logs: {e}", exc_info=True)
        return jsonify({
            'error': 'Failed to clear logs',
            'message': str(e)
        }), 500


@anonymize_bp.route('/deanonymize', methods=['POST'])
def deanonymize():
    """
    Désanonymise une réponse IA en remplaçant les tokens numérotés par les valeurs originales.

    Request JSON:
        {
            "session_id": "uuid-de-la-session",
            "text": "Réponse de l\\'IA contenant [PERSONNE_1] et [EMAIL_1]"
        }

    Response JSON:
        {
            "deanonymized_text": "Réponse avec Marie Dupont et marie@example.com",
            "replacements": 2
        }
    """
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'Champ requis : text'}), 400
    if 'session_id' not in data and 'ts' not in data:
        return jsonify({'error': 'Champ requis : ts (ou session_id)'}), 400

    ts = data.get('ts') or data.get('session_id')
    text = data['text']

    mapping = _get_mapping(ts)
    if not mapping:
        return jsonify({'error': f'Aucun mapping pour le timestamp {ts}. Session expirée ou texte sans entités.'}), 404

    deanonymized = deanonymize_text(text, mapping)
    replacements = sum(1 for token in mapping if token in text)

    return jsonify({
        'deanonymized_text': deanonymized,
        'replacements': replacements,
        'ts': ts,
    }), 200


@anonymize_bp.route('/reload', methods=['POST'])
def reload_analyzer():
    """Rebuild the analyzer so newly added entities take effect without restart."""
    global analyzer, config, analyzer_error

    try:
        logger.info("Rechargement de l'analyseur demandé...")
        analyzer, config = build_analyzer()
        analyzer_error = None
        logger.info("Analyseur rechargé avec succès")
        return jsonify({
            'status': 'success',
            'message': 'Analyseur rechargé, nouvelles entités actives'
        }), 200
    except Exception as e:
        analyzer = None
        config = None
        analyzer_error = str(e)
        logger.error(f"Échec du rechargement de l'analyseur : {e}", exc_info=True)
        return jsonify({
            'error': 'Reload failed',
            'message': analyzer_error
        }), 500
