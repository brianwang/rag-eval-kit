"""核心评测逻辑：纯函数，无外部依赖，便于测试。"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Iterable, Sequence


@dataclass(frozen=True)
class Case:
    """一条评测用例。"""
    question: str
    expected_ids: Sequence[str]


@dataclass
class EvalResult:
    total: int
    recall: float
    mrr: float
    hit_rate: float
    misses: list[tuple[Case, list[str]]] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "total": self.total,
            "recall@k": round(self.recall, 4),
            "mrr": round(self.mrr, 4),
            "hit_rate": round(self.hit_rate, 4),
            "misses": [{"question": c.question, "expected": list(c.expected_ids),
                        "got": got} for c, got in self.misses],
        }


def recall_at_k(expected: Iterable[str], retrieved: Sequence[str], k: int) -> float:
    """命中的期望文档数 / 期望文档总数。"""
    exp = set(expected)
    if not exp:
        raise ValueError("expected_ids 不能为空")
    top = set(retrieved[:k])
    return len(exp & top) / len(exp)


def mrr(expected: Iterable[str], retrieved: Sequence[str]) -> float:
    """第一个命中位置的倒数；没命中返回 0。"""
    exp = set(expected)
    for i, doc_id in enumerate(retrieved, start=1):
        if doc_id in exp:
            return 1.0 / i
    return 0.0


def evaluate(cases: Sequence[Case], retrieve: Callable[[str], Sequence[str]], k: int = 5) -> EvalResult:
    """跑一遍评测。

    retrieve(question) -> 按相关度排序的 doc_id 列表（越靠前越相关）
    """
    if not cases:
        raise ValueError("cases 不能为空")
    recalls, rr, hits = [], [], []
    misses = []
    for case in cases:
        got = list(retrieve(case.question))[:k]
        r = recall_at_k(case.expected_ids, got, k)
        m = mrr(case.expected_ids, got)
        recalls.append(r)
        rr.append(m)
        hits.append(1.0 if r > 0 else 0.0)
        if r == 0:
            misses.append((case, got))
    n = len(cases)
    return EvalResult(
        total=n,
        recall=sum(recalls) / n,
        mrr=sum(rr) / n,
        hit_rate=sum(hits) / n,
        misses=misses,
    )
