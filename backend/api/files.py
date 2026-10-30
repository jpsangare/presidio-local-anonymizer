"""
Anonymisation de fichiers à déposer dans le RAG d'un LLM cloud
(Projets ChatGPT / Claude, NotebookLM, Gems…).

Les fichiers texte sont anonymisés tels quels ; les documents (PDF, Word,
PowerPoint, Excel, HTML, images) sont d'abord convertis en Markdown par Docling,
chargé au premier document seulement. Le fichier produit ne garde ni la mise en
forme ni les métadonnées de l'original.
"""

import base64
import binascii
import io
import logging
from functools import lru_cache
from pathlib import PurePath

from flask import Blueprint, jsonify, request

from api import anonymize as engine

logger = logging.getLogger(__name__)
files_bp = Blueprint('files', __name__)

MAX_FILE_BYTES = 20 * 1024 * 1024

TEXT_EXTENSIONS = {'.txt', '.md', '.csv', '.tsv', '.json', '.log'}
DOCLING_EXTENSIONS = {
    '.pdf', '.docx', '.pptx', '.xlsx', '.html', '.htm',
    '.png', '.jpg', '.jpeg', '.tif', '.tiff', '.bmp',
}
IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.tif', '.tiff', '.bmp'}


def _decode_text(data: bytes) -> str:
    try:
        return data.decode('utf-8-sig')
    except UnicodeDecodeError:
        return data.decode('cp1252', errors='replace')


@lru_cache(maxsize=2)
def _converter(ocr: bool):
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import PdfPipelineOptions
    from docling.document_converter import DocumentConverter, PdfFormatOption

    options = PdfPipelineOptions(do_ocr=ocr)
    return DocumentConverter(format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=options)})


def _to_markdown(filename: str, data: bytes) -> str:
    """Conversion Docling ; l'OCR (lent) n'est lancé que pour une image ou un PDF sans texte."""
    from docling.datamodel.base_models import DocumentStream

    def convert(ocr):
        stream = DocumentStream(name=filename, stream=io.BytesIO(data))
        return _converter(ocr).convert(stream).document.export_to_markdown()

    suffix = PurePath(filename).suffix.lower()
    markdown = convert(ocr=suffix in IMAGE_EXTENSIONS)
    if suffix == '.pdf' and not markdown.strip():
        logger.info("PDF sans texte extractible : nouvelle conversion avec OCR")
        markdown = convert(ocr=True)
    return markdown


def docling_available() -> bool:
    import importlib.util
    return importlib.util.find_spec('docling') is not None


@files_bp.route('/files/formats', methods=['GET'])
def formats():
    """Extensions acceptées (les documents exigent Docling)."""
    has_docling = docling_available()
    accepted = TEXT_EXTENSIONS | (DOCLING_EXTENSIONS if has_docling else set())
    return jsonify({'extensions': sorted(accepted), 'docling': has_docling}), 200


@files_bp.route('/files/anonymize', methods=['POST'])
def anonymize_file():
    """
    Request JSON:
        {"filename": "rapport.pdf", "content": "<base64>", "workspace_id": "26_10_30_14_05_12"}

    Response JSON : celle de /anonymize, plus
        {"output_filename": "document-26_10_30_14_05_12-anonymise.md", "source_format": "pdf"}
    """
    error = engine.service_error()
    if error:
        return jsonify({'error': 'Service not ready', 'message': error}), 503

    data = request.get_json(silent=True) or {}
    filename = PurePath(str(data.get('filename', ''))).name
    suffix = PurePath(filename).suffix.lower()
    workspace_id = data.get('workspace_id')

    if suffix not in TEXT_EXTENSIONS | DOCLING_EXTENSIONS:
        return jsonify({'error': 'Unsupported format', 'message': f'Format non pris en charge : {suffix or filename}'}), 415
    if suffix in DOCLING_EXTENSIONS and not docling_available():
        return jsonify({
            'error': 'Unsupported format',
            'message': 'Les documents PDF, Office et images exigent Docling : pip install docling'
        }), 415
    if len(data.get('content') or '') > MAX_FILE_BYTES * 4 // 3 + 4:
        return jsonify({'error': 'File too large', 'message': 'Fichier limité à 20 Mo'}), 413
    try:
        raw = base64.b64decode(data.get('content') or '', validate=True)
    except (binascii.Error, ValueError):
        return jsonify({'error': 'Invalid request', 'message': 'Contenu base64 invalide'}), 400
    if not raw:
        return jsonify({'error': 'Invalid request', 'message': 'Fichier vide'}), 400

    try:
        if suffix in TEXT_EXTENSIONS:
            text, extension = _decode_text(raw), suffix
        else:
            text, extension = _to_markdown(filename, raw), '.md'
    except Exception as e:
        logger.error("Conversion impossible de %s : %s", suffix, e, exc_info=True)
        return jsonify({'error': 'Conversion failed', 'message': f'Conversion impossible : {e}'}), 422
    if not text.strip():
        return jsonify({'error': 'Conversion failed', 'message': 'Aucun texte trouvé dans le fichier'}), 422

    try:
        response = engine.anonymize_document(text, workspace_id=workspace_id)
    except engine.UnknownWorkspace:
        return jsonify({'error': 'Not found', 'message': f'Espace de travail inconnu : {workspace_id}'}), 404
    except Exception as e:
        logger.error("Erreur d'anonymisation du fichier : %s", e, exc_info=True)
        return jsonify({'error': 'Anonymization failed', 'message': str(e)}), 500

    # Le nom d'origine (« CV_Aminata_Kouassi.pdf ») peut lui-même être une donnée personnelle
    label = response['ts'] or workspace_id or 'texte'
    response['output_filename'] = f'document-{label}-anonymise{extension}'
    response['source_format'] = suffix.lstrip('.')
    return jsonify(response), 200
