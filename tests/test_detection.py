"""Évaluation de la détection sur un corpus annoté (précision / rappel).

Les cas marqués "known_issue" documentent des limites connues : ils sont suivis
(xfail) mais exclus des seuils. Si l’un d’eux se met à passer, le test échoue
pour rappeler de retirer l’annotation.
"""

import json
from pathlib import Path

import pytest

import conftest

CORPUS = json.loads((Path(__file__).parent / "data" / "corpus.json").read_text(encoding="utf-8"))

MIN_PRECISION = 0.90
MIN_RECALL = 0.90

pytestmark = pytest.mark.models


def _detect(client, text):
    body = client.post("/api/anonymize", json={"text": text}).get_json()
    return {(e["type"], e["text"]) for e in body["entities_found"]}


@pytest.mark.parametrize("case", CORPUS, ids=[c["id"] for c in CORPUS])
def test_corpus_case(client, models_ready, case):
    expected = {tuple(e) for e in case["expected"]}
    found = _detect(client, case["text"])

    if "known_issue" in case:
        if found == expected:
            pytest.fail(f"Ce cas passe désormais : retirez « known_issue » ({case['id']})")
        pytest.xfail(case["known_issue"])

    assert found == expected, f"manquants={expected - found} en trop={found - expected}"


def test_precision_and_recall_thresholds(client, models_ready):
    true_positives = false_positives = false_negatives = 0

    for case in CORPUS:
        if "known_issue" in case:
            continue
        expected = {tuple(e) for e in case["expected"]}
        found = _detect(client, case["text"])
        true_positives += len(found & expected)
        false_positives += len(found - expected)
        false_negatives += len(expected - found)

    precision = true_positives / (true_positives + false_positives) if true_positives + false_positives else 1.0
    recall = true_positives / (true_positives + false_negatives) if true_positives + false_negatives else 1.0
    conftest.METRICS.update(precision=precision, recall=recall, cases=len(CORPUS))

    assert precision >= MIN_PRECISION, f"précision {precision:.2f} < {MIN_PRECISION}"
    assert recall >= MIN_RECALL, f"rappel {recall:.2f} < {MIN_RECALL}"
