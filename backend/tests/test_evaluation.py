from copy import deepcopy

from evaluation.dataset import CASES
from evaluation.metrics import measure, score
from evaluation.run import baseline


def oracle(cases):
    return {case["id"]: {"skills": case["expected"], "match_score": score(case["expected"])} for case in cases}


def test_perfect_predictions_score_one():
    report = measure(CASES, oracle(CASES))
    assert report["macro_f1"] == 1
    assert report["requirement_recall"] == 1
    assert report["score_mae_valid_cases"] == 0


def test_missing_and_failed_cases_count_against_recall():
    report = measure(CASES, {})
    assert report["requirement_recall"] == 0
    assert report["label_accuracy_all_requirements"] == 0
    assert report["valid_response_rate"] == 0
    assert report["score_mae_valid_cases"] is None


def test_extra_requirement_reduces_precision():
    predicted = deepcopy(oracle(CASES))
    predicted[CASES[0]["id"]]["skills"].append({"requirement_quote": "invented", "status": "strong", "required": False})
    assert measure(CASES, predicted)["requirement_precision"] < 1


def test_keyword_baseline_exposes_semantic_and_negation_failures():
    predictions = {case["id"]: baseline(case) for case in CASES}
    report = measure(CASES, predictions)
    assert report["requirement_recall"] == 1  # oracle extraction, by design
    assert 0 < report["macro_f1"] < 1
    assert predictions["negation"]["skills"][0]["status"] == "strong"
    assert predictions["semantic-testing"]["skills"][0]["status"] == "missing"
