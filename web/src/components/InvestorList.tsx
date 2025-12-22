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
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Divider,
  Drawer,
  IconButton,
  CircularProgress
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
  const [chatOpen, setChatOpen] = useState(false);
  const [chatQuery, setChatQuery] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  const [chatResults, setChatResults] = useState<RagResponseItem[]>([]);
  const [chatError, setChatError] = useState<string | null>(null);

  type PolicyGateResponse = {
    regime: { id: string; label?: string; score?: number; confidence?: number; reasons?: string[] };
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

  const loadScenarios = () => {
    fetch('/api/policy/scenarios')
      .then(r => r.json())
      .then(data => setScenarios(data.scenarios || []))
      .catch(err => console.error('Failed to load scenarios', err));
  };

  useEffect(() => {
    loadScenarios();
  }, []);

  async function handleValidateAll() {
    setBatchLoading(true);
    setBatchReport(null);
    try {
      const resp = await fetch('/api/policy/validate_all', { method: 'POST' });
      if (!resp.ok) throw new Error('批量验证失败');
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
    try {
      const resp = await fetch('/api/rag/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: q, top_k: 8 }),
      });
      if (!resp.ok) throw new Error('对话请求失败');
      const data = await resp.json();
      setChatResults(data);
    } catch (e: any) {
      setChatError(e.message || '搜索失败');
    } finally {
      setChatLoading(false);
    }
  }

  useEffect(() => {
    if (typeof window !== 'undefined') setOrigin(window.location.origin);
  }, []);

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
    <Box sx={{ maxWidth: 1200, mx: 'auto', p: 4 }}>
      <Box sx={{ mb: 6, textAlign: 'center' }}>
        <Typography variant="h4" component="h1" gutterBottom fontWeight="bold" color="primary">
          Investment Masters Handbook
        </Typography>
        <Typography variant="body1" color="text.secondary" gutterBottom>
          复现 17 位投资传奇的决策大脑
        </Typography>
        
        <Box sx={{ mt: 4, display: 'flex', justifyContent: 'center' }}>
          <TextField
            fullWidth
            sx={{ maxWidth: 600 }}
            placeholder="搜索大师姓名、风格或领域..."
            variant="outlined"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon color="action" />
                </InputAdornment>
              ),
              sx: { borderRadius: 50, bgcolor: 'background.paper' }
            }}
          />
        </Box>

        <Box sx={{ mt: 2, display: 'flex', justifyContent: 'center' }}>
          <Paper
            variant="outlined"
            sx={{
              px: 2,
              py: 1,
              borderRadius: 3,
              bgcolor: 'background.paper',
              borderColor: 'rgba(2,6,23,0.10)',
            }}
          >
            <Stack
              direction={{ xs: 'column', sm: 'row' }}
              spacing={1}
              alignItems={{ xs: 'stretch', sm: 'center' }}
              justifyContent="center"
            >
              <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 700 }}>
                API（给网页 / 其他系统调用）
              </Typography>

              <Chip
                label="GET /health"
                size="small"
                component="a"
                href="/health"
                clickable
                variant="outlined"
              />

              <Stack direction="row" spacing={1} alignItems="center" justifyContent="center">
                <Chip label="POST /api/rag/query" size="small" color="primary" variant="outlined" />
                <Button
                  size="small"
                  variant="text"
                  onClick={() =>
                    copy(exampleCurl)
                  }
                >
                  复制 curl
                </Button>
              </Stack>

              <Stack direction="row" spacing={1} alignItems="center" justifyContent="center">
                <Chip label="POST /api/route" size="small" color="secondary" variant="outlined" />
                <Button
                  size="small"
                  variant="text"
                  onClick={() =>
                    copy(
                      `curl -s -X POST \"${api.route}\" -H \"Content-Type: application/json\" -d \"{\\\"text\\\":\\\"今天AAPL涨5%，我担心估值太贵且市场过热，该追吗？\\\",\\\"top_k\\\":5}\"`,
                    )
                  }
                >
                  复制 curl
                </Button>
              </Stack>

              <Typography variant="caption" color="text.secondary" sx={{ opacity: 0.85 }}>
                若你用 /imh 集成（代理）：POST /imh/api/rag/query
              </Typography>
              <Button
                size="small"
                variant="text"
                onClick={() =>
                  copy(exampleCurlImh)
                }
              >
                复制 /imh curl
              </Button>
            </Stack>
          </Paper>
        </Box>

        <Box sx={{ mt: 2, display: 'flex', justifyContent: 'center' }}>
          <Box sx={{ width: '100%', maxWidth: 900, textAlign: 'left' }}>
            <Accordion
              variant="outlined"
              sx={{
                bgcolor: 'rgba(25, 118, 210, 0.04)', // Light blue background
                borderRadius: 3,
                border: '2px solid',
                borderColor: 'primary.main',
                '&:before': { display: 'none' },
              }}
            >
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Stack direction="row" spacing={1.5} alignItems="center">
                  <DescriptionIcon color="primary" />
                  <Typography fontWeight={800} color="primary">
                    查看 IMH 核心产品说明书 (Product Manual)
                  </Typography>
                  <Chip size="small" label="必读" color="primary" />
                </Stack>
              </AccordionSummary>
              <AccordionDetails sx={{ pt: 0, px: 3, pb: 3 }}>
                <Box sx={{ 
                  maxHeight: '60vh', 
                  overflowY: 'auto',
                  pr: 1,
                  '&::-webkit-scrollbar': { width: '6px' },
                  '&::-webkit-scrollbar-thumb': { bgcolor: 'rgba(0,0,0,0.1)', borderRadius: '10px' },
                  '& h1, & h2, & h3': { mt: 3, mb: 1.5, fontWeight: 800, color: 'primary.main' },
                  '& table': { width: '100%', borderCollapse: 'collapse', my: 2, fontSize: '0.85rem' },
                  '& th, & td': { border: '1px solid rgba(0,0,0,0.1)', p: 1, textAlign: 'left' },
                  '& th': { bgcolor: 'rgba(0,0,0,0.05)' },
                  '& code': { bgcolor: 'rgba(0,0,0,0.05)', p: '2px 4px', borderRadius: 1, fontFamily: 'monospace', fontSize: '0.9em' },
                  '& pre': { bgcolor: 'rgba(2,6,23,0.03)', p: 2, borderRadius: 2, overflowX: 'auto', border: '1px dashed rgba(0,0,0,0.1)', mb: 2 },
                  '& blockquote': { borderLeft: '4px solid', borderColor: 'primary.main', pl: 2, m: 0, py: 0.5, bgcolor: 'rgba(2,6,23,0.02)', fontStyle: 'italic' },
                  '& p': { mb: 1.5, lineHeight: 1.7 }
                }}>
                  <ReactMarkdown>{productManual || '暂无说明书内容'}</ReactMarkdown>
                </Box>
              </AccordionDetails>
            </Accordion>
          </Box>
        </Box>

        <Box sx={{ mt: 2, display: 'flex', justifyContent: 'center' }}>
          <Box sx={{ width: '100%', maxWidth: 900 }}>
            <Accordion variant="outlined" sx={{ bgcolor: 'background.paper', borderRadius: 3 }}>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Stack direction="row" spacing={1} alignItems="center">
                  <Typography fontWeight={800}>新手 1 分钟上手</Typography>
                  <Chip size="small" label="网页" variant="outlined" />
                  <Chip size="small" label="API" variant="outlined" />
                </Stack>
              </AccordionSummary>
              <AccordionDetails>
                <Stack spacing={2}>
                  <Box>
                    <Typography variant="subtitle2" fontWeight={800}>
                      A. 用网页怎么用（最推荐）
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                      1) 在首页搜索框输入：大师姓名 / 风格 / 擅长领域（例如“护城河”、“宏观”、“逆向”）<br />
                      2) 点击任意大师卡片进入详情页<br />
                      3) 切到 <strong>Ask AI</strong>，输入你的问题（例如“什么情况下可以买入？”）<br />
                      4) 结果里可以展开 <strong>溯源信息</strong>，看到来源文件与引用编号（更可信）
                    </Typography>
                  </Box>

                  <Divider />

                  <Box>
                    <Typography variant="subtitle2" fontWeight={800}>
                      B. 用 API 怎么用（给机器人/脚本）
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                      先确认服务在跑：打开 <strong>/health</strong>，看到 status=ok 即可。
                    </Typography>

                    <Stack
                      direction={{ xs: 'column', sm: 'row' }}
                      spacing={1}
                      sx={{ mt: 1 }}
                      alignItems={{ xs: 'stretch', sm: 'center' }}
                    >
                      <Button size="small" variant="outlined" component="a" href="/health">
                        打开 /health
                      </Button>
                      <Button size="small" variant="text" onClick={() => copy(api.health)}>
                        复制完整 /health 链接
                      </Button>
                    </Stack>

                    <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                      然后请求：<strong>POST /api/rag/query</strong>
                    </Typography>

                    <Paper
                      variant="outlined"
                      sx={{
                        mt: 1,
                        p: 1.5,
                        borderRadius: 2,
                        bgcolor: 'rgba(2,6,23,0.02)',
                        fontFamily: 'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace',
                        fontSize: 12,
                        whiteSpace: 'pre-wrap',
                      }}
                    >
                      {exampleCurl}
                    </Paper>

                    <Stack direction="row" spacing={1} sx={{ mt: 1 }} justifyContent="flex-start">
                      <Button size="small" variant="contained" onClick={() => copy(exampleCurl)}>
                        复制 curl
                      </Button>
                      <Button size="small" variant="text" onClick={() => copy(exampleBody)}>
                        复制 JSON body
                      </Button>
                    </Stack>

                    <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                      可选字段（不懂就先不填）：<br />
                      - investor_id：只问某位大师（如 warren_buffett）<br />
                      - top_k：返回几条（默认 5）<br />
                      - source_type：rule / investor_doc<br />
                      - kind：entry / exit / risk_management / other
                    </Typography>

                    <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                      返回是一个数组，每条都有：<strong>content</strong>（片段内容）、<strong>metadata</strong>（来源/引用/偏移）、<strong>similarity_estimate</strong>（相似度估算）。
                    </Typography>

                    <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1 }}>
                      如果你是通过 /imh 集成到别的系统里：用 <strong>POST /imh/api/rag/query</strong>（上方也有一键复制）。
                    </Typography>
                  </Box>
                </Stack>
              </AccordionDetails>
            </Accordion>
          </Box>
        </Box>

        <Box sx={{ mt: 2, display: 'flex', justifyContent: 'center' }}>
          <Box sx={{ width: '100%', maxWidth: 900, textAlign: 'left' }}>
            <Accordion
              variant="outlined"
              sx={{
                bgcolor: 'background.paper',
                borderRadius: 3,
                '&:before': { display: 'none' },
                borderColor: 'rgba(2,6,23,0.10)',
              }}
            >
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Stack direction="row" spacing={1} alignItems="center">
                  <Typography fontWeight={800}>Policy Gate：Regime Router → Risk Overlay（不改方向）</Typography>
                  <Chip size="small" label="护栏" color="secondary" variant="outlined" />
                  <Chip size="small" label="/api/policy/gate" variant="outlined" />
                </Stack>
              </AccordionSummary>
              <AccordionDetails sx={{ pt: 0 }}>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                  最安全的用法：策略信号（买/卖）由你的系统决定；Handbook 只输出 risk_multiplier 与 max_leverage/min_cash/max_invest/max_turnover/max_corr 的乘数与绝对护栏。
                </Typography>

                {/* --- Scenario Sandbox --- */}
                <Box sx={{ mb: 2, p: 2, bgcolor: 'rgba(25, 118, 210, 0.05)', borderRadius: 2, border: '1px solid rgba(25, 118, 210, 0.1)' }}>
                  <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 1.5 }}>
                    <Typography variant="subtitle2" fontWeight={800} color="primary" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      🚀 场景沙盒 (Scenario Sandbox)
                      <Chip size="small" label="New" color="primary" sx={{ height: 16, fontSize: 10 }} />
                    </Typography>
                    <Button 
                      size="small" 
                      variant="outlined" 
                      startIcon={<PlayArrowIcon />} 
                      onClick={handleValidateAll}
                      disabled={batchLoading}
                    >
                      {batchLoading ? '运行中...' : '运行全量回归 (Run All)'}
                    </Button>
                  </Stack>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                    {scenarios.map((s) => (
                      <Chip
                        key={s.id}
                        label={s.label}
                        clickable
                        variant={selectedScenarioId === s.id ? 'filled' : 'outlined'}
                        color={selectedScenarioId === s.id ? 'primary' : 'default'}
                        onClick={() => {
                          setSelectedScenarioId(s.id);
                          setPolicyText(s.description);
                          setPolicyFeaturesJson(JSON.stringify(s.features, null, 2));
                          setPolicyPortfolioJson(JSON.stringify(s.portfolio_state || {}, null, 2));
                          setPolicyResult(null);
                          setValidationReport(null);
                        }}
                      />
                    ))}
                    {selectedScenarioId && (
                      <Button size="small" variant="text" color="inherit" onClick={() => {
                        setSelectedScenarioId(null);
                        setValidationReport(null);
                      }}>
                        重置
                      </Button>
                    )}
                  </Box>
                  {selectedScenarioId && (
                    <Stack direction="row" spacing={1} alignItems="center" sx={{ mt: 1.5 }}>
                      <Typography variant="caption" color="text.secondary" sx={{ fontStyle: 'italic' }}>
                        编辑后可保存到本地：
                      </Typography>
                      <Button 
                        size="small" 
                        variant="contained" 
                        color="success" 
                        startIcon={<SaveIcon />} 
                        onClick={handleSaveCurrentScenario}
                        sx={{ height: 24, fontSize: 10 }}
                      >
                        保存当前场景
                      </Button>
                    </Stack>
                  )}
                </Box>

                {/* --- Batch Regression Report --- */}
                {batchReport && (
                  <Paper variant="outlined" sx={{ mb: 2, p: 2, borderRadius: 2, bgcolor: 'rgba(0,0,0,0.02)', border: '1px solid rgba(0,0,0,0.1)' }}>
                    <Typography variant="subtitle2" fontWeight={800} gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      🧪 批量回归报告 (Regression Scorecard)
                      <IconButton size="small" onClick={() => setBatchReport(null)} sx={{ ml: 'auto' }}>
                        <CloseIcon sx={{ fontSize: 14 }} />
                      </IconButton>
                    </Typography>
                    <Stack direction="row" spacing={2} sx={{ mb: 1.5 }}>
                      <Chip label={`总数: ${batchReport.total}`} size="small" variant="outlined" />
                      <Chip label={`通过: ${batchReport.passed_count}`} size="small" color="success" />
                      <Chip label={`失败: ${batchReport.failed_count}`} size="small" color={batchReport.failed_count > 0 ? 'error' : 'default'} />
                    </Stack>
                    <Box sx={{ maxHeight: 200, overflowY: 'auto' }}>
                      {batchReport.items.map((item: any, idx: number) => (
                        <Box key={idx} sx={{ mb: 1, pb: 1, borderBottom: '1px dashed rgba(0,0,0,0.05)' }}>
                          <Typography variant="caption" fontWeight={700} color={item.passed ? 'success.main' : 'error.main'} sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                            {item.passed ? '✅' : '❌'} {item.label}
                          </Typography>
                          {item.details.map((d: string, i: number) => (
                            <Typography key={i} variant="caption" color="text.secondary" sx={{ display: 'block', ml: 2, fontSize: 10 }}>
                              {d}
                            </Typography>
                          ))}
                        </Box>
                      ))}
                    </Box>
                  </Paper>
                )}

                <TextField
                  fullWidth
                  multiline
                  minRows={3}
                  label="Market Observations / text"
                  placeholder="示例：
