# 精簡反饋閉環系統使用指南

## 📋 概述

IMH 反饋閉環系統是一個**輕量級**的用戶反饋收集與分析工具，用於持續優化投資建議質量。

### 設計理念

- ✅ **輕量級**: 基於 JSON 文件存儲，無需數據庫
- ✅ **實用**: 聚焦核心功能 (評分 + 點贊/倒讚)
- ✅ **簡單**: NPS 計算 + 基本統計
- ✅ **隱私友好**: 匿名收集，不存儲個人信息

### 核心指標

| 指標 | 說明 | 計算方式 |
|------|------|---------|
| **平均評分** | 用戶平均滿意度 | 所有評分的平均值 |
| **點贊率** | 正面反饋比例 | 點贊數 / 總反饋數 |
| **NPS** | 淨推薦值 | (推廣者 - 貶損者) / 總評分數 × 100% |

---

## 🚀 快速開始

### 1. Python 代碼使用

```python
from services.feedback_system import FeedbackCollector, FeedbackAnalyzer

# 創建收集器
collector = FeedbackCollector()

# 提交反饋
collector.submit_feedback(
    session_id="session_001",
    query="如何評估當前市場估值？",
    response_id="resp_001",
    feedback_type="rating",
    rating=5,
    comment="非常詳細，很有幫助"
)

# 創建分析器
analyzer = FeedbackAnalyzer(collector)

# 分析數據
stats = analyzer.analyze(days=7)
print(f"平均評分：{stats['average_rating']:.2f}")
print(f"NPS: {stats['nps']:.1f}")
print(f"點贊率：{stats['thumbs_up_ratio']:.1%}")

# 生成報告
report = analyzer.generate_report(days=7)
print(report)
```

### 2. 命令行測試

```bash
# 運行 Toy Example
python services\feedback_system.py

# 輸出:
# 🔄 反饋閉環系統 Toy Example
# 
# 📝 模擬提交反饋...
# ✅ 反饋已保存：fb_20260218001959_9554
# ✅ 反饋已保存：fb_20260218001959_1952
# ...
# 
# 📊 分析反饋數據:
# 總反饋數：5
# 平均評分：4.67/5.0
# NPS: 100.0
# 點贊率：20.0%
```

---

## 📊 API 端點

### 1. 提交反饋

**端點**: `POST /api/feedback`

**請求體**:
```json
{
  "session_id": "session_001",
  "query": "如何評估當前市場估值？",
  "response_id": "resp_001",
  "feedback_type": "rating",
  "rating": 5,
  "comment": "非常詳細，很有幫助"
}
```

**反饋類型**:
- `thumbs_up`: 點贊
- `thumbs_down`: 倒讚
- `rating`: 評分 (1-5 分)

**響應**:
```json
{
  "success": true,
  "feedback_id": "fb_20260218001959_9554",
  "message": "反饋已保存"
}
```

**cURL 示例**:
```bash
curl -X POST http://localhost:8000/api/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session_001",
    "query": "如何評估當前市場估值？",
    "response_id": "resp_001",
    "feedback_type": "rating",
    "rating": 5,
    "comment": "非常詳細，很有幫助"
  }'
```

---

### 2. 獲取統計數據

**端點**: `GET /api/feedback/stats?days=7`

**參數**:
- `days`: 統計天數 (默認 7 天)

**響應**:
```json
{
  "total_feedback": 50,
  "average_rating": 4.2,
  "nps": 65.5,
  "thumbs_up_ratio": 0.78,
  "total_thumbs_up": 35,
  "total_thumbs_down": 5
}
```

**cURL 示例**:
```bash
curl http://localhost:8000/api/feedback/stats?days=7
```

---

### 3. 獲取分析報告

**端點**: `GET /api/feedback/report?days=7`

**參數**:
- `days`: 報告天數 (默認 7 天)

**響應**:
```json
{
  "report": "============================================================\n📊 反饋分析報告 (最近 7 天)\n============================================================\n\n總反饋數：50\n平均評分：4.20/5.0\n點贊率：78.0%\nNPS: 65.5\n\n👍 點贊：35\n👎 倒讚：5\n\n============================================================",
  "days": 7
}
```

