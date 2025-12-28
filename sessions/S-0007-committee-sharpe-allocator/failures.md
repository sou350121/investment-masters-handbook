# 失败路径记录 (Failure Log)

## 尝试 #1
- 日期：2025-12-29
- 现象：`pytest tests/test_ensemble.py` 导入 `services/rag_service.py` 失败：`ImportError: cannot import name 'EnsembleRequest' from 'tools.rag_core'`。
- 根因分析：`rag_service.py` 过度依赖从 `tools/rag_core.py` 导入 API request/response models（其中 `EnsembleRequest` 并不存在于 rag_core）。
- 教训/对策：将 API request model（`EnsembleRequest`）保留在 `services/rag_service.py`；仅从 `tools/rag_core.py` 导入共享逻辑（`run_ensemble_committee` + response_model）。随后单测通过。
