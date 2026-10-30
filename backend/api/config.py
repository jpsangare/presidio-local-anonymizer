"""
Configuration endpoint - manage anonymization settings
"""

from flask import Blueprint, jsonify, request
import base64
import binascii
import logging
import re
import yaml

# Path to config file (source unique définie dans core.analyzer)
from core.analyzer import CONFIG_PATH
from core.config_excel import ExcelConfigError, from_xlsx, to_xlsx
from core.validators import VALIDATORS

logger = logging.getLogger(__name__)
config_bp = Blueprint('config', __name__)


def _load_config() -> dict:
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def _save_config(config: dict):
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, allow_unicode=True, default_flow_style=False)


def _invalid_entities(entities: dict):
    """(erreur, message) pour la première entité invalide, sinon None."""
    for entity_name, entity_cfg in entities.items():
        if not re.fullmatch(r'[A-Z][A-Z0-9_]*', entity_name):
            return 'Invalid entity name', (f"Nom d'entité invalide : {entity_name} "
                                           "(majuscules, chiffres et _ uniquement)")
        if not isinstance(entity_cfg, dict):
            return 'Invalid entity', f"Entité invalide : {entity_name}"
        validator = entity_cfg.get('validator')
        if validator and validator not in VALIDATORS:
            return 'Invalid validator', (f"Validateur inconnu pour {entity_name} : {validator} "
                                         f"(valeurs possibles : {', '.join(VALIDATORS)})")
        for pattern in entity_cfg.get('patterns', []):
            try:
                re.compile(pattern['regex'])
            except (re.error, KeyError, TypeError) as e:
                return 'Invalid regex', f"Motif invalide pour {entity_name} : {e}"
    return None

@config_bp.route('/config', methods=['GET'])
def get_config():
    """
    Get current configuration

    Response JSON:
        {
            "language": "fr",
            "threshold": 0.35,
            "entities": [{"name": "EMAIL_ADDRESS", "enabled": true}, ...]
        }
    """
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        # Convert entities dict to array format for frontend
        entities_array = []
        for name, settings in config.get('entities', {}).items():
            entities_array.append({
                'name': name,
                'enabled': settings.get('enabled', True),
                'description': settings.get('description', ''),
                'mask': settings.get('mask', f'[{name}]')
            })

        response = {
            'language': config.get('language', 'fr'),
            'threshold': config.get('threshold', 0.35),
            'entities': entities_array
        }

        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error loading config: {e}")
        return jsonify({
            'error': 'Failed to load configuration',
            'message': str(e)
        }), 500

@config_bp.route('/config', methods=['POST'])
def update_config():
    """
    Update configuration

    Request JSON:
        {
            "threshold": 0.5,
            "entities": {...}
        }

    Response JSON:
        {
            "status": "success",
            "message": "Configuration updated"
        }
    """
    try:
        # Get new config from request
        new_config = request.get_json()

        if not new_config:
            return jsonify({
                'error': 'Invalid request',
                'message': 'Missing configuration data'
            }), 400

        # Load current config
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            current_config = yaml.safe_load(f)

        # Update config (merge)
        if 'threshold' in new_config:
            current_config['threshold'] = new_config['threshold']

        if 'entities' in new_config:
            # Handle array format from frontend: [{name: "EMAIL", enabled: true}, ...]
            if isinstance(new_config['entities'], list):
                for entity_update in new_config['entities']:
                    entity_name = entity_update.get('name')
                    if entity_name and entity_name in current_config['entities']:
                        current_config['entities'][entity_name]['enabled'] = entity_update.get('enabled', True)
            # Handle dict format: {EMAIL_ADDRESS: {...}, ...}
            else:
                invalid = _invalid_entities(new_config['entities'])
                if invalid:
                    return jsonify({'error': invalid[0], 'message': invalid[1]}), 400
                current_config['entities'].update(new_config['entities'])

        _save_config(current_config)

        logger.info("Configuration updated successfully")

        return jsonify({
            'status': 'success',
            'message': 'Configuration updated',
            'config': current_config
        }), 200

    except Exception as e:
        logger.error(f"Error updating config: {e}")
        return jsonify({
            'error': 'Failed to update configuration',
            'message': str(e)
        }), 500


@config_bp.route('/config/export', methods=['GET'])
def export_config():
    """Classeur Excel des entités et de leurs motifs (base64 : l'extension ne relaie que du JSON)."""
    try:
        content = to_xlsx(_load_config())
    except Exception as e:
        logger.error(f"Error exporting config: {e}", exc_info=True)
        return jsonify({'error': 'Export failed', 'message': str(e)}), 500
    return jsonify({
        'filename': 'masqueia-formules.xlsx',
        'content': base64.b64encode(content).decode(),
    }), 200


@config_bp.route('/config/import', methods=['POST'])
def import_config():
    """
    Importe un classeur exporté puis modifié.

    Les entités du classeur remplacent celles du même nom (motifs compris) ;
    les entités absentes du classeur sont conservées.
    """
    data = request.get_json(silent=True) or {}
    try:
        threshold, entities = from_xlsx(base64.b64decode(data.get('content') or '', validate=True))
    except (binascii.Error, ValueError) as e:
        message = str(e) if isinstance(e, ExcelConfigError) else 'Contenu base64 invalide'
        return jsonify({'error': 'Invalid file', 'message': message}), 400
    if not entities:
        return jsonify({'error': 'Invalid file', 'message': 'Aucune entité dans le classeur'}), 400

    invalid = _invalid_entities(entities)
    if invalid:
        return jsonify({'error': invalid[0], 'message': invalid[1]}), 400

    config = _load_config()
    added = [name for name in entities if name not in config['entities']]
    config['entities'].update(entities)
    if threshold is not None:
        config['threshold'] = threshold
    _save_config(config)

    logger.info("Configuration importée depuis Excel : %d entité(s), %d nouvelle(s)", len(entities), len(added))
    return jsonify({
        'status': 'success',
        'imported': len(entities),
        'added': added,
        'patterns': sum(len(e.get('patterns', [])) for e in entities.values()),
    }), 200