**cURL 示例**:
```bash
curl "http://localhost:8000/api/feedback/report?days=7"
```

---

## 💡 使用場景

### 場景 1: Policy Gate 反饋集成

在 Policy Gate 返回響應後，自動附加反饋收集:

```python
# 1. 獲取 Policy Gate 響應
response = await policy_gate(request)

# 2. 在 UI 中顯示反饋按鈕
# [👍 點贊] [👎 倒讚] [⭐ 評分]

# 3. 用戶點擊後提交反饋
feedback_data = {
    "session_id": session_id,
    "query": request.text,
    "response_id": response.audit["ts"],  # 使用時間戳作為 response_id
    "feedback_type": "thumbs_up",  # 或 "thumbs_down", "rating"
    "rating": 5,  # 可選
    "comment": "很有幫助"  # 可選
}

requests.post("http://localhost:8000/api/feedback", json=feedback_data)
```

### 場景 2: 定期生成質量報告

```python
from services.feedback_system import FeedbackCollector, FeedbackAnalyzer

# 每週生成報告
collector = FeedbackCollector()
analyzer = FeedbackAnalyzer(collector)

# 本週報告
weekly_report = analyzer.generate_report(days=7)
print(weekly_report)

# 上月報告
monthly_report = analyzer.generate_report(days=30)
print(monthly_report)
```

### 場景 3: 監控 NPS 趨勢

```python
import json
from datetime import datetime

collector = FeedbackCollector()
analyzer = FeedbackAnalyzer(collector)

# 每日記錄 NPS
stats = analyzer.analyze(days=1)
nps_record = {
    "date": datetime.now().isoformat(),
    "nps": stats["nps"],
    "average_rating": stats["average_rating"],
    "total_feedback": stats["total_feedback"]
}

# 保存到歷史記錄
with open("nps_history.json", "a") as f:
    f.write(json.dumps(nps_record) + "\n")
```

---

## 📈 NPS 計算方法

### 評分轉換

| 評分 | 轉換為 NPS 分數 | 分類 |
|------|--------------|------|
| 5 星 | 10 分 | 推廣者 (Promoter) |
| 4 星 | 9 分 | 推廣者 (Promoter) |
| 3 星 | 7-8 分 | 被動者 (Passive) |
| 2 星 | 5-6 分 | 貶損者 (Detractor) |
| 1 星 | 0-6 分 | 貶損者 (Detractor) |

### NPS 公式

```
NPS = (推廣者數量 - 貶損者數量) / 總評分數量 × 100%
```

**示例**:
- 總評分數：100
- 推廣者 (4-5 星): 60
- 貶損者 (1-2 星): 20
- 被動者 (3 星): 20

```
NPS = (60 - 20) / 100 × 100% = 40%
```

### NPS 解讀

| NPS 範圍 | 評價 | 建議 |
|---------|------|------|
| > 75 | 優秀 | 保持現狀 |
| 50-75 | 良好 | 持續改進 |
| 25-49 | 一般 | 需要關注 |
| 0-24 | 較差 | 急需改進 |
| < 0 | 危險 | 立即行動 |

---

## 🔧 高級配置

### 1. 自定義存儲目錄

```python
# 默認存儲在 .feedback 目錄
collector = FeedbackCollector()

# 自定義目錄
collector = FeedbackCollector(storage_dir="my_feedback_data")
```

### 2. 清空反饋數據

```python
collector = FeedbackCollector()
collector.clear_feedback()  # 清空所有反饋
```

### 3. 獲取歷史反饋

```python
collector = FeedbackCollector()

# 獲取最近 7 天的反饋
recent_feedback = collector.get_recent_feedback(days=7)

# 獲取最近 30 天的反饋
monthly_feedback = collector.get_recent_feedback(days=30)

# 遍歷反饋
for record in recent_feedback:
    print(f"{record['timestamp']}: {record['feedback_type']} - {record.get('rating', 'N/A')}")
```

---

## 📁 數據存儲結構

### 文件位置

```
.feedback/
└── feedback.json
```

### JSON 結構

