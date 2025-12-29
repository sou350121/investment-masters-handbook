'use client';

import React, { useEffect, useMemo, useState } from 'react';
import {
  Alert,
  Box,
  Button,
  Chip,
  CircularProgress,
  Divider,
  List,
  ListItemButton,
  ListItemText,
  Paper,
  Stack,
  Tab,
  Tabs,
  Typography,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';

type Metrics = Record<string, any>;

type BacktestRunSummary = {
  run_id: string;
  root: string;
  last_modified_iso: string;
  modes?: string[];
  metrics?: Record<string, Metrics>;
};

type EquityPoint = { date: string; equity: number };

type Allocation = { stocks?: number; bonds?: number; gold?: number; cash?: number };

type HistoryRow = {
  date?: string;
  brief?: string;
  risk_bias?: string | number;
  allocation?: Allocation;
  equity?: number;
  [k: string]: any;
};

type BacktestRunDetail = {
  run_id: string;
  root: string;
  files?: Record<string, boolean>;
  config?: Record<string, any>;
  metrics?: Record<string, Metrics>;
  equity?: Record<string, EquityPoint[]>;
  history?: Record<string, HistoryRow[]>;
  comparison_md?: string | null;
};

function num(v: any): number | null {
  const x = Number(v);
  return Number.isFinite(x) ? x : null;
}

function fmtPct(v: any, digits = 1) {
  const x = num(v);
  if (x === null) return '--';
  return `${(x * 100).toFixed(digits)}%`;
}

function fmtNum(v: any, digits = 3) {
  const x = num(v);
  if (x === null) return '--';
  return x.toFixed(digits);
}

function getAuthHeaders(): Record<string, string> {
  const headers: Record<string, string> = {};
  try {
    if (typeof window !== 'undefined') {
      const t = (window.localStorage.getItem('imh_api_token') || '').trim();
      if (t) headers.Authorization = `Bearer ${t}`;
    }
  } catch {
    // ignore
  }
  return headers;
}

function Sparkline({
  points,
  color,
}: {
  points: EquityPoint[] | undefined;
  color: string;
}) {
  const w = 260;
  const h = 56;
  const pad = 4;
  const ys = (points || []).map((p) => Number(p.equity)).filter((x) => Number.isFinite(x));
  if (!ys || ys.length < 2) {
    return (
      <Box
        sx={{
          width: w,
          height: h,
          borderRadius: 2,
          bgcolor: 'rgba(0,0,0,0.04)',
        }}
      />
    );
  }
  const minY = Math.min(...ys);
  const maxY = Math.max(...ys);
  const scaleX = (i: number) => pad + (i / (ys.length - 1)) * (w - 2 * pad);
  const scaleY = (v: number) => {
    if (maxY === minY) return h / 2;
    const t = (v - minY) / (maxY - minY);
    return h - pad - t * (h - 2 * pad);
  };
  const d = ys
    .map((v, i) => `${i === 0 ? 'M' : 'L'}${scaleX(i).toFixed(1)},${scaleY(v).toFixed(1)}`)
    .join(' ');

  return (
    <Box
      component="svg"
      viewBox={`0 0 ${w} ${h}`}
      sx={{
        width: w,
        height: h,
        borderRadius: 2,
        bgcolor: 'rgba(0,0,0,0.03)',
        border: '1px solid rgba(0,0,0,0.06)',
      }}
    >
      <path d={d} stroke={color} strokeWidth={2} fill="none" />
    </Box>
  );
}

function AllocationBars({ alloc }: { alloc: Allocation | undefined }) {
  const a = alloc || {};
  const rows = [
    { k: 'stocks', label: '股', v: num(a.stocks) ?? 0, color: 'primary.main' },
    { k: 'bonds', label: '债', v: num(a.bonds) ?? 0, color: 'info.main' },
    { k: 'gold', label: '金', v: num(a.gold) ?? 0, color: 'warning.main' },
    { k: 'cash', label: '现', v: num(a.cash) ?? 0, color: 'success.main' },
  ];
  return (
    <Stack spacing={0.6} sx={{ minWidth: 220 }}>
      {rows.map((r) => (
        <Box key={r.k}>
          <Stack direction="row" justifyContent="space-between" alignItems="center">
            <Typography variant="caption" fontWeight={900}>
              {r.label}
            </Typography>
            <Typography variant="caption" color="text.secondary" fontWeight={800}>
              {Math.round(r.v)}%
            </Typography>
          </Stack>
          <Box
            sx={{
              mt: 0.35,
              height: 7,
              borderRadius: 99,
              bgcolor: 'rgba(0,0,0,0.06)',
              overflow: 'hidden',
            }}
          >
            <Box sx={{ height: 7, width: `${Math.max(0, Math.min(100, r.v))}%`, bgcolor: r.color }} />
          </Box>
        </Box>
      ))}
    </Stack>
  );
}

function MetricsCard({ title, metrics }: { title: string; metrics: Metrics | undefined }) {
  const m = metrics || {};
  return (
    <Paper variant="outlined" sx={{ p: 2, borderRadius: 3, flex: 1, minWidth: 260 }}>
      <Typography variant="subtitle2" fontWeight={900} sx={{ mb: 1 }}>
        {title}
      </Typography>
      <Stack direction="row" spacing={2} flexWrap="wrap" useFlexGap>
        <Box sx={{ minWidth: 120 }}>
          <Typography variant="caption" color="text.secondary" fontWeight={800}>
            Sortino
          </Typography>
          <Typography variant="body2" fontWeight={900}>
            {fmtNum(m.sortino_ratio, 3)}
          </Typography>
        </Box>
        <Box sx={{ minWidth: 120 }}>
          <Typography variant="caption" color="text.secondary" fontWeight={800}>
            Sharpe
          </Typography>
          <Typography variant="body2" fontWeight={900}>
            {fmtNum(m.sharpe_ratio, 3)}
          </Typography>
        </Box>
        <Box sx={{ minWidth: 120 }}>
          <Typography variant="caption" color="text.secondary" fontWeight={800}>
            CAGR
          </Typography>
          <Typography variant="body2" fontWeight={900}>
            {fmtPct(m.cagr)}
          </Typography>
        </Box>
        <Box sx={{ minWidth: 120 }}>
          <Typography variant="caption" color="text.secondary" fontWeight={800}>
            MaxDD
          </Typography>
          <Typography variant="body2" fontWeight={900}>
            {fmtPct(m.max_drawdown)}
          </Typography>
        </Box>
        <Box sx={{ minWidth: 120 }}>
          <Typography variant="caption" color="text.secondary" fontWeight={800}>
            Total
          </Typography>
          <Typography variant="body2" fontWeight={900}>
            {fmtPct(m.total_return)}
          </Typography>
        </Box>
      </Stack>
    </Paper>
  );
}

export default function BacktestHistory() {
  const [runs, setRuns] = useState<BacktestRunSummary[]>([]);
  const [selectedRun, setSelectedRun] = useState<string | null>(null);
  const [detail, setDetail] = useState<BacktestRunDetail | null>(null);
  const [loadingRuns, setLoadingRuns] = useState(false);
  const [loadingDetail, setLoadingDetail] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [mode, setMode] = useState<'A' | 'B'>('A');

  const flow = useMemo(
    () => [
      { label: 'news/signals', hint: '输入（brief_text / risk_bias）' },
      { label: 'committee', hint: 'LLM 委员会（可缓存）' },
      { label: 'adjudicator', hint: 'impact×confidence 合成' },
      { label: 'allocator', hint: '确定性 primary 配置' },
      { label: 'execution', hint: '执行/成本/滑点' },
      { label: 'metrics', hint: '曲线 + Sortino/Sharpe' },
    ],
    [],
  );

  async function loadRuns() {
    setLoadingRuns(true);
    setError(null);
    try {
      const resp = await fetch('/api/backtest/runs', {
        headers: { ...getAuthHeaders() },
      });
      if (!resp.ok) {
        const body = await resp.text().catch(() => '');
        throw new Error(`加载回测 runs 失败（HTTP ${resp.status}）${body ? `: ${body}` : ''}`);
      }
      const data = await resp.json();
      setRuns(Array.isArray(data?.runs) ? data.runs : []);
    } catch (e: any) {
      setError(e?.message || '加载回测 runs 失败');
      setRuns([]);
    } finally {
      setLoadingRuns(false);
    }
  }

  async function loadDetail(runId: string) {
    setLoadingDetail(true);
    setError(null);
    setDetail(null);
    try {
      const resp = await fetch(`/api/backtest/runs/${encodeURIComponent(runId)}`, {
        headers: { ...getAuthHeaders() },
      });
      if (!resp.ok) {
        const body = await resp.text().catch(() => '');
        throw new Error(`加载回测详情失败（HTTP ${resp.status}）${body ? `: ${body}` : ''}`);
      }
      const data = (await resp.json()) as BacktestRunDetail;
      setDetail(data);
      const modes = Object.keys(data?.metrics || {});
      if (modes.includes('A')) setMode('A');
      else if (modes.includes('B')) setMode('B');
    } catch (e: any) {
      setError(e?.message || '加载回测详情失败');
    } finally {
      setLoadingDetail(false);
    }
  }

  useEffect(() => {
    loadRuns();
  }, []);

  const historyRows = (detail?.history || {})[mode] || [];
  const equityPts = (detail?.equity || {})[mode] || [];

  return (
    <Box sx={{ maxWidth: 1100, mx: 'auto' }}>
      <Stack direction={{ xs: 'column', sm: 'row' }} justifyContent="space-between" alignItems={{ xs: 'flex-start', sm: 'center' }} spacing={2} sx={{ mb: 2 }}>
        <Box>
          <Typography variant="h4" fontWeight={900} gutterBottom>
            📈 回测历史工作台
          </Typography>
          <Typography variant="body2" color="text.secondary">
            把 `results/&lt;run_id&gt;/` 的指标、曲线与 rebalance history 变成可视化证据链（方便复盘与迭代参数）。
          </Typography>
        </Box>
        <Button variant="outlined" startIcon={<RefreshIcon />} onClick={loadRuns} disabled={loadingRuns}>
          刷新 runs
        </Button>
      </Stack>

      <Paper variant="outlined" sx={{ p: 2, borderRadius: 4, mb: 2, bgcolor: 'rgba(25,118,210,0.02)' }}>
        <Typography variant="caption" color="text.secondary" fontWeight={900} sx={{ display: 'block', mb: 1 }}>
          Flow（回测流程）
        </Typography>
        <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
          {flow.map((s, idx) => (
            <Chip
              key={s.label}
              label={`${idx + 1}. ${s.label}`}
              variant="outlined"
              sx={{ fontWeight: 900 }}
              title={s.hint}
            />
          ))}
        </Stack>
      </Paper>

      {error && (
        <Alert severity="error" sx={{ mb: 2, borderRadius: 3 }}>
          {error}
        </Alert>
      )}

      <Stack direction={{ xs: 'column', md: 'row' }} spacing={2} alignItems="stretch">
        {/* Left: Runs list */}
        <Paper variant="outlined" sx={{ p: 1.5, borderRadius: 4, minWidth: { md: 320 } }}>
          <Typography variant="subtitle2" fontWeight={900} sx={{ px: 1, mb: 1 }}>
            Runs（{runs.length}）
          </Typography>
          <Divider sx={{ mb: 1 }} />
          {loadingRuns ? (
            <Box sx={{ py: 4, textAlign: 'center' }}>
              <CircularProgress size={24} />
              <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1 }}>
                加载中...
              </Typography>
            </Box>
          ) : runs.length === 0 ? (
            <Alert severity="info" sx={{ borderRadius: 3 }}>
              还没有检测到回测输出。先运行一次：`python scripts/run_backtest_biweekly.py ...`（会生成 `results/&lt;run_id&gt;/`）。
            </Alert>
          ) : (
            <List dense disablePadding>
              {runs.map((r) => {
                const isActive = r.run_id === selectedRun;
                const mA = r.metrics?.A || {};
                const mB = r.metrics?.B || {};
                return (
                  <ListItemButton
                    key={r.run_id}
                    selected={isActive}
                    onClick={() => {
                      setSelectedRun(r.run_id);
                      loadDetail(r.run_id);
                    }}
                    sx={{ borderRadius: 2, mb: 0.5 }}
                  >
                    <ListItemText
                      primary={
                        <Stack direction="row" spacing={1} alignItems="center">
                          <Typography variant="body2" fontWeight={900} sx={{ fontFamily: 'monospace' }}>
                            {r.run_id}
                          </Typography>
                          <Chip size="small" label={(r.modes || []).join('/') || '—'} sx={{ fontWeight: 900 }} />
                        </Stack>
                      }
                      secondary={
                        <Box sx={{ mt: 0.5 }}>
                          <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
                            {r.last_modified_iso}
                          </Typography>
                          <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
                            A Sortino {fmtNum(mA.sortino_ratio, 2)} · B Sortino {fmtNum(mB.sortino_ratio, 2)}
                          </Typography>
                        </Box>
                      }
                    />
                  </ListItemButton>
                );
              })}
            </List>
          )}
        </Paper>

        {/* Right: Detail */}
        <Paper variant="outlined" sx={{ p: 2, borderRadius: 4, flex: 1 }}>
          {!selectedRun && (
            <Alert severity="info" sx={{ borderRadius: 3 }}>
              选择左侧一个 run，查看回测曲线与 history。
            </Alert>
          )}

          {selectedRun && loadingDetail && (
            <Box sx={{ py: 6, textAlign: 'center' }}>
              <CircularProgress />
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                加载回测详情...
              </Typography>
            </Box>
          )}

          {selectedRun && detail && !loadingDetail && (
            <>
              <Stack direction={{ xs: 'column', sm: 'row' }} justifyContent="space-between" alignItems={{ xs: 'flex-start', sm: 'center' }} spacing={1} sx={{ mb: 2 }}>
                <Box>
                  <Typography variant="h6" fontWeight={900}>
                    {detail.run_id}{' '}
                    <Typography component="span" variant="caption" color="text.secondary" sx={{ fontWeight: 800 }}>
                      ({detail.root})
                    </Typography>
                  </Typography>
                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
                    默认执行 ETF 代理：SPY（股）/ SHY（债）/ GLD（金）/ BIL（现金）
                  </Typography>
                  {detail.config && Object.keys(detail.config || {}).length > 0 && (
                    <>
                      <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
                        range: {String(detail.config.start || '--')} → {String(detail.config.end || '--')} · step_days:{' '}
                        {String(detail.config.step_days ?? '--')}
                      </Typography>
                      {detail.config.tickers && (
                        <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
                          tickers: {String(detail.config.tickers.stocks || 'SPY')},{String(detail.config.tickers.bonds || 'SHY')},
                          {String(detail.config.tickers.gold || 'GLD')},{String(detail.config.tickers.cash || 'BIL')}
                        </Typography>
                      )}
                    </>
                  )}
                </Box>
                <Stack direction="row" spacing={1} alignItems="center">
                  <Chip
                    label={`modes: ${Object.keys(detail.metrics || {}).join('/') || '—'}`}
                    size="small"
                    variant="outlined"
                    sx={{ fontWeight: 900 }}
                  />
                </Stack>
              </Stack>

              <Stack direction={{ xs: 'column', lg: 'row' }} spacing={1.5} sx={{ mb: 2 }}>
                <MetricsCard title="Mode A（Committee）" metrics={(detail.metrics || {}).A} />
                <MetricsCard title="Mode B（Signals）" metrics={(detail.metrics || {}).B} />
              </Stack>

              <Paper variant="outlined" sx={{ p: 2, borderRadius: 3, mb: 2 }}>
                <Typography variant="subtitle2" fontWeight={900} sx={{ mb: 1 }}>
                  Equity Curve（{mode}）
                </Typography>
                <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} alignItems="center" justifyContent="space-between">
                  <Sparkline points={equityPts} color={mode === 'A' ? '#1976d2' : '#6a1b9a'} />
                  <Box sx={{ minWidth: 220 }}>
                    <Typography variant="caption" color="text.secondary" fontWeight={800}>
                      Points
                    </Typography>
                    <Typography variant="body2" fontWeight={900}>
                      {equityPts.length}
                    </Typography>
                    <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
                      start: {equityPts[0]?.date || '--'}
                    </Typography>
                    <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
                      end: {equityPts[equityPts.length - 1]?.date || '--'}
                    </Typography>
                  </Box>
                </Stack>
              </Paper>

              <Paper variant="outlined" sx={{ p: 2, borderRadius: 3 }}>
                <Stack direction={{ xs: 'column', sm: 'row' }} justifyContent="space-between" alignItems={{ xs: 'flex-start', sm: 'center' }} spacing={1} sx={{ mb: 1 }}>
                  <Typography variant="subtitle2" fontWeight={900}>
                    History（Rebalance Timeline）
                  </Typography>
                  <Tabs
                    value={mode}
                    onChange={(_e, v) => setMode(v)}
                    variant="scrollable"
                    allowScrollButtonsMobile
                    sx={{ minHeight: 36 }}
                  >
                    <Tab value="A" label="Mode A" sx={{ minHeight: 36, fontWeight: 900 }} />
                    <Tab value="B" label="Mode B" sx={{ minHeight: 36, fontWeight: 900 }} />
                  </Tabs>
                </Stack>

                {historyRows.length === 0 ? (
                  <Alert severity="info" sx={{ borderRadius: 3 }}>
                    该 run 暂无 history_{mode}.csv（或还未生成）。
                  </Alert>
                ) : (
                  <Stack spacing={1}>
                    {historyRows.slice(0, 60).map((row, idx) => {
                      const date = String(row.date || '').slice(0, 10);
                      const equity = num(row.equity);
                      const rb = row.risk_bias;
                      const brief = String(row.brief || '').trim();
                      const alloc = row.allocation;
                      return (
                        <Accordion key={`${date}-${idx}`} variant="outlined" sx={{ borderRadius: 3 }}>
                          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} alignItems={{ xs: 'flex-start', sm: 'center' }} sx={{ width: '100%' }}>
                              <Box sx={{ minWidth: 110 }}>
                                <Typography variant="body2" fontWeight={900}>
                                  {date || '—'}
                                </Typography>
                                <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
                                  equity: {equity !== null ? equity.toFixed(3) : '--'}
                                </Typography>
                                {mode === 'B' && (
                                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
                                    risk_bias: {rb ?? '--'}
                                  </Typography>
                                )}
                              </Box>
                              <AllocationBars alloc={alloc} />
                              <Box sx={{ flex: 1 }} />
                              <Chip size="small" label={mode} sx={{ fontWeight: 900 }} />
                            </Stack>
                          </AccordionSummary>
                          <AccordionDetails>
                            {brief ? (
                              <>
                                <Typography variant="caption" color="text.secondary" fontWeight={900}>
                                  Input brief
                                </Typography>
                                <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap', mt: 0.5 }}>
                                  {brief}
                                </Typography>
                              </>
                            ) : (
                              <Typography variant="caption" color="text.secondary">
                                （无 brief 字段）
                              </Typography>
                            )}
                          </AccordionDetails>
                        </Accordion>
                      );
                    })}
                    {historyRows.length > 60 && (
                      <Typography variant="caption" color="text.secondary">
                        仅展示前 60 条 rebalance（总计 {historyRows.length}）。如需分页/搜索，我可以继续增强。
                      </Typography>
                    )}
                  </Stack>
                )}

                {detail.comparison_md && (
                  <>
                    <Divider sx={{ my: 2 }} />
                    <Accordion variant="outlined" sx={{ borderRadius: 3 }}>
                      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                        <Typography variant="subtitle2" fontWeight={900}>
                          comparison.md（A/B 对照报告）
                        </Typography>
                      </AccordionSummary>
                      <AccordionDetails>
                        <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap', fontFamily: 'ui-monospace, SFMono-Regular, Menlo, monospace' }}>
                          {detail.comparison_md}
                        </Typography>
                      </AccordionDetails>
                    </Accordion>
                  </>
                )}
              </Paper>
            </>
          )}
        </Paper>
      </Stack>
    </Box>
  );
}


