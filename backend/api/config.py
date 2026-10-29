"""
Configuration endpoint - manage anonymization settings
"""

from flask import Blueprint, jsonify, request
import logging
import yaml
from pathlib import Path

logger = logging.getLogger(__name__)
config_bp = Blueprint('config', __name__)

# Path to config file (source unique définie dans core.analyzer)
from core.analyzer import CONFIG_PATH

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
                import re as _re
                for entity_name, entity_cfg in new_config['entities'].items():
                    if not _re.fullmatch(r'[A-Z][A-Z0-9_]*', entity_name):
                        return jsonify({
                            'error': 'Invalid entity name',
                            'message': f"Nom d’entité invalide : {entity_name} "
                                       "(majuscules, chiffres et _ uniquement)"
                        }), 400
                    if not isinstance(entity_cfg, dict):
                        return jsonify({
                            'error': 'Invalid entity',
                            'message': f"Entité invalide : {entity_name}"
                        }), 400
                    for pattern in entity_cfg.get('patterns', []):
                        try:
                            _re.compile(pattern['regex'])
                        except (_re.error, KeyError, TypeError) as e:
                            return jsonify({
                                'error': 'Invalid regex',
                                'message': f"Motif invalide pour {entity_name} : {e}"
                            }), 400
                current_config['entities'].update(new_config['entities'])

        # Save updated config
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            yaml.dump(current_config, f, allow_unicode=True, default_flow_style=False)

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
