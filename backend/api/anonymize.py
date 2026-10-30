"""
Anonymization endpoint - core functionality
"""

from flask import Blueprint, jsonify, request
import logging
import json
import os
import re
import time
import threading
from datetime import datetime, timedelta
from collections import deque
from core.analyzer import build_analyzer, get_supported_entities, SUPPORTED_LANGUAGES
from core.anonymizer import anonymize_text, deanonymize_text
from core import crypto

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
    encrypted = {token: crypto.encrypt(value) for token, value in mapping.items()}
    with _MAPPINGS_LOCK:
        data = _load_mappings()
        data = _purge_old_mappings(data)
        data[ts] = encrypted
        _save_mappings(data)


# Espaces de travail : un coffre durable par projet (Projet ChatGPT/Claude, Notebook…).
# Leur identifiant a le format d'un horodatage, si bien que leurs jetons
# [TYPE_N_ID] restent reconnus et désanonymisés comme ceux d'une session.
_WORKSPACES_FILE = os.path.join(_DATA_DIR, 'workspaces.json')


def _load_workspaces() -> dict:
    try:
        with open(_WORKSPACES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _save_workspaces(data: dict):
    os.makedirs(_DATA_DIR, exist_ok=True)
    with open(_WORKSPACES_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _decrypt_mapping(stored: dict) -> dict:
    mapping = {}
    for token, value in stored.items():
        plain = crypto.decrypt(value) if crypto.is_encrypted(value) else value
        if plain is None:
            logger.warning("Valeur indéchiffrable pour %s (clé de chiffrement perdue ?)", token)
            continue
        mapping[token] = plain
    return mapping


def _get_mapping(ts: str) -> dict:
    with _MAPPINGS_LOCK:
        workspace = _load_workspaces().get(ts)
        stored = workspace['mapping'] if workspace else _load_mappings().get(ts, {})
    return _decrypt_mapping(stored)


def _encrypt_legacy_mappings():
    """Chiffre une fois les valeurs encore stockées en clair (fichiers antérieurs)."""
    with _MAPPINGS_LOCK:
        data = _load_mappings()
        changed = 0
        for session in data.values():
            for token, value in session.items():
                if not crypto.is_encrypted(value):
                    session[token] = crypto.encrypt(value)
                    changed += 1
        if changed:
            _save_mappings(data)
            logger.info("%d valeur(s) en clair chiffrée(s) dans %s", changed, _MAPPINGS_FILE)


_TS_FORMAT = "%y_%m_%d_%H_%M_%S"


def _make_ts() -> str:
    """
    Horodatage YY_MM_DD_HH_MM_SS libre : une seconde déjà prise par une session
    ou un espace de travail décale au suivant, pour qu'aucun mapping n'en écrase un autre.
    """
    with _MAPPINGS_LOCK:
        taken = _load_mappings().keys() | _load_workspaces().keys()
    moment = datetime.now()
    while moment.strftime(_TS_FORMAT) in taken:
        moment += timedelta(seconds=1)
    return moment.strftime(_TS_FORMAT)


def _merge_results(results):
    kept = []
    ordered = sorted(results, key=lambda r: (r.entity_type in NER_ENTITIES, -r.score, r.start - r.end))
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

_encrypt_legacy_mappings()

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
    workspace_id = data.get('workspace_id')

    # Validate text
    if not text or not text.strip():
        return jsonify({
            'error': 'Invalid request',
            'message': 'Text cannot be empty'
        }), 400

    if workspace_id is not None and workspace_id not in _load_workspaces():
        return _unknown_workspace(workspace_id)

    try:
        response = anonymize_document(text, entities_filter, data.get('language'), workspace_id)
    except UnknownWorkspace:
        return _unknown_workspace(workspace_id)
    except Exception as e:
        logger.error(f"Error during anonymization: {e}", exc_info=True)
        return jsonify({
            'error': 'Anonymization failed',
            'message': str(e)
        }), 500
    return jsonify(response), 200


class UnknownWorkspace(KeyError):
    pass


def _unknown_workspace(workspace_id):
    return jsonify({'error': 'Not found', 'message': f'Espace de travail inconnu : {workspace_id}'}), 404


def service_error():
    """Raison de l'indisponibilité de l'analyseur, ou None s'il est prêt."""
    if analyzer is None or config is None:
        return analyzer_error or 'Presidio Analyzer failed to initialize'
    return None


def anonymize_document(text, entities_filter=None, language=None, workspace_id=None) -> dict:
    """
    Analyse et anonymise un texte, enregistre son mapping (session horodatée ou
    coffre de l'espace de travail) et renvoie la réponse de /anonymize.
    Lève UnknownWorkspace si l'espace n'existe pas (ou plus).
    """
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
        results = _analyze_all_languages(text, entities_to_use, language, threshold)

    if workspace_id is not None:
        # Jetons stables : le coffre de l'espace est relu, complété puis réenregistré
        ts = workspace_id
        with _MAPPINGS_LOCK:
            workspaces = _load_workspaces()
            if ts not in workspaces:
                raise UnknownWorkspace(ts)
            stored = workspaces[ts]['mapping']
            mapping = _decrypt_mapping(stored)
            anonymized_text = anonymize_text(text, results, config, mapping if results else None, ts)
            new_tokens = mapping.keys() - stored.keys()
            if new_tokens:
                stored.update({token: crypto.encrypt(mapping[token]) for token in new_tokens})
                _save_workspaces(workspaces)
    else:
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
        'session_id': ts if results else None,  # rétrocompat extension
        'ts': ts if results else None,
        'workspace_id': workspace_id,
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

    return response

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


_TOKEN_SUFFIX = re.compile(r'_\d+(?:_\d{2}){6}$')


@anonymize_bp.route('/sessions', methods=['GET'])
def list_sessions():
    """Liste les sessions récentes (horodatage, nombre et types d'entités, sans les valeurs)."""
    limit = min(request.args.get('limit', 20, type=int), 100)
    with _MAPPINGS_LOCK:
        data = _load_mappings()
    sessions = []
    for ts in sorted(data, reverse=True)[:limit]:
        types = sorted({_TOKEN_SUFFIX.sub('', token.strip('[]')) for token in data[ts]})
        sessions.append({'ts': ts, 'count': len(data[ts]), 'types': types})
    return jsonify({'sessions': sessions}), 200


def _workspace_summary(workspace_id: str, workspace: dict) -> dict:
    types = sorted({_TOKEN_SUFFIX.sub('', token.strip('[]')) for token in workspace['mapping']})
    return {
        'id': workspace_id,
        'name': workspace['name'],
        'created': workspace['created'],
        'count': len(workspace['mapping']),
        'types': types,
    }


@anonymize_bp.route('/workspaces', methods=['GET'])
def list_workspaces():
    """Liste les espaces de travail (sans les valeurs d'origine)."""
    with _MAPPINGS_LOCK:
        data = _load_workspaces()
    workspaces = [_workspace_summary(wid, ws) for wid, ws in sorted(data.items(), reverse=True)]
    return jsonify({'workspaces': workspaces}), 200


@anonymize_bp.route('/workspaces', methods=['POST'])
def create_workspace():
    """Crée un espace de travail : ses jetons restent identiques d'un texte à l'autre."""
    data = request.get_json(silent=True) or {}
    name = str(data.get('name', '')).strip()
    if not name:
        return jsonify({'error': 'Invalid request', 'message': 'Champ requis : name'}), 400

    workspace_id = _make_ts()
    workspace = {'name': name[:100], 'created': datetime.now().isoformat(timespec='seconds'), 'mapping': {}}
    with _MAPPINGS_LOCK:
        workspaces = _load_workspaces()
        workspaces[workspace_id] = workspace
        _save_workspaces(workspaces)
    return jsonify(_workspace_summary(workspace_id, workspace)), 201


@anonymize_bp.route('/workspaces/<workspace_id>', methods=['DELETE'])
def delete_workspace(workspace_id):
    """Supprime un espace et son coffre : ses jetons ne pourront plus être désanonymisés."""
    with _MAPPINGS_LOCK:
        workspaces = _load_workspaces()
        if workspaces.pop(workspace_id, None) is None:
            return jsonify({'error': 'Not found', 'message': f'Espace de travail inconnu : {workspace_id}'}), 404
        _save_workspaces(workspaces)
    return jsonify({'message': 'Espace de travail supprimé'}), 200


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
