"""
Health check endpoint
"""

from flask import Blueprint, jsonify
import logging

logger = logging.getLogger(__name__)
health_bp = Blueprint('health', __name__)

@health_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint - verify service is running

    Returns:
        JSON with service status
    """
    from api import anonymize

    return jsonify({
        'status': 'healthy',
        'service': 'masqueia',
        'version': '1.0.0',
        'analyzer_ready': anonymize.analyzer is not None,
        'analyzer_error': anonymize.analyzer_error
    }), 200
