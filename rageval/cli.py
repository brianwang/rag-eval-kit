"""命令行入口：对 HTTP 检索接口跑评测。

cases.jsonl 每行: {"question": "...", "expected_ids": ["doc-1", "doc-2"]}

用法:
  rageval cases.jsonl --endpoint http://localhost:8000/search --k 5
  rageval cases.jsonl --endpoint ... --ids-field doc_id --json
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request

from .core import Case, evaluate


def load_cases(path: str) -> list[Case]:
    cases = []
    with open(path, encoding="utf-8") as f:
        for lineno, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                cases.append(Case(obj["question"], obj["expected_ids"]))
            except Exception as exc:
                raise SystemExit(f"{path}:{lineno} 解析失败: {exc}") from exc
    return cases


def make_retriever(endpoint: str, ids_field: str, timeout: float):
    def retrieve(question: str) -> list[str]:
        req = urllib.request.Request(
            endpoint,
            data=json.dumps({"query": question}).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read())
        except urllib.error.URLError as exc:
            raise SystemExit(f"请求失败 {endpoint}: {exc}") from exc
        items = data.get("results", data if isinstance(data, list) else [])
        out = []
        for it in items:
            out.append(it.get(ids_field) if isinstance(it, dict) else str(it))
        return [x for x in out if x]

    return retrieve


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="rageval", description="RAG 检索评测")
    ap.add_argument("cases", help="cases.jsonl 路径")
    ap.add_argument("--endpoint", required=True, help="检索接口 URL（POST {query}）")
    ap.add_argument("--k", type=int, default=5)
    ap.add_argument("--ids-field", default="id", help="响应中放文档 id 的字段名")
    ap.add_argument("--timeout", type=float, default=15.0)
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    args = ap.parse_args(argv)

    cases = load_cases(args.cases)
    result = evaluate(cases, make_retriever(args.endpoint, args.ids_field, args.timeout), k=args.k)

    if args.json:
        print(json.dumps(result.as_dict(), ensure_ascii=False, indent=1))
    else:
        print(f"用例 {result.total} 条")
        print(f"recall@{args.k}: {result.recall:.2%}")
        print(f"MRR:        {result.mrr:.3f}")
        print(f"命中率:     {result.hit_rate:.1%}")
        if result.misses:
            print("\n未命中：")
            for case, got in result.misses[:5]:
                print(f"  - {case.question[:40]}  期望 {list(case.expected_ids)} 实际 {got[:3]}")
    return 0 if result.recall > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
