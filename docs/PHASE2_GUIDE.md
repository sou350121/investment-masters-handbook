# 阶段 2 实战指南

**完成日期**: 2026-02-18  
**状态**: ✅ 已完成

---

## 📋 概述

阶段 2 新增 **4 个核心模块**,将系统从静态知识库升级为动态智能投资平台:

| 模块 | 功能 | 核心文件 |
|------|------|---------|
| **实时数据** | 获取 VIX、通胀、利率等 | `services/realtime_data.py` |
| **多 Agent** | 3 个专家 Agent 协作决策 | `agents/multi_agent_system.py` |
| **反馈系统** | 收集用户反馈持续优化 | `services/feedback_system.py` |
| **高级回测** | 验证策略历史表现 | `services/backtest_platform.py` |

---

## 🚀 快速开始

### 1. 实时数据管道

```python
from services.realtime_data import get_pipeline

pipeline = get_pipeline()
features = pipeline.get_features()

print(f"VIX: {features['vix']}")
print(f"通胀率：{features['inflation']}")
```

**核心功能**:
- ✅ VIX 恐慌指数
- ✅ 通胀数据 (CPI/PCE)
- ✅ 利率决策
- ✅ 收益率曲线

### 2. 多 Agent 协作

```python
from agents.multi_agent_system import MultiAgentCoordinator, MarketData

coordinator = MultiAgentCoordinator()

market_data = MarketData(
    spy_price=450,
    spy_ma_200=420,
    vix=25,
    inflation_rate=3.5,
    interest_rate=5.0
)

decision = coordinator.make_decision(market_data)
print(f"建议仓位：{decision.portfolio_allocation.get('equity', 0):.1%}")
```

**3 个 Agent**:
- **RegimeAnalyst**: 识别市场状态
- **RiskManager**: 评估风险
- **PortfolioOptimizer**: 优化资产配置

### 3. 反馈系统

```python
from services.feedback_system import FeedbackCollector

collector = FeedbackCollector()
collector.submit_feedback(
    session_id="session_001",
    query="如何评估市场估值？",
    response_id="resp_001",
    feedback_type="thumbs_up",
    rating=5
)

# 获取统计
stats = collector.get_stats()
```

### 4. 高级回测

```python
from services.backtest_platform import BacktestPlatform, SmaCross
from backtesting.test import GOOG

platform = BacktestPlatform(initial_cash=10000)
data = GOOG

# 运行回测
stats = platform.run(SmaCross, data, {"n1": 10, "n2": 20})
stats.print_summary()
```

---

## 📊 4 个高级回测示例

### 示例 1: RAG 增强型回测

**文件**: `examples/example_1_rag_backtest.py`

**功能**:
- 从 RAG 规则库提取交易信号
- 对比不同投资人规则效果

**策略**:
- RAGRuleStrategy: 规则驱动
- InvestorBlendStrategy: 达利欧 + 索罗斯 + 林奇混合

### 示例 2: Policy Gate 动态仓位

**文件**: `examples/example_2_policy_gate_backtest.py`

**功能**:
- Policy Gate 评估市场状态
- 动态调整仓位大小

**仓位映射**:
```python
if vix > 40:      # 危机
    position_size = 0.2
elif vix > 30:    # 熊市
    position_size = 0.5
elif vix < 20:    # 牛市
    position_size = 1.0
else:             # 震荡
    position_size = 0.7
```

### 示例 3: 多 Agent 协作回测

**文件**: `examples/example_3_multi_agent_backtest.py`

**策略**:
- SingleAgentStrategy: 单一 Agent
- DualAgentStrategy: 双 Agent 协作
- MultiAgentCoordinatorStrategy: 完整系统
- DynamicAgentWeightStrategy: 动态权重

### 示例 4: 反馈驱动自适应

**文件**: `examples/example_4_feedback_driven_backtest.py`

**功能**:
- 收集交易反馈 (盈亏)
- 根据反馈调整策略参数

**自适应逻辑**:
```python
if win_rate < 0.4 or consecutive_losses >= 3:
    # 表现差 → 增加参数 (减少交易频率)
    adjustment_factor = 1.0 + 0.3
elif win_rate > 0.6:
    # 表现好 → 减小参数
    adjustment_factor = 1.0 - 0.05
```

---

## 📁 文件结构

```
investment-masters-handbook/
├── services/
│   ├── realtime_data.py       # 实时数据管道
│   ├── feedback_system.py     # 反馈系统
│   ├── backtest_platform.py   # 回测平台
│   └── rag_service.py         # RAG 服务 (已集成反馈 API)
├── agents/
│   └── multi_agent_system.py  # 多 Agent 系统
├── examples/
│   ├── example_1_rag_backtest.py         # RAG 回测
│   ├── example_2_policy_gate_backtest.py # Policy Gate
│   ├── example_3_multi_agent_backtest.py # 多 Agent
│   └── example_4_feedback_driven_backtest.py # 反馈驱动
└── docs/
    ├── PHASE2_SUMMARY.md           # 阶段 2 总结
    ├── REALTIME_DATA_GUIDE.md      # 实时数据指南
    ├── MULTI_AGENT_GUIDE.md        # 多 Agent 指南
    ├── FEEDBACK_SYSTEM_GUIDE.md    # 反馈系统指南
    ├── BACKTEST_PLATFORM_GUIDE.md  # 回测平台指南
    └── ADVANCED_BACKTEST_EXAMPLES.md # 高级示例集
```

