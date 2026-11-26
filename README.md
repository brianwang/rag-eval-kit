# rag-eval-kit

**最小可用的 RAG 检索评测工具。** 给一组「问题 + 应当被检索到的文档 id」，算出 recall@k、MRR、命中率，并列出未命中的用例。

不绑定任何向量库——你只要提供一个 `retrieve(question) -> [doc_id...]` 函数，或者一个 HTTP 接口。

[![CI](https://github.com/brianwang/rag-eval-kit/actions/workflows/ci.yml/badge.svg)](https://github.com/brianwang/rag-eval-kit/actions/workflows/ci.yml)

## 为什么需要它

RAG 项目最常见的失败模式：**改完 prompt 或切分策略，不知道是变好还是变坏。**
没有评测集，所有"优化"都是凭感觉。

这个工具只做一件事：把「感觉」变成数字。

## 安装

```bash
pip install git+https://github.com/brianwang/rag-eval-kit
```

## 用法一：命令行打 HTTP 接口

```bash
# cases.jsonl 每行一条
# {"question": "员工年假多少天", "expected_ids": ["hr-policy-3"]}

rageval cases.jsonl --endpoint http://localhost:8000/search --k 5
```

输出：

```
用例 42 条
recall@5: 78.57%
MRR:      0.612
命中率:   85.7%

未命中：
  - 报销流程要走几级审批  期望 ['finance-2'] 实际 ['finance-7', 'finance-9']
```

你的接口需要接受 `POST {"query": "..."}`，返回 `{"results": [{"id": "..."}, ...]}`（字段名可用 `--ids-field` 改）。

## 用法二：当库用

```python
from rageval import Case, evaluate

cases = [Case("员工年假多少天", ["hr-policy-3"])]
result = evaluate(cases, retrieve=lambda q: my_search(q), k=5)
print(result.as_dict())
```

## 指标说明

| 指标 | 含义 | 什么时候看它 |
|---|---|---|
| **recall@k** | 期望文档有多少比例出现在前 k 条 | 检索层是否漏召 |
| **MRR** | 第一个命中排在第几（倒数） | 排序质量 |
| **hit_rate** | 至少命中一条的用例占比 | 整体可用性 |

> `recall@k` 低 = 检索没找到；
> `recall@k` 高但 `MRR` 低 = 找到了但排太后，重排有问题。

## 设计取舍

- **不自动生成测试集**：测试集必须来自真实用户问题，自动生成的自评毫无意义
- **不内置 embedding**：换成任何检索方案都能用，不被框架绑死
- **纯标准库**：零依赖，塞进任何项目都不增负担

## 协议

MIT
