"""
Investment Masters Handbook - Prometheus 指標導出模塊

提供自定義指標用於監控系統性能、LLM 使用情況、緩存效率等
"""

from prometheus_client import (
    Counter,
    Gauge,
    Histogram,
    Summary,
    CollectorRegistry,
    generate_latest,
    CONTENT_TYPE_LATEST,
    start_http_server,
)
from prometheus_client.core import REGISTRY
import time
from typing import Dict, Any, Optional
from contextlib import contextmanager
import threading


# ============================================
# 自定義指標註冊表
# ============================================
class IMHMetricsRegistry:
    """IMH 自定義指標註冊表"""
    
    def __init__(self):
        self.registry = CollectorRegistry()
        self._lock = threading.Lock()
        self._register_metrics()
    
    def _register_metrics(self):
        """註冊所有指標"""
        
        # HTTP 請求指標
        self.http_requests_total = Counter(
            'imh_http_requests_total',
            'Total HTTP requests',
            ['method', 'endpoint', 'status'],
            registry=self.registry
        )
        
        self.http_request_duration_seconds = Histogram(
            'imh_http_request_duration_seconds',
            'HTTP request duration in seconds',
            ['method', 'endpoint'],
            buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
            registry=self.registry
        )
        
        self.http_requests_in_flight = Gauge(
            'imh_http_requests_in_flight',
            'Number of HTTP requests currently being processed',
            ['method', 'endpoint'],
            registry=self.registry
        )
        
        # LLM 使用指標
        self.llm_tokens_total = Counter(
            'imh_llm_tokens_total',
            'Total tokens used by LLM',
            ['model', 'type'],  # type: prompt, completion
            registry=self.registry
        )
        
        self.llm_calls_total = Counter(
            'imh_llm_calls_total',
            'Total LLM API calls',
            ['model', 'status'],  # status: success, error
            registry=self.registry
        )
        
        self.llm_call_duration_seconds = Histogram(
            'imh_llm_call_duration_seconds',
            'LLM API call duration in seconds',
            ['model'],
            buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0),
            registry=self.registry
        )
        
        # 向量檢索指標
        self.vectorstore_query_total = Counter(
            'imh_vectorstore_query_total',
            'Total vectorstore queries',
            ['status'],  # status: success, error
            registry=self.registry
        )
        
        self.vectorstore_query_duration_seconds = Histogram(
            'imh_vectorstore_query_duration_seconds',
            'Vectorstore query duration in seconds',
            buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5),
            registry=self.registry
        )
        
        self.vectorstore_documents_count = Gauge(
            'imh_vectorstore_documents_count',
            'Number of documents in vectorstore',
            ['collection'],
            registry=self.registry
        )
        
        # 緩存指標
        self.cache_hits_total = Counter(
            'imh_cache_hits_total',
            'Total cache hits',
            ['cache_type'],  # cache_type: document_split, llm_response, vectorstore
            registry=self.registry
        )
        
        self.cache_misses_total = Counter(
            'imh_cache_misses_total',
            'Total cache misses',
            ['cache_type'],
            registry=self.registry
        )
        
        self.cache_size = Gauge(
            'imh_cache_size',
            'Current cache size',
            ['cache_type'],
            registry=self.registry
        )
        
        # 大師會診指標
        self.ensemble_experts_count = Histogram(
            'imh_ensemble_experts_count',
            'Number of experts in ensemble reasoning',
            buckets=(1, 2, 3, 4, 5, 6, 7, 8, 9, 10),
            registry=self.registry
        )
        
        self.ensemble_rules_count = Histogram(
            'imh_ensemble_rules_count',
            'Number of rules matched in ensemble reasoning',
            buckets=(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10),
            registry=self.registry
        )
        
        self.ensemble_confidence = Histogram(
            'imh_ensemble_confidence',
            'Ensemble reasoning confidence score',
            buckets=(0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0),
            registry=self.registry
        )
        
        # 政策閘指標
        self.policy_gate_evaluations_total = Counter(
            'imh_policy_gate_evaluations_total',
            'Total policy gate evaluations',
            ['result'],  # result: approved, rejected
            registry=self.registry
        )
        
        self.policy_gate_regime = Gauge(
            'imh_policy_gate_regime',
            'Current market regime detected',
            ['regime_id'],
            registry=self.registry
        )
        
        self.policy_gate_risk_multiplier = Gauge(
            'imh_policy_gate_risk_multiplier',
            'Current risk multiplier from policy gate',
            registry=self.registry
        )
        
        # 系統資源指標
        self.system_memory_usage = Gauge(
            'imh_system_memory_usage_bytes',
            'System memory usage',
            ['type'],  # type: rss, vms, percent
            registry=self.registry
        )
        
        self.system_cpu_usage = Gauge(
            'imh_system_cpu_usage_percent',
            'System CPU usage percentage',
            registry=self.registry
        )
        
        # 審計日誌指標
        self.audit_events_total = Counter(
            'imh_audit_events_total',
            'Total audit events',
            ['event_type', 'severity'],
            registry=self.registry
        )
    
    def get_registry(self) -> CollectorRegistry:
        """獲取指標註冊表"""
        return self.registry
    
    def get_metrics(self) -> bytes:
        """獲取 Prometheus 格式的指標"""
        return generate_latest(self.registry)


# ============================================
# 全局指標實例
# ============================================
_metrics_registry: Optional[IMHMetricsRegistry] = None


