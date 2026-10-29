"""Tests de la fusion des résultats multilingues."""

from presidio_analyzer import RecognizerResult


def _r(entity, start, end, score):
    return RecognizerResult(entity_type=entity, start=start, end=end, score=score)


def test_empty(anonymize_module):
    assert anonymize_module._merge_results([]) == []


def test_non_overlapping_results_are_kept_and_sorted(anonymize_module):
    merged = anonymize_module._merge_results([_r("EMAIL_ADDRESS", 20, 30, 1.0), _r("PERSON", 0, 5, 0.85)])

    assert [r.entity_type for r in merged] == ["PERSON", "EMAIL_ADDRESS"]


def test_highest_score_wins_on_overlap(anonymize_module):
    merged = anonymize_module._merge_results([_r("URL", 0, 10, 0.5), _r("EMAIL_ADDRESS", 2, 12, 1.0)])

    assert [r.entity_type for r in merged] == ["EMAIL_ADDRESS"]


def test_structured_entity_beats_ner_on_overlap(anonymize_module):
    ner = _r("LOCATION", 0, 17, 0.85)
    nip = _r("PL_NIP", 4, 17, 0.8)

    merged = anonymize_module._merge_results([ner, nip])

    assert [r.entity_type for r in merged] == ["PL_NIP"]


def test_duplicate_detections_from_two_languages_are_collapsed(anonymize_module):
    merged = anonymize_module._merge_results([_r("PERSON", 0, 11, 0.85), _r("PERSON", 0, 11, 0.85)])

    assert len(merged) == 1
