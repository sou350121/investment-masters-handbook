'use client';
import React, { useEffect, useMemo, useState } from 'react';
import { 
  TextField, 
  Card, 
  CardContent, 
  Typography, 
  Box, 
  Avatar,
  Chip, 
  InputAdornment,
  CardActionArea,
  Stack,
  Paper,
  Button,
  Snackbar,
  Alert,
  Tooltip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Divider,
  Drawer,
  IconButton,
  CircularProgress,
  Tabs,
  Tab,
  FormControlLabel,
  Switch,
  Fab
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import HelpOutlineIcon from '@mui/icons-material/HelpOutline';
import ChatIcon from '@mui/icons-material/Chat';
import CloseIcon from '@mui/icons-material/Close';
import SendIcon from '@mui/icons-material/Send';
import DescriptionIcon from '@mui/icons-material/Description';
import SaveIcon from '@mui/icons-material/Save';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import RefreshIcon from '@mui/icons-material/Refresh';
import Link from 'next/link';
import ReactMarkdown from 'react-markdown';
import { 
  Investor, 
  RagResponseItem 
} from '@/lib/imh/data';
import { getAvatarUrl } from '@/lib/imh/avatarMap';

function hashToHsl(input: string) {
  let hash = 0;
  for (let i = 0; i < input.length; i++) {
    hash = (hash * 31 + input.charCodeAt(i)) >>> 0;
  }
  const h = hash % 360;
  return `hsl(${h} 70% 45%)`;
}

function getInitials(investor: Investor) {
  const cn = (investor.chinese_name || '').trim();
  if (cn) return cn.slice(0, 1);
  const parts = (investor.full_name || '').trim().split(/\s+/).filter(Boolean);
  if (parts.length === 0) return '?';
  if (parts.length === 1) return parts[0].slice(0, 1).toUpperCase();
  return `${parts[0][0]}${parts[parts.length - 1][0]}`.toUpperCase();
}

function buildIntro(investor: Investor) {
  if (investor.intro_zh && investor.intro_zh.trim()) return investor.intro_zh.trim();
  const style = (investor.style || []).slice(0, 2).join(' / ');
  const bestFor = (investor.best_for || []).slice(0, 2).join(' / ');
  const fund = investor.fund ? `代表：${investor.fund}` : '';
  const parts = [
    style ? `风格：${style}` : '',
    bestFor ? `擅长：${bestFor}` : '',
    fund,
  ].filter(Boolean);
  return parts.join('；');
}

export default function InvestorList({ 
  investors, 
  productManual 
}: { 
  investors: Investor[], 
  productManual?: string 
}) {
  const [search, setSearch] = useState('');
  const [missingAvatar, setMissingAvatar] = useState<Record<string, boolean>>({});
  const [origin, setOrigin] = useState('');
  const [toast, setToast] = useState<{ open: boolean; text: string }>({ open: false, text: '' });
  const [routeText, setRouteText] = useState('');
  const [routeLoading, setRouteLoading] = useState(false);
  const [routeError, setRouteError] = useState<string | null>(null);
  const [routeResults, setRouteResults] = useState<
    Array<{
      investor_id: string;
      chinese_name: string;
      full_name: string;
      nationality?: string;
      fund?: string;
      intro_zh?: string;
      score: number;
      reasons: string[];
      matched_scenarios?: string[];
    }>
  >([]);

  // --- Chat Window State ---
  type EnsembleContribution = {
    investor_id: string;
    category?: string;
    weight: number;
    impact: number;
    confidence: number;
    contribution: number;
  };

  type EnsembleAdjustment = {
    final_multiplier_offset: number;
    primary_expert: string;
    conflict_detected: boolean;
    resolution: string;
    contributions?: EnsembleContribution[];
  };

  type EnsembleMetadata = {
    regime_id_inferred?: string;
    reasoning_preview?: string;
    [k: string]: any;
  };

  type SecondaryEnsembleResult = {
    experts: string[];
    expert_opinions?: Array<{
      expert: string;
      summary: string;
      impact?: number;
      confidence?: number;
      citations?: number[];
    }>;
    consensus?: string;
    conflicts?: string;
    synthesis?: string;
    citations?: any[];
    ensemble_adjustment?: EnsembleAdjustment;
    metadata?: EnsembleMetadata;
  };

  type PrimaryAllocation = {
    target_allocation: { stocks: number; bonds: number; gold: number; cash: number };
    one_liner: string;
    confidence: number;
  };

  type TieredEnsembleResult = {
    primary: PrimaryAllocation;
    secondary: SecondaryEnsembleResult;
  };

  const [chatOpen, setChatOpen] = useState(false);
  const [chatQuery, setChatQuery] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  const [chatResults, setChatResults] = useState<RagResponseItem[]>([]);
  const [ensembleMode, setEnsembleMode] = useState(false);
  const [ensembleResult, setEnsembleResult] = useState<TieredEnsembleResult | null>(null);
  const [chatError, setChatError] = useState<string | null>(null);
  const [apiToken, setApiToken] = useState<string>('');
  const [apiTokenSaved, setApiTokenSaved] = useState(false);

  type PolicyGateResponse = {
    regime: { id: string; label?: string; score: number; confidence?: number; reasons?: string[] };
    scenario: { matched?: string[]; primary?: string | null; count?: number };
    router: Array<{
      investor_id: string;
      chinese_name: string;
      full_name: string;
      score: number;
      reasons: string[];
    }>;
    rule_hits: Array<{ content: string; metadata: Record<string, any>; similarity_estimate: number }>;
    risk_overlay: { multipliers: Record<string, number>; absolute: Record<string, number> };
    explanation: { markdown?: string; json?: any };
    audit: any;
  };

  // --- Policy Gate State ---
  const [policyText, setPolicyText] = useState('');
  const [policyFeaturesJson, setPolicyFeaturesJson] = useState(
    '{\n  "vix": 18,\n  "credit_spread_bps": 180,\n  "rate_change_3m_bps": 25,\n  "inflation_yoy": 0.03,\n  "breadth_pct_up": 0.55,\n  "realized_vol_20d": 0.22\n}',
  );
  const [policyPortfolioJson, setPolicyPortfolioJson] = useState(
    '{\n  "leverage": 1.0,\n  "cash": 0.12,\n  "drawdown_pct": 0.05,\n  "turnover_30d": 0.20\n}',
  );
  const [policyConstraintsJson, setPolicyConstraintsJson] = useState(
    '{\n  "max_leverage": 1.5,\n  "min_cash": 0.08\n}',
  );
  const [policyLoading, setPolicyLoading] = useState(false);
  const [policyError, setPolicyError] = useState<string | null>(null);
  const [policyResult, setPolicyResult] = useState<PolicyGateResponse | null>(null);
  const [scenarios, setScenarios] = useState<any[]>([]);
  const [selectedScenarioId, setSelectedScenarioId] = useState<string | null>(null);
  const [validationReport, setValidationReport] = useState<{ passed: boolean; details: string[] } | null>(null);
  const [batchReport, setBatchReport] = useState<any | null>(null);
  const [batchLoading, setBatchLoading] = useState(false);
  const [scenarioLoadError, setScenarioLoadError] = useState<string | null>(null);
  const [scenarioQuery, setScenarioQuery] = useState('');
  const [scenarioTag, setScenarioTag] = useState<string>('all');
  const [tabValue, setTabValue] = useState(0);

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const scenarioTags = useMemo(() => {
    const set = new Set<string>();
    for (const s of scenarios || []) {
      const tags = (s?.tags || []) as any[];
      for (const t of tags) if (typeof t === 'string' && t.trim()) set.add(t.trim());
    }
    return ['all', ...Array.from(set).sort()];
  }, [scenarios]);

  const filteredScenarios = useMemo(() => {
    const q = scenarioQuery.trim().toLowerCase();
    return (scenarios || []).filter((s) => {
      const tags = (s?.tags || []) as any[];
      const tagOk = scenarioTag === 'all' ? true : tags.includes(scenarioTag);
      if (!tagOk) return false;
      if (!q) return true;
      const text = `${s?.id || ''} ${s?.label || ''} ${s?.description || ''}`.toLowerCase();
      return text.includes(q);
    });
  }, [scenarios, scenarioQuery, scenarioTag]);

  const loadScenarios = () => {
    setScenarioLoadError(null);
    fetch('/api/policy/scenarios')
      .then(async (r) => {
        if (!r.ok) {
          const body = await r.text().catch(() => '');
          throw new Error(`GET /api/policy/scenarios 失败（HTTP ${r.status}）${body ? `: ${body}` : ''}`);
        }
        return r.json();
      })
      .then(data => setScenarios(data.scenarios || []))
      .catch(err => {
        const msg = err?.message || '加载场景失败';
        setScenarioLoadError(msg);
        console.error('Failed to load scenarios', err);
      });
  };

  useEffect(() => {
    loadScenarios();
  }, []);

  async function handleValidateAll() {
    setBatchLoading(true);
    setBatchReport(null);
    try {
      const resp = await fetch('/api/policy/validate_all', { method: 'POST' });
      if (!resp.ok) {
        const body = await resp.text().catch(() => '');
        throw new Error(`批量验证失败（POST /api/policy/validate_all，HTTP ${resp.status}）${body ? `: ${body}` : ''}`);
      }
      const data = await resp.json();
      setBatchReport(data);
    } catch (e: any) {
      setToast({ open: true, text: e.message });
    } finally {
      setBatchLoading(false);
    }
  }

  async function handleSaveCurrentScenario() {
    if (!selectedScenarioId) return;
    try {
      const current = scenarios.find(s => s.id === selectedScenarioId);
      if (!current) return;

      const updatedScenarios = scenarios.map(s => {
        if (s.id === selectedScenarioId) {
          return {
            ...s,
            description: policyText,
            features: JSON.parse(policyFeaturesJson || '{}'),
            portfolio_state: JSON.parse(policyPortfolioJson || '{}'),
          };
        }
        return s;
      });

      const resp = await fetch('/api/policy/scenarios', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ scenarios: updatedScenarios }),
      });
      if (!resp.ok) throw new Error('保存失败');
      setScenarios(updatedScenarios);
      setToast({ open: true, text: '场景已保存至本地 config/scenarios.yaml' });
    } catch (e: any) {
      setToast({ open: true, text: `保存失败: ${e.message}` });
    }
  }

  async function handlePolicyGate() {
    const text = policyText.trim();
    if (!text) {
      setToast({ open: true, text: '请先输入市场观察/交易想法（Policy Gate 的 text）' });
      return;
    }

    let features: any = {};
    let portfolio_state: any = {};
    let constraints: any = {};

    try {
      features = policyFeaturesJson.trim() ? JSON.parse(policyFeaturesJson) : {};
    } catch {
      setPolicyError('features JSON 解析失败');
      return;
    }

    try {
      portfolio_state = policyPortfolioJson.trim() ? JSON.parse(policyPortfolioJson) : {};
    } catch {
      setPolicyError('portfolio_state JSON 解析失败');
      return;
    }

    try {
      constraints = policyConstraintsJson.trim() ? JSON.parse(policyConstraintsJson) : {};
    } catch {
      setPolicyError('constraints JSON 解析失败');
      return;
    }

    setPolicyLoading(true);
    setPolicyError(null);
    setPolicyResult(null);
    setValidationReport(null);

    try {
      const resp = await fetch('/api/policy/gate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text,
          features,
          portfolio_state,
          constraints,
          top_k_router: 5,
          top_k_rule_hits: 8,
        }),
      });

      if (!resp.ok) {
        const err = await resp.json().catch(() => ({}));
        throw new Error(err.detail || err.error || 'Policy Gate 请求失败');
      }

      const data = (await resp.json()) as PolicyGateResponse;
      setPolicyResult(data);

      // Run validation if a scenario is selected
      if (selectedScenarioId) {
        const scenario = scenarios.find(s => s.id === selectedScenarioId);
        if (scenario && scenario.expectations) {
          const report: string[] = [];
          let allPassed = true;

          const check = (key: string, actual: number | undefined, expect: any) => {
            const { op, value, tol } = expect || {};
            const opStr = String(op || '').trim();
            const expected = Number(value);
            const t = tol !== undefined ? Number(tol) : 0.05;

            if (actual === undefined || Number.isNaN(actual)) {
              report.push(`❌ ${key}: 预期 ${opStr} ${expected}, 但输出中未找到该指标`);
              allPassed = false;
              return;
            }

            let passed = false;
            if (opStr === '<=') passed = actual <= expected;
            else if (opStr === '>=') passed = actual >= expected;
            else if (opStr === '<') passed = actual < expected;
            else if (opStr === '>') passed = actual > expected;
            else if (opStr === '==') passed = actual === expected;
            else if (opStr === '!=') passed = actual !== expected;
            else if (opStr === '~' || opStr === '≈' || opStr === 'approx') passed = Math.abs(actual - expected) <= t;

            if (passed) {
              if (opStr === '~' || opStr === '≈' || opStr === 'approx') {
                report.push(`✅ ${key}: 预期 ${opStr} ${expected} ± ${t}, 实际 ${actual}`);
              } else {
                report.push(`✅ ${key}: 预期 ${opStr} ${expected}, 实际 ${actual}`);
              }
            } else {
              if (opStr === '~' || opStr === '≈' || opStr === 'approx') {
                report.push(`❌ ${key}: 预期 ${opStr} ${expected} ± ${t}, 实际 ${actual}`);
              } else {
                report.push(`❌ ${key}: 预期 ${opStr} ${expected}, 实际 ${actual}`);
              }
              allPassed = false;
            }
          };

          for (const [key, expect] of Object.entries(scenario.expectations)) {
            const exp: any = expect || {};
            const scope = String(exp.scope || '').toLowerCase(); // multipliers | absolute | ''
            let actualVal: number | undefined;
            if (scope === 'multipliers') actualVal = data.risk_overlay.multipliers[key];
            else if (scope === 'absolute') actualVal = data.risk_overlay.absolute[key];
            else {
              // Default: risk_multiplier is a multiplier; others are absolute guardrails.
              actualVal =
                key === 'risk_multiplier'
                  ? data.risk_overlay.multipliers[key]
                  : (data.risk_overlay.absolute[key] ?? data.risk_overlay.multipliers[key]);
            }
            check(key, actualVal, exp);
          }
          setValidationReport({ passed: allPassed, details: report });
        }
      }
    } catch (e: any) {
      setPolicyError(e?.message || 'Policy Gate 请求失败');
    } finally {
      setPolicyLoading(false);
    }
  }

  const questionCategories = [
    {
      title: '选股决策 (Stock Selection)',
      questions: [
        '护城河怎么评估？',
        '这家公司有没有定价权？',
        '成长股现在贵不贵？',
        'PEG 多少算合理？',
        '现在是不是安全边际足够？',
        '这算被错杀吗？',
        '这是价值陷阱吗？',
        '基建类资产适合长期持有吗？',
        '这块地段值不值？',
        '什么是二流生意？',
        '如何看管理层的资本分配能力？',
        '周期性公司的买入时点？',
      ],
    },
    {
      title: '宏观择时 (Macro & Timing)',
      questions: [
        '现在处在经济周期哪个阶段？',
        '增长和通胀怎么组合判断？',
        '债务周期在什么位置？',
        '最近有什么法案会影响股市？',
        '现在市场在炒什么叙事？',
        '什么是反身性？',
        '通胀会不会继续上升？',
        '流动性在收紧还是放松？',
        '加息周期到头了吗？',
        '滞胀时期买什么？',
        '黄金和比特币的逻辑差异？',
        '政府赤字对长端利率的影响？',
      ],
    },
    {
      title: '风险检查 (Risk Check)',
      questions: [
        '我是不是在 FOMO？',
        '怎么用清单避免低级错误？',
        '现在该进攻还是防守？',
        '这是不是泡沫？',
        '我的决策过程靠谱吗？',
        '要不要止损？',
        '止损点怎么设？',
        '如何识别会计造假？',
        '如何对冲地缘政治风险？',
        '反向思维（Invert）的实战应用？',
      ],
    },
    {
      title: '组合配置 (Portfolio)',
      questions: [
        '我该怎么做大类资产配置？',
        '股债黄金现金怎么配？',
        '什么是风险平价？',
        '我应该集中下注还是分散？',
        '我该留多少现金？',
        '仓位怎么配？',
        '我该不该用杠杆？',
        '如何构建“全天候”策略？',
        '流动性危机时的仓位管理？',
        '年轻人的第一笔投资建议？',
      ],
    },
  ];

  async function handleChatQuery(queryOverride?: string) {
    const q = (queryOverride || chatQuery).trim();
    if (!q) return;
    setChatLoading(true);
    setChatError(null);
    setChatResults([]);
    setEnsembleResult(null);
    try {
      const localToken =
        typeof window !== 'undefined' ? (window.localStorage.getItem('imh_api_token') || '').trim() : '';
      const headers: Record<string, string> = { 'Content-Type': 'application/json' };
      if (ensembleMode && localToken) headers.Authorization = `Bearer ${localToken}`;

      const resp = await fetch(ensembleMode ? '/api/rag/ensemble' : '/api/rag/query', {
        method: 'POST',
        headers,
        body: ensembleMode ? JSON.stringify({ query: q }) : JSON.stringify({ query: q, top_k: 8 }),
      });
      if (!resp.ok) {
        const detail = await resp.text().catch(() => '');
        throw new Error(
          `对话请求失败 (HTTP ${resp.status})${detail ? `: ${detail}` : ''}${
            ensembleMode && !localToken ? '（提示：深度会诊需要在右侧输入 Token 并保存）' : ''
          }`,
        );
      }
      const data = await resp.json();
      if (ensembleMode) setEnsembleResult(data);
      else setChatResults(data);
    } catch (e: any) {
      setChatError(e.message || '搜索失败');
    } finally {
      setChatLoading(false);
    }
  }

  useEffect(() => {
    if (typeof window !== 'undefined') setOrigin(window.location.origin);
  }, []);

  // NOFX-style frontend token login: store Bearer token in localStorage (client-only)
  useEffect(() => {
    if (typeof window === 'undefined') return;
    try {
      const saved = window.localStorage.getItem('imh_api_token') || '';
      if (saved) setApiToken(saved);
    } catch {
      // ignore
    }
  }, []);

  const saveApiToken = () => {
    if (typeof window === 'undefined') return;
    const trimmed = apiToken.trim();
    // Prevent common confusion: OpenRouter keys typically look like "sk-or-..."
    if (trimmed.startsWith('sk-or-')) {
      setToast({
        open: true,
        text: '检测到你粘贴的是 OpenRouter Key（sk-or-...）。这里是 IMH_API_TOKEN（接口口令），不要放 LLM Key。',
      });
      return;
    }
    try {
      window.localStorage.setItem('imh_api_token', trimmed);
      setApiTokenSaved(true);
      setToast({ open: true, text: 'Token 已保存（仅本机浏览器）' });
      setTimeout(() => setApiTokenSaved(false), 1500);
    } catch {
      setToast({ open: true, text: '保存 Token 失败（浏览器禁止 localStorage？）' });
    }
  };

  const clearApiToken = () => {
    if (typeof window === 'undefined') return;
    try {
      window.localStorage.removeItem('imh_api_token');
    } catch {
      // ignore
    }
    setApiToken('');
    setToast({ open: true, text: 'Token 已清除' });
  };

  const api = useMemo(() => {
    const base = origin || '';
    return {
      health: `${base}/health`,
      query: `${base}/api/rag/query`,
      queryImh: `${base}/imh/api/rag/query`,
      route: `${base}/api/route`,
    };
  }, [origin]);

  const exampleBody = useMemo(
    () => `{"query":"护城河","top_k":3,"investor_id":"warren_buffett"}`,
    [],
  );
  const exampleCurl = useMemo(
    () =>
      `curl -s -X POST "${api.query}" -H "Content-Type: application/json" -d '${exampleBody}'`,
    [api.query, exampleBody],
  );
  const exampleCurlImh = useMemo(
    () =>
      `curl -s -X POST "${api.queryImh}" -H "Content-Type: application/json" -d '${exampleBody}'`,
    [api.queryImh, exampleBody],
  );

  async function copy(text: string) {
    try {
      await navigator.clipboard.writeText(text);
      setToast({ open: true, text: '已复制到剪贴板' });
    } catch {
      setToast({ open: true, text: '复制失败（浏览器权限限制）' });
    }
  }

  async function handleRoute() {
    const text = routeText.trim();
    if (!text) {
      setToast({ open: true, text: '请先粘贴/输入今天的股票信息' });
      return;
    }
    setRouteLoading(true);
    setRouteError(null);
    try {
      const resp = await fetch('/api/route', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, top_k: 5 }),
      });
      if (!resp.ok) {
        const err = await resp.json().catch(() => ({}));
        throw new Error(err.detail || err.error || '路由失败');
      }
      const data = await resp.json();
      setRouteResults(Array.isArray(data) ? data : []);
    } catch (e: any) {
      setRouteError(e?.message || '路由失败');
      setRouteResults([]);
    } finally {
      setRouteLoading(false);
    }
  }

  const filtered = investors.filter(i => 
    i.full_name.toLowerCase().includes(search.toLowerCase()) ||
    i.chinese_name.includes(search) ||
    i.style.some(s => s.toLowerCase().includes(search.toLowerCase())) ||
    i.best_for.some(b => b.toLowerCase().includes(search.toLowerCase()))
  );

  return (
    <Box sx={{ maxWidth: 1200, mx: 'auto', p: { xs: 2, sm: 4 } }}>
      {/* --- Sticky Header with Tabs --- */}
      <Paper 
        elevation={0}
        sx={{ 
          position: 'sticky', 
          top: 0, 
          zIndex: 1000, 
          bgcolor: 'rgba(255, 255, 255, 0.95)', 
          backdropFilter: 'blur(8px)',
          borderBottom: '1px solid rgba(0,0,0,0.08)',
          mb: 4,
          mx: { xs: -2, sm: -4 },
          px: { xs: 2, sm: 4 }
        }}
      >
        <Stack direction={{ xs: 'column', sm: 'row' }} justifyContent="space-between" alignItems="center">
          <Box sx={{ py: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
            <Typography variant="h6" fontWeight={900} color="primary" sx={{ letterSpacing: -0.5 }}>
              IMH
            </Typography>
            <Typography variant="caption" sx={{ color: 'text.secondary', fontWeight: 600, bgcolor: 'rgba(0,0,0,0.04)', px: 1, py: 0.5, borderRadius: 1 }}>
              v1.0
            </Typography>
          </Box>
          <Tabs value={tabValue} onChange={handleTabChange} sx={{ minHeight: 48 }}>
            <Tab label="大师列表" sx={{ fontWeight: 800, px: 3 }} />
            <Tab label="场景沙盒" sx={{ fontWeight: 800, px: 3 }} />
            <Tab label="风控护栏" sx={{ fontWeight: 800, px: 3 }} />
            <Tab label="关于手册" sx={{ fontWeight: 800, px: 3 }} />
          </Tabs>
        </Stack>
      </Paper>

      {/* --- Tab 0: Master List & Search --- */}
      {tabValue === 0 && (
        <Box>
          <Box sx={{ mb: 6, textAlign: 'center' }}>
            <Typography variant="h3" component="h1" gutterBottom fontWeight={900} color="primary" sx={{ letterSpacing: -1 }}>
              Investment Masters Handbook
            </Typography>
            <Typography variant="h6" color="text.secondary" gutterBottom sx={{ maxWidth: 600, mx: 'auto', opacity: 0.8 }}>
              复现 17 位投资传奇的决策大脑，为你的投资组合保驾护航
            </Typography>
            
            <Box sx={{ mt: 5, display: 'flex', justifyContent: 'center' }}>
              <TextField
                fullWidth
                sx={{ 
                  maxWidth: 700,
                  '& .MuiOutlinedInput-root': {
                    borderRadius: 4,
                    bgcolor: 'background.paper',
                    boxShadow: '0 4px 20px rgba(0,0,0,0.05)',
                    '& fieldset': { borderColor: 'rgba(0,0,0,0.1)' },
                  }
                }}
                placeholder="搜索大师姓名、投资风格（如：价值、成长）或擅长领域（如：消费、科技）..."
                variant="outlined"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <SearchIcon color="primary" />
                    </InputAdornment>
                  ),
                }}
              />
            </Box>
          </Box>

          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', md: '1fr 1fr 1fr' }, gap: 3, mb: 8 }}>
            {filtered.map((investor) => (
              <Card 
                key={investor.id} 
                variant="outlined"
                sx={{ 
                  borderRadius: 4, 
                  transition: 'all 0.2s',
                  '&:hover': { 
                    transform: 'translateY(-4px)',
                    boxShadow: '0 12px 24px rgba(0,0,0,0.1)',
                    borderColor: 'primary.main'
                  }
                }}
              >
                <Link href={`/investors/${investor.id}`} style={{ textDecoration: 'none', color: 'inherit' }}>
                  <CardActionArea sx={{ p: 2 }}>
                    <Stack direction="row" spacing={2} alignItems="center" sx={{ mb: 2 }}>
                      {(() => {
                        const avatarUrl = getAvatarUrl(investor);
                        const src =
                          avatarUrl && !missingAvatar[investor.id] ? avatarUrl : undefined;
                        return (
                          <Avatar
                            src={src}
                            imgProps={{
                              onError: () =>
                                setMissingAvatar((prev) => ({
                                  ...prev,
                                  [investor.id]: true,
                                })),
                            }}
                            sx={{ 
                              width: 64, 
                              height: 64, 
                              bgcolor: hashToHsl(investor.id),
                              fontSize: 24,
                              fontWeight: 800,
                              boxShadow: '0 4px 10px rgba(0,0,0,0.1)'
                            }}
                          >
                            {getInitials(investor)}
                          </Avatar>
                        );
                      })()}
                      <Box>
                        <Typography variant="h6" fontWeight={900}>
                          {investor.chinese_name || investor.full_name}
                        </Typography>
                        <Typography variant="caption" color="text.secondary" sx={{ display: 'block', fontWeight: 600 }}>
                          {investor.fund || investor.nationality || 'Legendary Investor'}
                        </Typography>
                      </Box>
                    </Stack>
                    
                    <Typography variant="body2" color="text.secondary" sx={{ 
                      height: 48, 
                      overflow: 'hidden', 
                      display: '-webkit-box', 
                      WebkitLineClamp: 2, 
                      WebkitBoxOrient: 'vertical',
                      mb: 2,
                      lineHeight: 1.6
                    }}>
                      {buildIntro(investor)}
                    </Typography>

                    <Stack direction="row" flexWrap="wrap" gap={0.5}>
                      {(investor.style || []).map((s) => (
                        <Chip key={s} label={s} size="small" variant="outlined" sx={{ borderRadius: 1.5, fontWeight: 700, fontSize: 10 }} />
                      ))}
                    </Stack>
                  </CardActionArea>
                </Link>
              </Card>
            ))}
          </Box>

          <Box id="master-questions" sx={{ mb: 6 }}>
            <Typography variant="h6" fontWeight={800} sx={{ mb: 2, textAlign: 'center' }}>
              🎯 大师题库：你可以这样问
            </Typography>
            <Box
              sx={{
                display: 'grid',
                gap: 2,
                gridTemplateColumns: {
                  xs: '1fr',
                  sm: 'repeat(2, 1fr)',
                  md: 'repeat(4, 1fr)',
                },
              }}
            >
              {questionCategories.map((cat) => (
                <Paper
                  key={cat.title}
                  variant="outlined"
                  sx={{
                    p: 2,
                    borderRadius: 3,
                    bgcolor: 'background.paper',
                    height: '100%',
                  }}
                >
                  <Typography variant="subtitle2" fontWeight={800} color="primary" gutterBottom>
                    {cat.title}
                  </Typography>
                  <Stack spacing={0.5}>
                    {cat.questions.map((q) => (
                      <Typography
                        key={q}
                        variant="caption"
                        sx={{
                          cursor: 'pointer',
                          p: 0.5,
                          borderRadius: 1,
                          '&:hover': { bgcolor: 'rgba(2,6,23,0.04)', color: 'primary.main' },
                        }}
                        onClick={() => {
                          setChatQuery(q);
                          setChatOpen(true);
                          handleChatQuery(q);
                        }}
                      >
                        • {q}
                      </Typography>
                    ))}
                  </Stack>
                </Paper>
              ))}
            </Box>
          </Box>

          {/* Quick Route Section moved inside Tab 0 for better visibility */}
          <Box sx={{ mt: 4, mb: 8 }}>
            <Accordion variant="outlined" sx={{ borderRadius: 4, borderColor: 'rgba(0,0,0,0.1)' }}>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography fontWeight={800}>快速路由：贴入股票信息，推荐该问谁</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <TextField
                  fullWidth
                  multiline
                  minRows={3}
                  placeholder="示例：今天AAPL涨5%，成交放大。我担心估值太贵且市场过热，该追吗？"
                  value={routeText}
                  onChange={(e) => setRouteText(e.target.value)}
                  sx={{ mb: 2 }}
                />
                <Button variant="contained" onClick={handleRoute} disabled={routeLoading}>
                  {routeLoading ? '推荐中...' : '开始推荐'}
                </Button>
                {routeResults.length > 0 && (
                  <Stack spacing={1} sx={{ mt: 2 }}>
                    {routeResults.map((r) => (
                      <Paper key={r.investor_id} variant="outlined" sx={{ p: 1.5, borderRadius: 2 }}>
                        <Typography variant="body2" fontWeight={800}>{r.chinese_name}（{r.investor_id}）</Typography>
                        <Typography variant="caption" color="text.secondary">{r.reasons.join('；')}</Typography>
                      </Paper>
                    ))}
                  </Stack>
                )}
              </AccordionDetails>
            </Accordion>
          </Box>
        </Box>
      )}

      {/* --- Tab 1: Scenario Sandbox --- */}
      {tabValue === 1 && (
        <Box sx={{ maxWidth: 900, mx: 'auto' }}>
          <Typography variant="h4" fontWeight={900} gutterBottom sx={{ mb: 3 }}>
            🚀 场景沙盒 <Typography component="span" variant="h6" color="text.secondary">(Scenario Sandbox)</Typography>
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
            模拟经典历史行情（如 2008 金融危机、2020 疫情闪崩），验证当前护栏逻辑在极端压力下的表现。
          </Typography>

          <Paper variant="outlined" sx={{ p: 4, borderRadius: 5, bgcolor: 'rgba(25, 118, 210, 0.02)', mb: 4 }}>
            <Stack direction={{ xs: 'column', sm: 'row' }} justifyContent="space-between" alignItems="flex-start" sx={{ mb: 3 }} spacing={2}>
              <Box>
                <Typography variant="subtitle1" fontWeight={900} color="primary">
                  回归测试 (Regression Scorecard)
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  对比 actual 输出与 scenarios.yaml 中的 expectations
                </Typography>
              </Box>
              <Stack direction="row" spacing={1}>
                <Button 
                  variant="outlined" 
                  startIcon={<RefreshIcon />} 
                  onClick={loadScenarios}
                  disabled={batchLoading}
                >
                  刷新场景
                </Button>
                <Button 
                  variant="contained" 
                  startIcon={<PlayArrowIcon />} 
                  onClick={handleValidateAll}
                  disabled={batchLoading}
                  sx={{ borderRadius: 2, fontWeight: 800 }}
                >
                  {batchLoading ? '全量回归运行中...' : '运行全量回归 (Run All Scenarios)'}
                </Button>
              </Stack>
            </Stack>

            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} sx={{ mb: 3 }}>
              <TextField
                size="small"
                fullWidth
                placeholder="搜索场景（按名称、标签或描述）..."
                value={scenarioQuery}
                onChange={(e) => setScenarioQuery(e.target.value)}
                InputProps={{ startAdornment: <InputAdornment position="start"><SearchIcon fontSize="small" /></InputAdornment> }}
              />
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                {scenarioTags.map((t) => (
                  <Chip
                    key={t}
                    label={t}
                    size="small"
                    clickable
                    color={scenarioTag === t ? 'primary' : 'default'}
                    onClick={() => setScenarioTag(t)}
                    sx={{ fontWeight: 700 }}
                  />
                ))}
              </Box>
            </Stack>

            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1.5 }}>
              {filteredScenarios.map((s) => {
                const expKeys = Object.keys(s?.expectations || {});
                return (
                  <Tooltip 
                    key={s.id} 
                    title={
                      <Box sx={{ p: 0.5 }}>
                        <Typography variant="caption" fontWeight={800} sx={{ display: 'block', mb: 0.5 }}>{s.label}</Typography>
                        <Typography variant="caption" sx={{ display: 'block', mb: 1, opacity: 0.8 }}>{s.description}</Typography>
                        <Typography variant="caption" fontWeight={700}>期望指标：</Typography>
                        <Typography variant="caption" sx={{ display: 'block' }}>{expKeys.join(', ')}</Typography>
                      </Box>
                    }
                  >
                    <Chip
                      label={s.label}
                      clickable
                      onClick={() => {
                        setSelectedScenarioId(s.id);
                        setPolicyText(s.description);
                        setPolicyFeaturesJson(JSON.stringify(s.features, null, 2));
                        setPolicyPortfolioJson(JSON.stringify(s.portfolio_state || {}, null, 2));
                        setTabValue(2); // Jump to Policy Gate for manual run
                      }}
                      variant="outlined"
                      sx={{ 
                        borderRadius: 2, 
                        py: 2.5, 
                        px: 1,
                        fontWeight: 800,
                        borderColor: selectedScenarioId === s.id ? 'primary.main' : 'rgba(0,0,0,0.1)',
                        bgcolor: selectedScenarioId === s.id ? 'rgba(25, 118, 210, 0.08)' : 'transparent'
                      }}
                    />
                  </Tooltip>
                );
              })}
            </Box>
          </Paper>

          {batchReport && (
            <Paper variant="outlined" sx={{ p: 3, borderRadius: 4, border: '1px solid rgba(0,0,0,0.1)' }}>
              <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
                <Typography variant="subtitle1" fontWeight={900}>
                  验证结果统计：{batchReport.passed_count} / {batchReport.total} 通过
                </Typography>
                <IconButton size="small" onClick={() => setBatchReport(null)}><CloseIcon /></IconButton>
              </Stack>
              <Stack spacing={1}>
                {(batchReport.items || []).map((item: any, idx: number) => (
                  <Box key={idx} sx={{ p: 1.5, borderRadius: 2, bgcolor: item.passed ? 'rgba(76, 175, 80, 0.05)' : 'rgba(244, 67, 54, 0.05)', border: '1px solid', borderColor: item.passed ? 'rgba(76, 175, 80, 0.1)' : 'rgba(244, 67, 54, 0.1)' }}>
                    <Stack direction="row" justifyContent="space-between">
                      <Typography variant="body2" fontWeight={800}>{item.label}</Typography>
                      <Typography variant="body2" color={item.passed ? 'success.main' : 'error.main'} fontWeight={900}>
                        {item.passed ? 'PASS ✅' : 'FAIL ❌'}
                      </Typography>
                    </Stack>
                    <Box sx={{ mt: 1 }}>
                      {(item.details || []).map((d: string, dIdx: number) => (
                        <Typography key={dIdx} variant="caption" color="text.secondary" sx={{ display: 'block', fontSize: 10 }}>
                          {d}
                        </Typography>
                      ))}
                    </Box>
                  </Box>
                ))}
              </Stack>
            </Paper>
          )}
        </Box>
      )}

      {/* --- Tab 2: Policy Gate Debugger --- */}
      {tabValue === 2 && (
        <Box sx={{ maxWidth: 900, mx: 'auto' }}>
          <Typography variant="h4" fontWeight={900} gutterBottom sx={{ mb: 1 }}>
            🛡️ 风险护栏 <Typography component="span" variant="h6" color="text.secondary">(Policy Gate)</Typography>
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
            手动调节市场特征 (Features) 与组合状态 (Portfolio State)，获取实时的 Risk Overlay。
          </Typography>
          
          {selectedScenarioId && (
            <Alert severity="info" sx={{ mb: 3, borderRadius: 3 }} action={<Button color="inherit" size="small" onClick={() => setSelectedScenarioId(null)}>取消加载</Button>}>
              当前加载场景：<strong>{scenarios.find(s => s.id === selectedScenarioId)?.label}</strong>
            </Alert>
          )}

          <Card variant="outlined" sx={{ borderRadius: 5, overflow: 'visible' }}>
            <CardContent sx={{ p: 4 }}>
              <Stack spacing={3}>
                <Box>
                  <Typography variant="subtitle2" fontWeight={900} gutterBottom>
                    1. 市场环境描述 (Context)
                  </Typography>
                  <TextField
                    fullWidth
                    multiline
                    rows={2}
                    placeholder="例如：市场恐慌加剧，VIX 飙升至 40 以上，信用利差迅速走阔..."
                    value={policyText}
                    onChange={(e) => setPolicyText(e.target.value)}
                  />
                </Box>

                <Stack direction={{ xs: 'column', md: 'row' }} spacing={3}>
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="subtitle2" fontWeight={900} gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      2. 特征向量 (Features JSON)
                      <Tooltip title="输入当前的市场指标，如 vix, cpi, yield_curve 等">
                        <HelpOutlineIcon sx={{ fontSize: 16, color: 'text.secondary' }} />
                      </Tooltip>
                    </Typography>
                    <TextField
                      fullWidth
                      multiline
                      rows={6}
                      value={policyFeaturesJson}
                      onChange={(e) => setPolicyFeaturesJson(e.target.value)}
                      sx={{ fontFamily: 'monospace' }}
                    />
                  </Box>
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="subtitle2" fontWeight={900} gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      3. 组合状态 (Portfolio JSON)
                      <Tooltip title="输入当前的组合状态，如 cash, leverage, drawdown_pct">
                        <HelpOutlineIcon sx={{ fontSize: 16, color: 'text.secondary' }} />
                      </Tooltip>
                    </Typography>
                    <TextField
                      fullWidth
                      multiline
                      rows={6}
                      value={policyPortfolioJson}
                      onChange={(e) => setPolicyPortfolioJson(e.target.value)}
                      sx={{ fontFamily: 'monospace' }}
                    />
                  </Box>
                </Stack>

                <Button
                  fullWidth
                  variant="contained"
                  size="large"
                  onClick={handlePolicyGate}
                  disabled={policyLoading}
                  startIcon={policyLoading ? <CircularProgress size={20} /> : <PlayArrowIcon />}
                  sx={{ py: 2, borderRadius: 3, fontWeight: 900, fontSize: 18 }}
                >
                  {policyLoading ? '计算中...' : '生成 Policy Gate 护栏'}
                </Button>

                {validationReport && (
                  <Paper variant="outlined" sx={{ p: 2, borderRadius: 3, bgcolor: validationReport.passed ? 'rgba(76, 175, 80, 0.05)' : 'rgba(244, 67, 54, 0.05)', borderColor: validationReport.passed ? 'success.main' : 'error.main' }}>
                    <Typography variant="subtitle2" fontWeight={800} color={validationReport.passed ? 'success.main' : 'error.main'}>
                      场景验证：{validationReport.passed ? '通过 ✅' : '不符合预期 ❌'}
                    </Typography>
                    {(validationReport.details || []).map((d, i) => (
                      <Typography key={i} variant="caption" sx={{ display: 'block', mt: 0.5 }}>{d}</Typography>
                    ))}
                  </Paper>
                )}

                {policyResult && (
                  <Box sx={{ mt: 2 }}>
                    <Typography variant="subtitle2" fontWeight={900} gutterBottom>
                      4. 计算结果 (Risk Overlay)
                    </Typography>
                    <Paper 
                      variant="outlined" 
                      sx={{ 
                        p: 3, 
                        borderRadius: 4, 
                        bgcolor: 'rgba(0,0,0,0.02)',
                        border: '1px solid rgba(0,0,0,0.1)'
                      }}
                    >
                      <Stack direction="row" spacing={4} sx={{ mb: 3 }}>
                        <Box>
                          <Typography variant="caption" color="text.secondary" fontWeight={800}>REGIME</Typography>
                          <Typography variant="h6" fontWeight={900} color="primary">{policyResult.regime?.label}</Typography>
                          <Typography variant="caption" sx={{ opacity: 0.7 }}>Confidence: {((policyResult.regime?.confidence || 0) * 100).toFixed(0)}%</Typography>
                        </Box>
                        <Box>
                          <Typography variant="caption" color="text.secondary" fontWeight={800}>RISK MULTIPLIER</Typography>
                          <Typography variant="h4" fontWeight={900} color={(policyResult.risk_overlay?.multipliers?.risk_multiplier || 1) < 1 ? 'warning.main' : 'success.main'}>
                            {(policyResult.risk_overlay?.multipliers?.risk_multiplier || 1).toFixed(2)}x
                          </Typography>
                        </Box>
                      </Stack>
                      
                      <Divider sx={{ mb: 2 }} />
                      
                      <Typography variant="caption" color="text.secondary" fontWeight={800} sx={{ display: 'block', mb: 1 }}>ABSOLUTE GUARDRAILS</Typography>
                      <Stack direction="row" spacing={1} flexWrap="wrap" gap={1}>
                        {Object.entries(policyResult.risk_overlay?.absolute || {}).map(([k, v]: [string, any]) => (
                          <Chip 
                            key={k} 
                            label={`${k}: ${typeof v === 'number' ? v.toFixed(2) : v}`} 
                            variant="filled" 
                            size="small" 
                            sx={{ fontWeight: 800, bgcolor: 'background.paper' }} 
                          />
                        ))}
                      </Stack>
                    </Paper>
                  </Box>
                )}
              </Stack>
            </CardContent>
          </Card>
        </Box>
      )}

      {/* --- Tab 3: About & Product Manual --- */}
      {tabValue === 3 && (
        <Box sx={{ maxWidth: 900, mx: 'auto' }}>
           <Typography variant="h4" fontWeight={900} gutterBottom sx={{ mb: 4 }}>
            📖 手册与 API 说明
          </Typography>

          <Stack spacing={4}>
            <Box>
              <Typography variant="h6" fontWeight={900} gutterBottom color="primary">
                大师决策委员会 (IC Engine)
              </Typography>
              <Paper variant="outlined" sx={{ p: 3, borderRadius: 5, bgcolor: 'rgba(25, 118, 210, 0.03)', border: '2px dashed rgba(25, 118, 210, 0.2)' }}>
                <Typography variant="body2" sx={{ mb: 2, color: 'text.secondary', fontWeight: 600 }}>
                  通过模拟巴菲特、达利奥、索罗斯等大师的逻辑冲突，系统自动合成定量风险建议。
                </Typography>
                <Button 
                  variant="contained" 
                  fullWidth 
                  startIcon={<ChatIcon />}
                  onClick={() => setChatOpen(true)}
                  sx={{ py: 2, borderRadius: 3, fontWeight: 900, fontSize: 16 }}
                >
                  开启大师深度会诊 (Open IC Engine)
                </Button>
              </Paper>
            </Box>

            <Box>
              <Typography variant="h6" fontWeight={900} gutterBottom color="primary">
                核心产品说明书
              </Typography>
              <Paper variant="outlined" sx={{ p: 4, borderRadius: 5, maxHeight: '70vh', overflowY: 'auto' }}>
                <Box sx={{ 
                  '& h1, & h2, & h3': { mt: 3, mb: 1.5, fontWeight: 800, color: 'primary.main' },
                  '& p': { mb: 1.5, lineHeight: 1.7 },
                  '& code': { bgcolor: 'rgba(0,0,0,0.05)', px: 0.5, borderRadius: 1 }
                }}>
                  <ReactMarkdown>{productManual || '暂无说明书内容'}</ReactMarkdown>
                </Box>
              </Paper>
            </Box>

            <Box>
              <Typography variant="h6" fontWeight={900} gutterBottom color="primary">
                快速上手 (Quick Start)
              </Typography>
              <Stack direction="row" spacing={2} sx={{ mb: 2 }}>
                <Button variant="outlined" startIcon={<HelpOutlineIcon />} component="a" href="/health" target="_blank">
                  检查服务状态 (/health)
                </Button>
                <Button variant="contained" onClick={() => copy(exampleCurl)}>
                  复制 RAG API (curl)
                </Button>
              </Stack>
              <Paper variant="outlined" sx={{ p: 3, borderRadius: 4, bgcolor: 'rgba(0,0,0,0.02)', fontFamily: 'monospace', fontSize: 13 }}>
                {exampleCurl}
              </Paper>
            </Box>
          </Stack>
        </Box>
      )}

      <Snackbar
        open={toast.open}
        autoHideDuration={2500}
        onClose={() => setToast({ open: false, text: '' })}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert severity="info" variant="filled" onClose={() => setToast({ open: false, text: '' })}>
          {toast.text}
        </Alert>
      </Snackbar>

      {/* --- Global Chat Window --- */}
      <Drawer
        anchor="right"
        open={chatOpen}
        onClose={() => setChatOpen(false)}
        PaperProps={{
          sx: { width: { xs: '100%', sm: 450, md: 550 }, p: 0, display: 'flex', flexDirection: 'column' }
        }}
      >
        <Box sx={{ p: 2, borderBottom: '1px solid rgba(0,0,0,0.1)', display: 'flex', alignItems: 'center', bgcolor: 'primary.main', color: 'white' }}>
          <ChatIcon sx={{ mr: 1 }} />
          <Box sx={{ minWidth: 0 }}>
            <Typography variant="h6" fontWeight={800}>Ask All Masters (全局对话)</Typography>
            {/* Make mode switch highly visible (instead of a tiny Switch) */}
            <Stack direction="row" spacing={1} sx={{ mt: 1 }}>
              <Button
                size="small"
                variant={!ensembleMode ? 'contained' : 'outlined'}
                onClick={() => setEnsembleMode(false)}
                sx={{
                  borderRadius: 2,
                  fontWeight: 900,
                  borderColor: 'rgba(255,255,255,0.85)',
                  color: !ensembleMode ? 'primary.main' : 'rgba(255,255,255,0.95)',
                  bgcolor: !ensembleMode ? '#fff' : 'transparent',
                  '&:hover': { bgcolor: !ensembleMode ? '#fff' : 'rgba(255,255,255,0.12)' },
                }}
              >
                普通问答
              </Button>
              <Button
                size="small"
                variant={ensembleMode ? 'contained' : 'outlined'}
                onClick={() => setEnsembleMode(true)}
                sx={{
                  borderRadius: 2,
                  fontWeight: 900,
                  borderColor: 'rgba(255,255,255,0.85)',
                  color: ensembleMode ? 'primary.main' : 'rgba(255,255,255,0.95)',
                  bgcolor: ensembleMode ? '#fff' : 'transparent',
                  '&:hover': { bgcolor: ensembleMode ? '#fff' : 'rgba(255,255,255,0.12)' },
                }}
              >
                大师深度会诊
              </Button>
            </Stack>
          </Box>
          <Box sx={{ flex: 1 }} />
          <IconButton onClick={() => setChatOpen(false)} color="inherit">
            <CloseIcon />
          </IconButton>
        </Box>

        <Box sx={{ flex: 1, overflowY: 'auto', p: 2, bgcolor: 'rgba(0,0,0,0.02)' }}>
          <Alert
            severity={ensembleMode ? 'info' : 'success'}
            sx={{ mb: 2, borderRadius: 2 }}
          >
            当前模式：{ensembleMode ? '大师深度会诊（会调用 /api/rag/ensemble）' : '普通问答（会调用 /api/rag/query）'}
            {ensembleMode && (
              <Box sx={{ mt: 0.5, opacity: 0.9 }}>
                <Typography variant="caption">
                  提示：深度会诊需要设置 Token（浏览器端会用 Authorization: Bearer 发送）。
                </Typography>
              </Box>
            )}
          </Alert>

          {ensembleMode && (
            <Paper variant="outlined" sx={{ p: 1.5, borderRadius: 2, mb: 2 }}>
              <Stack direction="row" alignItems="center" spacing={0.5} sx={{ mb: 1 }}>
                <Typography variant="caption" fontWeight={900} color="text.secondary">
                  Token 登录 (NOFX 风格)
                </Typography>
                <Tooltip title="在这里填入 Access Token 或直接填入 OpenRouter/OpenAI API Key。Key 只会保存在你本地浏览器的 localStorage 中，后端不会持久化存储，非常安全。">
                  <HelpOutlineIcon sx={{ fontSize: 14, color: 'text.secondary', cursor: 'pointer' }} />
                </Tooltip>
              </Stack>
              <Stack direction="row" spacing={1} alignItems="center">
                <TextField
                  fullWidth
                  size="small"
                  type="password"
                  placeholder="Access Token 或 sk-or-..."
                  value={apiToken}
                  onChange={(e) => setApiToken(e.target.value)}
                />
                <Button
                  variant={apiTokenSaved ? 'contained' : 'outlined'}
                  onClick={saveApiToken}
                  sx={{ fontWeight: 900, flexShrink: 0 }}
                  disabled={!apiToken.trim()}
                >
                  {apiTokenSaved ? '已保存' : '保存'}
                </Button>
                <Button
                  variant="text"
                  color="inherit"
                  onClick={clearApiToken}
                  sx={{ fontWeight: 900, flexShrink: 0 }}
                >
                  清除
                </Button>
              </Stack>
              <Box sx={{ mt: 1, display: 'flex', gap: 1 }}>
                <Chip 
                  label="安全：本地存储" 
                  size="small" 
                  variant="outlined" 
                  color="success" 
                  sx={{ fontSize: 10, height: 20, fontWeight: 700 }} 
                />
                <Chip 
                  label="支持：OpenRouter" 
                  size="small" 
                  variant="outlined" 
                  color="info" 
                  sx={{ fontSize: 10, height: 20, fontWeight: 700 }} 
                />
              </Box>
            </Paper>
          )}

          {!chatResults.length && !ensembleResult && !chatLoading && !chatError && (
            <Box sx={{ textAlign: 'center', mt: 4, color: 'text.secondary' }}>
              <Typography variant="body2">
                点击题库问题，或在下方输入你想问所有投资大师的问题。
                {ensembleMode ? '（当前：大师深度会诊模式）' : ''}
              </Typography>
            </Box>
          )}

          {chatLoading && (
            <Box sx={{ textAlign: 'center', mt: 4 }}>
              <CircularProgress size={30} />
              <Typography variant="body2" sx={{ mt: 1 }}>大师们正在思考逻辑...</Typography>
            </Box>
          )}

          {chatError && (
            <Alert severity="error" sx={{ mt: 2 }}>{chatError}</Alert>
          )}

          <Stack spacing={2}>
            {ensembleResult && (
              <Card variant="outlined" sx={{ borderRadius: 2 }}>
                <CardContent sx={{ p: 2 }}>
                  {(() => {
                    const primary = ensembleResult.primary;
                    const sec = ensembleResult.secondary;
                    const alloc = primary?.target_allocation || { stocks: 0, bonds: 0, gold: 0, cash: 0 };
                    const rows = [
                      { k: 'stocks', label: '股', v: Number(alloc.stocks || 0), color: 'primary.main' },
                      { k: 'bonds', label: '债', v: Number(alloc.bonds || 0), color: 'info.main' },
                      { k: 'gold', label: '金', v: Number(alloc.gold || 0), color: 'warning.main' },
                      { k: 'cash', label: '现金', v: Number(alloc.cash || 0), color: 'success.main' },
                    ];
                    const confPct = Math.round(Math.max(0, Math.min(1, Number(primary?.confidence ?? 0))) * 100);

                    return (
                      <>
                        <Paper variant="outlined" sx={{ p: 1.5, borderRadius: 2, mb: 2 }}>
                          <Typography variant="caption" fontWeight={900} color="text.secondary">
                            一级输出：四类资产目标配比（sum=100）
                          </Typography>

                          <Typography variant="body2" fontWeight={900} sx={{ mt: 0.75 }}>
                            {primary?.one_liner || ''}
                          </Typography>
                          <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.25 }}>
                            confidence: {confPct}%
                          </Typography>

                          <Box sx={{ mt: 1.25 }}>
                            <Stack spacing={0.75}>
                              {rows.map((r) => (
                                <Box key={r.k}>
                                  <Stack direction="row" spacing={1} alignItems="center" justifyContent="space-between">
                                    <Typography variant="caption" fontWeight={900}>
                                      {r.label}
                                    </Typography>
                                    <Typography variant="caption" color="text.secondary" fontWeight={800}>
                                      {r.v}%
                                    </Typography>
                                  </Stack>
                                  <Box
                                    sx={{
                                      mt: 0.5,
                                      height: 8,
                                      borderRadius: 99,
                                      bgcolor: 'rgba(0,0,0,0.06)',
                                      overflow: 'hidden',
                                    }}
                                  >
                                    <Box
                                      sx={{
                                        height: 8,
                                        width: `${Math.max(0, Math.min(100, r.v))}%`,
                                        bgcolor: r.color,
                                      }}
                                    />
                                  </Box>
                                </Box>
                              ))}
                            </Stack>
                          </Box>
                        </Paper>

                        <Accordion variant="outlined" sx={{ borderRadius: 2 }}>
                          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                            <Typography variant="subtitle2" fontWeight={900}>
                              二级输出（证据与辩论）
                            </Typography>
                          </AccordionSummary>
                          <AccordionDetails>
                            <Typography variant="subtitle2" fontWeight={900} sx={{ mb: 1 }}>
                              参与大师
                            </Typography>
                            <Stack direction="row" spacing={1} flexWrap="wrap" gap={1} sx={{ mb: 2 }}>
                              {(sec.experts || []).map((id: string) => (
                                <Chip key={id} label={id} size="small" color="primary" sx={{ fontWeight: 800, fontSize: 11 }} />
                              ))}
                            </Stack>

                            {sec.ensemble_adjustment && (
                              <Paper variant="outlined" sx={{ p: 1.5, borderRadius: 2, mb: 2 }}>
                                <Typography variant="caption" color="text.secondary" fontWeight={800}>
                                  定量合成输出 (secondary.ensemble_adjustment)
                                </Typography>
                                <Typography variant="body2" fontWeight={900}>
                                  final_multiplier_offset: {Number(sec.ensemble_adjustment.final_multiplier_offset).toFixed(3)}
                                </Typography>
                                {sec.metadata?.regime_id_inferred && (
                                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
                                    regime_id_inferred: {String(sec.metadata.regime_id_inferred)}
                                  </Typography>
                                )}
                                <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
                                  primary_expert: {sec.ensemble_adjustment.primary_expert} · conflict_detected:{' '}
                                  {String(sec.ensemble_adjustment.conflict_detected)}
                                </Typography>
                                <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
                                  resolution: {sec.ensemble_adjustment.resolution}
                                </Typography>

                                {Array.isArray(sec.ensemble_adjustment.contributions) &&
                                  sec.ensemble_adjustment.contributions.length > 0 && (
                                    <Box sx={{ mt: 1.5 }}>
                                      <Typography
                                        variant="caption"
                                        fontWeight={900}
                                        color="text.secondary"
                                        sx={{ display: 'block', mb: 1 }}
                                      >
                                        专家贡献度（权重 × 影响）
                                      </Typography>
                                      <Stack spacing={0.75}>
                                        {sec.ensemble_adjustment.contributions.map((c, idx: number) => {
                                          const weight = Number(c.weight ?? 0);
                                          const impact = Number(c.impact ?? 0);
                                          const contribution = Number(c.contribution ?? 0);
                                          const bar = Math.min(100, Math.max(0, Math.round(Math.abs(contribution) * 120)));
                                          return (
                                            <Paper key={idx} variant="outlined" sx={{ p: 1, borderRadius: 2 }}>
                                              <Stack direction="row" spacing={1} alignItems="center" justifyContent="space-between">
                                                <Typography variant="caption" fontWeight={900}>
                                                  {String(c.investor_id || 'unknown')}
                                                </Typography>
                                                <Typography variant="caption" color="text.secondary">
                                                  w={weight.toFixed(2)} · impact={impact.toFixed(2)} · contrib={contribution.toFixed(3)}
                                                </Typography>
                                              </Stack>
                                              <Box
                                                sx={{
                                                  mt: 0.75,
                                                  height: 6,
                                                  borderRadius: 99,
                                                  bgcolor: 'rgba(0,0,0,0.06)',
                                                  overflow: 'hidden',
                                                }}
                                              >
                                                <Box
                                                  sx={{
                                                    height: 6,
                                                    width: `${bar}%`,
                                                    bgcolor: contribution < 0 ? 'warning.main' : 'success.main',
                                                  }}
                                                />
                                              </Box>
                                            </Paper>
                                          );
                                        })}
                                      </Stack>
                                    </Box>
                                  )}
                              </Paper>
                            )}

                            {Array.isArray(sec.expert_opinions) && sec.expert_opinions.length > 0 && (
                              <Box sx={{ mb: 2 }}>
                                <Typography variant="subtitle2" fontWeight={900} sx={{ mb: 1 }}>
                                  各自核心理由
                                </Typography>
                                <Stack spacing={1}>
                                  {sec.expert_opinions.map((op: any, idx: number) => (
                                    <Paper key={idx} variant="outlined" sx={{ p: 1.5, borderRadius: 2 }}>
                                      <Typography variant="body2" fontWeight={900}>
                                        {op.expert}
                                      </Typography>
                                      <Box sx={{ mt: 0.5, '& p': { m: 0 } }}>
                                        <ReactMarkdown>{op.summary || ''}</ReactMarkdown>
                                      </Box>
                                    </Paper>
                                  ))}
                                </Stack>
                              </Box>
                            )}

                            <Divider sx={{ my: 2 }} />

                            <Typography variant="subtitle2" fontWeight={900} sx={{ mb: 1 }}>
                              共识点
                            </Typography>
                            <Box sx={{ '& p': { m: 0 } }}>
                              <ReactMarkdown>{sec.consensus || ''}</ReactMarkdown>
                            </Box>

                            <Typography variant="subtitle2" fontWeight={900} sx={{ mt: 2, mb: 1 }}>
                              分歧点
                            </Typography>
                            <Box sx={{ '& p': { m: 0 } }}>
                              <ReactMarkdown>{sec.conflicts || ''}</ReactMarkdown>
                            </Box>

                            <Typography variant="subtitle2" fontWeight={900} sx={{ mt: 2, mb: 1 }}>
                              最终合意建议
                            </Typography>
                            <Box sx={{ '& p': { m: 0 } }}>
                              <ReactMarkdown>{sec.synthesis || ''}</ReactMarkdown>
                            </Box>

                            {Array.isArray(sec.citations) && sec.citations.length > 0 && (
                              <Box sx={{ mt: 2 }}>
                                <Typography variant="subtitle2" fontWeight={900} sx={{ mb: 1 }}>
                                  引用（可点击跳转）
                                </Typography>
                                <Stack spacing={0.75}>
                                  {sec.citations.map((c: any) => {
                                    const expertId = c.expert || c.investor_id;
                                    const ruleId = c.rule_id;
                                    const href =
                                      expertId && typeof expertId === 'string'
                                        ? `/investors/${expertId}${ruleId ? `#rule-${ruleId}` : ''}`
                                        : undefined;
                                    return (
                                      <Paper key={c.id} variant="outlined" sx={{ p: 1, borderRadius: 2 }}>
                                        <Stack direction="row" spacing={1} alignItems="center" flexWrap="wrap" useFlexGap>
                                          <Chip label={`#${c.id}`} size="small" sx={{ fontWeight: 800 }} />
                                          {href ? (
                                            <Button component={Link} href={href} size="small" sx={{ fontWeight: 900 }}>
                                              {expertId}{ruleId ? ` · ${ruleId}` : ''}
                                            </Button>
                                          ) : (
                                            <Typography variant="caption" fontWeight={800}>
                                              {String(expertId || 'unknown')}
                                            </Typography>
                                          )}
                                          <Typography variant="caption" color="text.secondary">
                                            {c.kind ? `kind=${c.kind} ` : ''}
                                            {c.source ? `source=${c.source}` : ''}
                                            {c.title_hint ? ` · ${c.title_hint}` : ''}
                                          </Typography>
                                        </Stack>
                                      </Paper>
                                    );
                                  })}
                                </Stack>
                              </Box>
                            )}
                          </AccordionDetails>
                        </Accordion>
                      </>
                    );
                  })()}
                </CardContent>
              </Card>
            )}

            {chatResults.map((r, i) => (
              <Card key={i} variant="outlined" sx={{ borderRadius: 2 }}>
                <CardContent sx={{ p: 2 }}>
                  <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1 }}>
                    <Chip 
                      label={r.metadata.investor_id} 
                      size="small" 
                      color="primary" 
                      sx={{ fontWeight: 800, fontSize: 10 }}
                    />
                    <Typography variant="caption" color="text.secondary">
                      相似度: {(r.similarity_estimate * 100).toFixed(0)}%
                    </Typography>
                    <Box sx={{ flex: 1 }} />
                    <Button 
                      size="small" 
                      component={Link} 
                      href={`/investors/${r.metadata.investor_id}`}
                      sx={{ fontSize: 10 }}
                    >
                      查看大师
                    </Button>
                  </Stack>
                  <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap', fontSize: 13, lineHeight: 1.6 }}>
                    {r.content}
                  </Typography>
                  <Box sx={{ mt: 1.5, pt: 1, borderTop: '1px dashed rgba(0,0,0,0.05)' }}>
                    <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
                      来源: {r.metadata.title_hint || r.metadata.source}
                    </Typography>
                  </Box>
                </CardContent>
              </Card>
            ))}
          </Stack>
        </Box>

        <Box sx={{ p: 2, borderTop: '1px solid rgba(0,0,0,0.1)', bgcolor: 'background.paper' }}>
          <TextField
            fullWidth
            placeholder="向所有大师提问..."
            value={chatQuery}
            onChange={(e) => setChatQuery(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleChatQuery()}
            InputProps={{
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton onClick={() => handleChatQuery()} disabled={chatLoading} color="primary">
                    <SendIcon />
                  </IconButton>
                </InputAdornment>
              )
            }}
          />
        </Box>
      </Drawer>

      <Fab 
        color="primary" 
        aria-label="chat" 
        onClick={() => setChatOpen(true)}
        sx={{ 
          position: 'fixed', 
          bottom: 32, 
          right: 32, 
          boxShadow: '0 8px 32px rgba(2, 6, 23, 0.25)',
          '&:hover': { transform: 'scale(1.1)' },
          transition: 'transform 0.2s'
        }}
      >
        <ChatIcon />
      </Fab>
    </Box>
  );
}
