"""rag-eval-kit: 最小可用的 RAG 检索评测工具。

给定「问题 + 应当被检索到的文档 id」，计算 recall@k、MRR、命中率，
并给出逐条失败原因。不依赖任何向量库——你只要提供检索函数。
"""
from .core import Case, EvalResult, evaluate, recall_at_k, mrr

__all__ = ["Case", "EvalResult", "evaluate", "recall_at_k", "mrr"]