```json
{
  "feedback_records": [
    {
      "id": "fb_20260218001959_9554",
      "session_id": "session_001",
      "query": "如何評估當前市場估值？",
      "response_id": "resp_001",
      "feedback_type": "rating",
      "rating": 5,
      "comment": "非常詳細，很有幫助",
      "timestamp": "2026-02-18T00:19:59.123456"
    }
  ],
  "metadata": {
    "created_at": "2026-02-18T00:00:00.000000"
  }
}
```

---

## 🎯 最佳實踐

### 1. 反饋類型選擇

**推薦**:
- ✅ **點贊/倒讚**: 簡單快速，用戶負擔低
- ✅ **評分**: 更細緻的滿意度反饋

**慎用**:
- ⚠️ **長評論**: 用戶填寫意願低

### 2. 反饋時機

**最佳時機**:
- ✅ Policy Gate 返回建議後立即顯示
- ✅ 用戶查看完整報告後
- ✅ 用戶執行跟隨操作後

**避免**:
- ❌ 用戶剛輸入問題就打斷
- ❌ 頻繁彈出反饋請求

### 3. 數據分析頻率

**建議**:
- 📅 **每日**: 監控異常 (NPS 驟降)
- 📊 **每週**: 生成質量報告
- 📈 **每月**: 趨勢分析

---

## 🐛 故障排查

### 問題 1: 反饋未保存

**症狀**: 提交反饋後找不到記錄

**檢查**:
```bash
# 檢查 .feedback 目錄是否存在
ls -la .feedback/

# 檢查 feedback.json 內容
cat .feedback/feedback.json
```

**解決**:
```python
# 手動初始化
collector = FeedbackCollector()
collector.clear_feedback()  # 重新初始化
```

### 問題 2: NPS 計算錯誤

**症狀**: NPS 值異常 (如 > 100 或 < -100)

**檢查**:
```python
stats = analyzer.analyze(days=7)
print(f"總評分數：{len([r for r in collector.get_recent_feedback() if r['feedback_type'] == 'rating'])}")
print(f"推廣者：{sum(1 for r in collector.get_recent_feedback() if r.get('rating', 0) >= 4)}")
print(f"貶損者：{sum(1 for r in collector.get_recent_feedback() if r.get('rating', 0) <= 2)}")
```

### 問題 3: API 返回 500 錯誤

**症狀**: `POST /api/feedback` 返回 500

**檢查日誌**:
```bash
# 查看 API 日誌
tail -f logs/api.log
```

**常見原因**:
- 反饋類型無效 (必須是 thumbs_up/thumbs_down/rating)
- 評分超出範圍 (必須是 1-5)

---

## 📊 示例輸出

### 完整報告示例

```
============================================================
📊 反饋分析報告 (最近 7 天)
============================================================

總反饋數：50
平均評分：4.20/5.0
點贊率：78.0%
NPS: 65.5

👍 點贊：35
👎 倒讚：5

============================================================
```

### API 響應示例

**提交反饋**:
```json
{
  "success": true,
  "feedback_id": "fb_20260218001959_9554",
  "message": "反饋已保存"
}
```

**統計數據**:
```json
{
  "total_feedback": 50,
  "average_rating": 4.2,
  "nps": 65.5,
  "thumbs_up_ratio": 0.78,
  "total_thumbs_up": 35,
  "total_thumbs_down": 5
}
```

---

## 🎉 總結

**精簡反饋閉環系統**提供:

✅ **輕量級存儲**: JSON 文件，無需數據庫  
✅ **核心指標**: NPS + 平均評分 + 點贊率  
✅ **API 集成**: 3 個簡單端點  
✅ **隱私友好**: 匿名收集  

**核心理念**: 
> "反饋不在多，而在精。每個反饋都應該能指導改進。"

**下一步**: 
- 集成到前端 UI (點贊/倒讚按鈕)
- 定期生成質量報告
- 根據反饋優化 Policy Gate 建議

---

## 📚 相關文件

- **代碼**: [`services/feedback_system.py`](file:///d:/Project_dev/investment-masters-handbook/services/feedback_system.py)
- **API 集成**: [`services/rag_service.py`](file:///d:/Project_dev/investment-masters-handbook/services/rag_service.py#L1370-L1460)
- **多 Agent 系統**: [`agents/multi_agent_system.py`](file:///d:/Project_dev/investment-masters-handbook/agents/multi_agent_system.py)