近期成交极度拥挤、上涨家数下降但指数创新高；我担心估值泡沫与流动性转向。
我希望策略继续做多，但仓位/杠杆/换手需要收紧到什么程度？"
                  value={policyText}
                  onChange={(e) => setPolicyText(e.target.value)}
                  disabled={policyLoading}
                />

                <Box sx={{ mt: 1, display: 'grid', gap: 1, gridTemplateColumns: { xs: '1fr', md: 'repeat(3, 1fr)' } }}>
                  <TextField
                    multiline
                    minRows={7}
                    label="features (JSON)"
                    value={policyFeaturesJson}
                    onChange={(e) => setPolicyFeaturesJson(e.target.value)}
                    disabled={policyLoading}
                  />
                  <TextField
                    multiline
                    minRows={7}
                    label="portfolio_state (JSON)"
                    value={policyPortfolioJson}
                    onChange={(e) => setPolicyPortfolioJson(e.target.value)}
                    disabled={policyLoading}
                  />
                  <TextField
                    multiline
                    minRows={7}
                    label="constraints (JSON)"
                    value={policyConstraintsJson}
                    onChange={(e) => setPolicyConstraintsJson(e.target.value)}
                    disabled={policyLoading}
                  />
                </Box>

                <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1} sx={{ mt: 1 }} alignItems="center">
                  <Button variant="contained" onClick={handlePolicyGate} disabled={policyLoading}>
                    {policyLoading ? '正在生成护栏…' : '生成 Policy Gate 护栏'}
                  </Button>
                  <Button
                    variant="text"
                    disabled={policyLoading}
                    onClick={() => {
                      setPolicyText('近期成交极度拥挤、上涨家数下降但指数创新高；我担心估值泡沫与流动性转向。\n我希望策略继续做多，但仓位/杠杆/换手需要收紧到什么程度？');
                    }}
                  >
                    填入示例
                  </Button>
                  <Button
                    variant="outlined"
                    disabled={!policyResult?.explanation?.markdown}
                    onClick={() => {
                      const md = policyResult?.explanation?.markdown || '';
                      copy(md);
                    }}
                  >
                    复制解释（Markdown）
                  </Button>
                  <Button
                    variant="outlined"
                    disabled={!policyResult?.explanation?.markdown}
                    onClick={() => {
                      const md = policyResult?.explanation?.markdown || '';
                      setChatQuery(md);
                      setChatOpen(true);
                      handleChatQuery(md);
                    }}
                  >
                    用解释继续 Ask AI
                  </Button>
                </Stack>

                {policyError && (
                  <Alert severity="error" sx={{ mt: 1 }}>
                    {policyError}
                  </Alert>
                )}

                {policyResult && (
                  <Box sx={{ mt: 1.5 }}>
                    {/* --- Validation Report --- */}
                    {validationReport && (
                      <Paper 
                        variant="outlined" 
                        sx={{ 
                          p: 1.5, 
                          mb: 2, 
                          borderRadius: 2, 
                          border: '2px solid',
                          borderColor: validationReport.passed ? 'success.main' : 'error.main',
                          bgcolor: validationReport.passed ? 'rgba(76, 175, 80, 0.05)' : 'rgba(244, 67, 54, 0.05)'
                        }}
                      >
                        <Typography variant="subtitle2" fontWeight={800} color={validationReport.passed ? 'success.main' : 'error.main'} sx={{ mb: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
                          {validationReport.passed ? '✅ 场景验证通过' : '❌ 场景验证不符合预期'}
                        </Typography>
                        <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr' }, gap: 1 }}>
                          {validationReport.details.map((d, i) => (
                            <Typography key={i} variant="caption" sx={{ fontFamily: 'monospace' }}>{d}</Typography>
                          ))}
                        </Box>
                      </Paper>
                    )}

                    <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1} alignItems={{ xs: 'flex-start', sm: 'center' }}>
                      <Chip
                        label={`Regime: ${policyResult.regime.id} (${policyResult.regime.confidence ?? 0})`}
                        color="primary"
                        variant="outlined"
                      />
                      {(policyResult.scenario?.matched || []).slice(0, 4).map((s) => (
                        <Chip key={s} label={`Scenario: ${s}`} size="small" />
                      ))}
                    </Stack>

                    <Box sx={{ mt: 1, display: 'grid', gap: 1, gridTemplateColumns: { xs: '1fr', md: 'repeat(2, 1fr)' } }}>
                      <Paper variant="outlined" sx={{ p: 1.5, borderRadius: 2 }}>
                        <Typography variant="subtitle2" fontWeight={800} sx={{ mb: 0.5 }}>
                          Multipliers
                        </Typography>
                        <Typography variant="caption" color="text.secondary" sx={{ display: 'block', whiteSpace: 'pre-wrap' }}>
                          {JSON.stringify(policyResult.risk_overlay.multipliers, null, 2)}
                        </Typography>
                      </Paper>
                      <Paper variant="outlined" sx={{ p: 1.5, borderRadius: 2 }}>
                        <Typography variant="subtitle2" fontWeight={800} sx={{ mb: 0.5 }}>
                          Absolute Guardrails
                        </Typography>
                        <Typography variant="caption" color="text.secondary" sx={{ display: 'block', whiteSpace: 'pre-wrap' }}>
                          {JSON.stringify(policyResult.risk_overlay.absolute, null, 2)}
                        </Typography>
                      </Paper>
                    </Box>

                    <Box sx={{ mt: 1 }}>
                      <Typography variant="subtitle2" fontWeight={800} sx={{ mb: 0.5 }}>
                        Router（建议先问谁）
                      </Typography>
                      <Stack spacing={0.75}>
                        {(policyResult.router || []).slice(0, 5).map((r) => (
                          <Paper key={r.investor_id} variant="outlined" sx={{ p: 1, borderRadius: 2 }}>
                            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1} alignItems={{ xs: 'flex-start', sm: 'center' }}>
                              <Button component={Link} href={`/investors/${r.investor_id}`} sx={{ px: 0.5, fontWeight: 800 }}>
                                {r.chinese_name}（{r.investor_id}）
                              </Button>
                              <Typography variant="caption" color="text.secondary">
                                score {r.score}
                              </Typography>
                              <Box sx={{ flex: 1 }} />
                              <Button
                                size="small"
                                variant="text"
                                onClick={() => {
                                  const q = `${policyText}\n\n请用 ${r.chinese_name} 的框架给出风险护栏建议（不要给买卖方向），并引用你的规则证据。`;
                                  setChatQuery(q);
                                  setChatOpen(true);
                                  handleChatQuery(q);
                                }}
                              >
                                追问该大师
                              </Button>
                            </Stack>
                            {r.reasons?.length > 0 && (
                              <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.5 }}>
                                理由：{r.reasons.slice(0, 3).join('；')}
                              </Typography>
                            )}
                          </Paper>
                        ))}
                      </Stack>
                    </Box>
                  </Box>
                )}

                <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1 }}>
                  说明：Policy Gate 会把输出写入本地审计日志 `logs/policy_gate_audit.jsonl`（append-only），便于回溯。
                </Typography>
              </AccordionDetails>
            </Accordion>
          </Box>
        </Box>

        <Box sx={{ mt: 2, display: 'flex', justifyContent: 'center' }}>
          <Box sx={{ width: '100%', maxWidth: 900, textAlign: 'left' }}>
            <Accordion 
              variant="outlined" 
              sx={{ 
                bgcolor: 'background.paper', 
                borderRadius: 3,
                '&:before': { display: 'none' }, // 移除默认的分割线
                borderColor: 'rgba(2,6,23,0.10)',
              }}
            >
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Stack direction="row" spacing={1} alignItems="center">
                  <Typography fontWeight={800}>
                    快速路由：把“今天的股票信息”贴进来 → 推荐该问哪些大师
                  </Typography>
                  <Chip size="small" label="决策推荐" color="primary" variant="outlined" />
                </Stack>
              </AccordionSummary>
              <AccordionDetails sx={{ px: 2, pb: 2, pt: 0 }}>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                  这是一个“很简单但很好用”的功能：先用关键词/情境把问题路由到合适的大师，再点进去 Ask AI 获取依据与溯源。
                </Typography>

              <Box
                sx={{
                  mb: 2,
                  p: 2,
                  borderRadius: 2,
                  bgcolor: 'rgba(2,6,23,0.03)',
                  border: '1px dashed rgba(2,6,23,0.1)',
                  fontFamily: 'ui-monospace, Consolas, monospace',
                  fontSize: 12,
                  lineHeight: 1.2,
                  color: 'text.secondary',
                  display: { xs: 'none', md: 'block' },
                }}
              >
                <pre style={{ margin: 0 }}>
                  {`          [ 用户提问 / 股票信息 ]
                    |
                    v
    +--------------------------------+
    |    1. 意图路由 (Intention)      |
    |  - 关键词触发 / 场景映射规则     |
    |  - 题库匹配 (Quick Lookup)     |
    +----------------+---------------+
                     |
       +-------------+-------------+
       |             |             |
 [ 选股大师 ]   [ 宏观大师 ]   [ 趋势大师 ]
 (如：巴菲特)   (如：达利奥)   (如：帕利哈皮)
       |             |             |
       +-------------+-------------+
                     |
                     v
    +--------------------------------+
    |   2. RAG 知识增强 (Knowledge)    |
    |  - 语义向量搜索 (ChromaDB)      |
    |  - 核心决策规则提取 (IF-THEN)   |
    |  - 大师原著文档片段 (Markdown)  |
    +----------------+---------------+
                     |
                     v
    +--------------------------------+
    |   3. 逻辑推理与溯源 (Evidence)   |
    |  - 标注引用片段编号 (Source ID) |
    |  - 对齐大师投资原则 (Rules)     |
    +----------------+---------------+
                     |
                     v
          [ 输出：大师视角的决策建议 ]`}
                </pre>
              </Box>

              <TextField
                fullWidth
                multiline
                minRows={3}
                placeholder="示例：\n今天AAPL涨5%，成交放大。我担心估值太贵且市场过热，该追吗？如果回撤到哪里更合适？\n（你也可以粘贴：新闻、财报摘要、K线描述、仓位与止损计划…）"
                value={routeText}
                onChange={(e) => setRouteText(e.target.value)}
                disabled={routeLoading}
              />

              <Box sx={{ mt: 1, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                <Chip
                  icon={<HelpOutlineIcon sx={{ fontSize: '14px !important' }} />}
                  label="查看分类大师题库"
                  color="primary"
                  variant="outlined"
                  size="small"
                  onClick={() => {
                    const el = document.getElementById('master-questions');
                    el?.scrollIntoView({ behavior: 'smooth' });
                  }}
                />
                <Chip
                  label="模板：止损/仓位"
                  clickable
                  onClick={() => setRouteText('我买了TSLA，目前浮亏8%。应该止损吗？止损点位怎么定？仓位要不要减半？')}
                />
                <Chip
                  label="模板：低估/高估"
                  clickable
                  onClick={() => setRouteText('请判断这只股票是低估还是高估？当前估值是否合理？如果要买，安全边际要多少？')}
                />
                <Chip
                  label="模板：宏观/利率"
                  clickable
                  onClick={() => setRouteText('美联储可能降息，通胀回落但经济放缓。现在更适合配置什么类型资产？')}
                />
                <Chip
                  label="模板：价值/安全边际"
                  clickable
                  onClick={() => setRouteText('这家公司现金流稳定，但估值偏贵。我想等到更有安全边际再买，怎么判断“合理价格”？')}
                />
                <Chip
                  label="模板：成长/PEG"
                  clickable
                  onClick={() => setRouteText('NVDA涨很多了，但业绩增速也高。用PEG怎么看是否还能继续持有/加仓？')}
                />
              </Box>

              <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1} sx={{ mt: 1 }} alignItems="center">
                <Button variant="contained" onClick={handleRoute} disabled={routeLoading}>
                  {routeLoading ? '正在推荐…' : '推荐大师'}
                </Button>
                <Button
                  variant="text"
                  onClick={() => {
                    setRouteText('今天AAPL涨5%，成交放大。我担心估值太贵且市场过热，该追吗？如果回撤到哪里更合适？');
                    setRouteResults([]);
                    setRouteError(null);
                  }}
                  disabled={routeLoading}
                >
                  填入示例
                </Button>
                <Typography variant="caption" color="text.secondary" sx={{ ml: { sm: 'auto' } }}>
                  接口：POST /api/route（无需 LLM，本地规则路由）
                </Typography>
              </Stack>

              {routeError && (
                <Alert severity="error" sx={{ mt: 1 }}>
                  {routeError}
                </Alert>
              )}

              {routeResults.length > 0 && (
                <Box sx={{ mt: 1.5 }}>
                  <Typography variant="subtitle2" fontWeight={800} sx={{ mb: 1 }}>
                    推荐结果（点名字进入详情页，再用 Ask AI 追问）
                  </Typography>
                  <Stack spacing={1}>
                    {routeResults.map((r) => (
                      <Paper key={r.investor_id} variant="outlined" sx={{ p: 1.25, borderRadius: 2 }}>
                        <Stack
                          direction={{ xs: 'column', sm: 'row' }}
                          spacing={1}
                          alignItems={{ xs: 'flex-start', sm: 'center' }}
                        >
                          <Button
                            component={Link}
                            href={`/investors/${r.investor_id}`}
                            variant="text"
                            sx={{ px: 0.5, fontWeight: 800 }}
                          >
                            {r.chinese_name}（{r.investor_id}）
                          </Button>
                          <Typography variant="caption" color="text.secondary">
                            {(r.nationality || '—')}{r.fund ? ` · ${r.fund}` : ''}
                          </Typography>
                          <Box sx={{ flex: 1 }} />
                          <Chip size="small" label={`score ${r.score}`} variant="outlined" />
                        </Stack>

                        {(r.matched_scenarios || []).length > 0 && (
                          <Box sx={{ mt: 0.75, display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                            {(r.matched_scenarios || []).slice(0, 3).map((s) => (
                              <Chip key={s} size="small" label={`情境：${s}`} />
                            ))}
                          </Box>
                        )}

                        {r.reasons?.length > 0 && (
                          <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.75 }}>
                            推荐理由：{r.reasons.join('；')}
                          </Typography>
                        )}
                      </Paper>
                    ))}
                  </Stack>
                </Box>
              )}
            </AccordionDetails>
          </Accordion>
        </Box>
      </Box>
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

      <Box
        sx={{
          display: 'grid',
          gap: 2,
          gridTemplateColumns: {
            xs: '1fr',
            sm: 'repeat(2, 1fr)',
            md: 'repeat(3, 1fr)',
            lg: 'repeat(5, 1fr)',
          },
        }}
      >
        {filtered.map((investor) => (
          <Box key={investor.id}>
            <Card className="imh-card" sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
              <CardActionArea component={Link} href={`/investors/${investor.id}`} sx={{ flexGrow: 1 }}>
                <CardContent sx={{ p: 2 }}>
                  <Stack direction="row" spacing={1.5} alignItems="center" sx={{ mb: 1 }}>
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
                        width: 40,
                        height: 40,
                        fontSize: 18,
                        bgcolor: hashToHsl(investor.id),
                        border: '1px solid rgba(2,6,23,0.08)',
                      }}
                    >
                      {getInitials(investor)}
                    </Avatar>
                      );
                    })()}
                    <Box sx={{ minWidth: 0 }}>
                      <Typography
                        variant="subtitle1"
                        component="div"
                        fontWeight={700}
                        sx={{ lineHeight: 1.1 }}
                        noWrap
                      >
                        {investor.chinese_name}
                      </Typography>
                      <Typography variant="caption" color="text.secondary" noWrap sx={{ display: 'block' }}>
                        {investor.full_name}
                      </Typography>
                      <Typography variant="caption" color="text.secondary" noWrap sx={{ display: 'block', opacity: 0.9 }}>
                        {(investor.nationality || '—')}{investor.fund ? ` · ${investor.fund}` : ''}
                      </Typography>
                    </Box>
                  </Stack>

                  <Typography
                    variant="body2"
                    color="text.secondary"
                    sx={{
                      mt: 1,
                      display: '-webkit-box',
                      WebkitLineClamp: 2,
                      WebkitBoxOrient: 'vertical',
                      overflow: 'hidden',
                      minHeight: 36,
                      fontSize: 12.5,
                    }}
                  >
                    {buildIntro(investor)}
                  </Typography>
                  
                  <Box sx={{ mt: 2, display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {investor.style.map(s => (
                      <Chip key={s} label={s} size="small" variant="outlined" color="primary" sx={{ fontSize: 11 }} />
                    ))}
                  </Box>
                  
                  <Box sx={{ mt: 1, display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {investor.best_for.map(b => (
                      <Chip key={b} label={b} size="small" sx={{ fontSize: 11 }} />
                    ))}
                  </Box>
                </CardContent>
              </CardActionArea>
            </Card>
          </Box>
        ))}
      </Box>

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
          <Typography variant="h6" fontWeight={800}>Ask All Masters (全局对话)</Typography>
          <Box sx={{ flex: 1 }} />
          <IconButton onClick={() => setChatOpen(false)} color="inherit">
            <CloseIcon />
          </IconButton>
        </Box>

        <Box sx={{ flex: 1, overflowY: 'auto', p: 2, bgcolor: 'rgba(0,0,0,0.02)' }}>
          {!chatResults.length && !chatLoading && !chatError && (
            <Box sx={{ textAlign: 'center', mt: 4, color: 'text.secondary' }}>
              <Typography variant="body2">点击题库问题，或在下方输入你想问所有投资大师的问题。</Typography>
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
    </Box>
  );
}
