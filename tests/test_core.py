import pytest

from rageval.core import Case, evaluate, mrr, recall_at_k


def test_recall_at_k_full_hit():
    assert recall_at_k(["a"], ["a", "b"], 5) == 1.0


def test_recall_at_k_partial():
    assert recall_at_k(["a", "b"], ["a", "x"], 5) == 0.5


def test_recall_respects_k():
    assert recall_at_k(["c"], ["a", "b", "c"], 2) == 0.0
    assert recall_at_k(["c"], ["a", "b", "c"], 3) == 1.0


def test_recall_requires_expected():
    with pytest.raises(ValueError):
        recall_at_k([], ["a"], 5)


def test_mrr_first_position():
    assert mrr(["a"], ["a", "b"]) == 1.0


def test_mrr_third_position():
    assert mrr(["c"], ["a", "b", "c"]) == pytest.approx(1 / 3)


def test_mrr_no_hit():
    assert mrr(["z"], ["a", "b"]) == 0.0


def test_evaluate_aggregates():
    cases = [Case("q1", ["d1"]), Case("q2", ["d2"]), Case("q3", ["d3"])]
    index = {"q1": ["d1"], "q2": ["x", "d2"], "q3": ["y"]}
    r = evaluate(cases, lambda q: index[q], k=5)
    assert r.total == 3
    assert r.recall == pytest.approx((1 + 1 + 0) / 3)
    assert r.hit_rate == pytest.approx(2 / 3)
    assert r.mrr == pytest.approx((1 + 0.5 + 0) / 3)
    assert len(r.misses) == 1


def test_evaluate_rejects_empty():
    with pytest.raises(ValueError):
        evaluate([], lambda q: [])
