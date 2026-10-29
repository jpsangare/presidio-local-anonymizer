"""
Test de motifs regex en direct — utilisé par le panneau « Ajouter une donnée »
du tableau de bord pour valider une expression avant de l’enregistrer.
"""

import logging
import re

from flask import Blueprint, jsonify, request
from presidio_analyzer import Pattern

from core.analyzer import ValidatedPatternRecognizer
from core.validators import VALIDATORS

logger = logging.getLogger(__name__)
patterns_bp = Blueprint('patterns', __name__)


@patterns_bp.route('/test-pattern', methods=['POST'])
def test_pattern():
    """
    Teste un motif regex sur un texte d’exemple, sans rien enregistrer.

    Request JSON:
        {"regex": "...", "text": "...", "score": 0.5,
         "context": ["mot1"], "validator": "luhn"}

    Response JSON:
        {"matches": [{"text": "...", "start": 0, "end": 5, "score": 1.0}]}
    """
    data = request.get_json()

    if not data or 'regex' not in data or 'text' not in data:
        return jsonify({
            'error': 'Invalid request',
            'message': 'Missing "regex" or "text" field'
        }), 400

    try:
        re.compile(data['regex'])
    except re.error as e:
        return jsonify({
            'error': 'Invalid regex',
            'message': f"Expression régulière invalide : {e}"
        }), 400

    score = data.get('score', 0.5)
    if not isinstance(score, (int, float)) or not 0 < score <= 1:
        return jsonify({
            'error': 'Invalid score',
            'message': 'Le score doit être un nombre entre 0 et 1'
        }), 400

    validator_name = data.get('validator')
    validator = VALIDATORS.get(validator_name) if validator_name else None
    if validator_name and validator is None:
        return jsonify({
            'error': 'Invalid validator',
            'message': f"Validateur inconnu : {validator_name}. "
                       f"Disponibles : {', '.join(VALIDATORS)}"
        }), 400

    context = data.get('context') or None
    if context is not None and not isinstance(context, list):
        return jsonify({
            'error': 'Invalid context',
            'message': 'Le contexte doit être une liste de mots'
        }), 400

    recognizer = ValidatedPatternRecognizer(
        supported_entity="TEST_ENTITY",
        patterns=[Pattern(name="test", regex=data['regex'], score=float(score))],
        supported_language="fr",
        context=context,
        validator=validator
    )

    try:
        results = recognizer.analyze(data['text'], ["TEST_ENTITY"])
    except Exception as e:
        logger.error(f"Error testing pattern: {e}")
        return jsonify({
            'error': 'Analysis failed',
            'message': str(e)
        }), 500

    text = data['text']
    matches = [
        {
            'text': text[r.start:r.end],
            'start': r.start,
            'end': r.end,
            'score': round(r.score, 2)
        }
        for r in results
    ]

    return jsonify({'matches': matches}), 200