def get_metrics_registry() -> IMHMetricsRegistry:
    """獲取全局指標註冊表"""
    global _metrics_registry
    if _metrics_registry is None:
        _metrics_registry = IMHMetricsRegistry()
    return _metrics_registry


def get_metrics() -> bytes:
    """獲取 Prometheus 指標"""
    return get_metrics_registry().get_metrics()


# ============================================
# 便捷函數
# ============================================

# HTTP 請求追蹤
def track_http_request(method: str, endpoint: str, status: int, duration: float):
    """追蹤 HTTP 請求"""
    registry = get_metrics_registry()
    registry.http_requests_total.labels(method=method, endpoint=endpoint, status=status).inc()
    registry.http_request_duration_seconds.labels(method=method, endpoint=endpoint).observe(duration)


@contextmanager
def http_request_tracker(method: str, endpoint: str):
    """HTTP 請求追蹤上下文管理器"""
    registry = get_metrics_registry()
    registry.http_requests_in_flight.labels(method=method, endpoint=endpoint).inc()
    start_time = time.time()
    status = 200
    
    try:
        yield lambda s: setattr(status, '__value__', s)
    except Exception as e:
        status = getattr(e, 'status_code', 500)
        raise
    finally:
        duration = time.time() - start_time
        registry.http_requests_in_flight.labels(method=method, endpoint=endpoint).dec()
        track_http_request(method, endpoint, getattr(status, '__value__', status), duration)


# LLM 使用追蹤
def track_llm_usage(model: str, prompt_tokens: int, completion_tokens: int, duration: float, success: bool = True):
    """追蹤 LLM 使用情況"""
    registry = get_metrics_registry()
    
    registry.llm_tokens_total.labels(model=model, type='prompt').inc(prompt_tokens)
    registry.llm_tokens_total.labels(model=model, type='completion').inc(completion_tokens)
    registry.llm_calls_total.labels(model=model, status='success' if success else 'error').inc()
    registry.llm_call_duration_seconds.labels(model=model).observe(duration)


# 向量檢索追蹤
def track_vectorstore_query(duration: float, success: bool = True):
    """追蹤向量檢索"""
    registry = get_metrics_registry()
    registry.vectorstore_query_total.labels(status='success' if success else 'error').inc()
    registry.vectorstore_query_duration_seconds.observe(duration)


# 緩存追蹤
def track_cache_hit(cache_type: str):
    """追蹤緩存命中"""
    registry = get_metrics_registry()
    registry.cache_hits_total.labels(cache_type=cache_type).inc()


def track_cache_miss(cache_type: str):
    """追蹤緩存未命中"""
    registry = get_metrics_registry()
    registry.cache_misses_total.labels(cache_type=cache_type).inc()


def update_cache_size(cache_type: str, size: int):
    """更新緩存大小"""
    registry = get_metrics_registry()
    registry.cache_size.labels(cache_type=cache_type).set(size)


# 大師會診追蹤
def track_ensemble(experts_count: int, rules_count: int, confidence: float):
    """追蹤大師會診"""
    registry = get_metrics_registry()
    registry.ensemble_experts_count.observe(experts_count)
    registry.ensemble_rules_count.observe(rules_count)
    registry.ensemble_confidence.observe(confidence)


# 政策閘追蹤
def track_policy_gate(result: str, regime_id: str, risk_multiplier: float):
    """追蹤政策閘"""
    registry = get_metrics_registry()
    registry.policy_gate_evaluations_total.labels(result=result).inc()
    registry.policy_gate_regime.labels(regime_id=regime_id).set(1)
    registry.policy_gate_risk_multiplier.set(risk_multiplier)


# 審計事件追蹤
def track_audit_event(event_type: str, severity: str = 'info'):
    """追蹤審計事件"""
    registry = get_metrics_registry()
    registry.audit_events_total.labels(event_type=event_type, severity=severity).inc()


# 系統資源追蹤
def update_system_metrics(memory_rss: int, memory_vms: int, memory_percent: float, cpu_percent: float):
    """更新系統資源指標"""
    registry = get_metrics_registry()
    registry.system_memory_usage.labels(type='rss').set(memory_rss)
    registry.system_memory_usage.labels(type='vms').set(memory_vms)
    registry.system_memory_usage.labels(type='percent').set(memory_percent)
    registry.system_cpu_usage.set(cpu_percent)


# ============================================
# Prometheus 服務器
# ============================================
def start_metrics_server(port: int = 8001):
    """啟動 Prometheus 指標服務器"""
    start_http_server(port, registry=get_metrics_registry().get_registry())
    print(f"✅ Prometheus metrics server started on port {port}")


# ============================================
# 中間件 (FastAPI)
# ============================================
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class PrometheusMiddleware(BaseHTTPMiddleware):
    """FastAPI Prometheus 監控中間件"""
    
    async def dispatch(self, request: Request, call_next):
        method = request.method
        endpoint = request.url.path
        
        # 跳過靜態文件和指標端點
        if endpoint.startswith('/docs') or endpoint.startswith('/openapi') or endpoint == '/metrics':
            return await call_next(request)
        
        with http_request_tracker(method, endpoint) as track_status:
            response = await call_next(request)
            track_status(response.status_code)
            return response


# ============================================
# 初始化
# ============================================
def setup_monitoring(enable_server: bool = True, server_port: int = 8001):
    """設置監控系統"""
    registry = get_metrics_registry()
    
    if enable_server:
        start_metrics_server(server_port)
    
    return registry