---

## 🎯 核心设计理念

### 1. 精简实用

**排除的功能** (过于复杂):
- ❌ 加密货币数据
- ❌ A/B 测试
- ❌ 重型 Agent 框架 (AutoGen/CrewAI)

**保留的功能** (核心实用):
- ✅ VIX、通胀、利率等核心指标
- ✅ 评分 + 点赞/倒讚反馈
- ✅ 轻量级 Agent 系统

### 2. 模块化设计

每个模块职责单一:
- `RealTimeDataPipeline`: 只负责数据采集
- `RegimeAnalyst`: 只负责市场状态识别
- `FeedbackCollector`: 只负责反馈收集

### 3. 实战导向

- ✅ 所有代码可直接运行
- ✅ 提供完整示例
- ✅ 包含故障排查

---

## 📈 性能指标

| 指标 | 数值 |
|------|------|
| **新增代码** | ~1,620 行 |
| **新增文档** | ~2,500 行 |
| **示例数量** | 5 个 (1 个 toy + 4 个高级) |
| **策略数量** | 15 个 (3 个内置 + 12 个示例) |

---

## 🔧 常见使用场景

### 场景 1: 宏观分析

```python
# 1. 获取实时数据
from services.realtime_data import get_pipeline
pipeline = get_pipeline()
features = pipeline.get_features()

# 2. 多 Agent 分析
from agents.multi_agent_system import MultiAgentCoordinator
coordinator = MultiAgentCoordinator()
decision = coordinator.make_decision(market_data)

# 3. Policy Gate 决策
```

### 场景 2: 策略验证

```python
# 1. 定义策略
from services.backtest_platform import BacktestPlatform, SmaCross
platform = BacktestPlatform()

# 2. 运行回测
stats = platform.run(SmaCross, data, {"n1": 10, "n2": 20})

# 3. 参数优化
best_params, best_stats = platform.optimize(SmaCross, data, param_grid)

# 4. 对比结果
stats.print_summary()
```

### 场景 3: 持续优化

```python
# 1. 收集反馈
from services.feedback_system import FeedbackCollector
collector = FeedbackCollector()
collector.submit_feedback(...)

# 2. 分析表现
from services.feedback_system import FeedbackAnalyzer
analyzer = FeedbackAnalyzer(collector)
report = analyzer.generate_report(days=7)

# 3. 调整策略
```

---

## 🐛 常见问题

### Q1: 向量库加载失败

**症状**: `⚠️ 向量库加载失败`

**解决**:
```python
from services.rag_service import initialize_rag
initialize_rag()
```

### Q2: Policy Gate 未初始化

**症状**: `⚠️ Policy Gate 初始化失败`

**解决**:
```python
from services.realtime_data import initialize_pipeline
initialize_pipeline()
```

### Q3: 多 Agent 导入错误

**症状**: `ImportError: cannot import name 'RegimeAnalystAgent'`

**解决**:
- 确保 `agents/__init__.py` 存在
- 检查 `agents/multi_agent_system.py` 是否正确

---

## 📚 详细文档索引

| 文档 | 用途 |
|------|------|
| [`PHASE2_SUMMARY.md`](file:///d:/Project_dev/investment-masters-handbook/docs/PHASE2_SUMMARY.md) | 阶段 2 完整总结 |
| [`REALTIME_DATA_GUIDE.md`](file:///d:/Project_dev/investment-masters-handbook/docs/REALTIME_DATA_GUIDE.md) | 实时数据详细指南 |
| [`MULTI_AGENT_GUIDE.md`](file:///d:/Project_dev/investment-masters-handbook/docs/MULTI_AGENT_GUIDE.md) | 多 Agent 系统详解 |
| [`FEEDBACK_SYSTEM_GUIDE.md`](file:///d:/Project_dev/investment-masters-handbook/docs/FEEDBACK_SYSTEM_GUIDE.md) | 反馈系统使用指南 |
| [`BACKTEST_PLATFORM_GUIDE.md`](file:///d:/Project_dev/investment-masters-handbook/docs/BACKTEST_PLATFORM_GUIDE.md) | 回测平台完整指南 |
| [`ADVANCED_BACKTEST_EXAMPLES.md`](file:///d:/Project_dev/investment-masters-handbook/docs/ADVANCED_BACKTEST_EXAMPLES.md) | 4 个高级示例详解 |

---

## 🎉 总结

**阶段 2** 成功将系统从**静态知识库**升级为**动态智能投资平台**:

✅ **实时数据** - 连接真实市场  
✅ **多 Agent** - 模拟专家团队  
✅ **反馈闭环** - 持续优化  
✅ **高级回测** - 历史验证  

**核心理念**: 
> "精简实用，模块化设计，实战导向。"

**下一步建议**:
- 运行所有示例，熟悉功能
- 根据需求修改策略参数
- 创建自定义策略
- 集成到生产环境

---

**日期**: 2026-02-18  
**版本**: v2.0  
**状态**: ✅ 已完成
