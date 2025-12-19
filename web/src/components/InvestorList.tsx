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
  Divider
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import Link from 'next/link';
import { Investor } from '@/lib/imh/data';
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

export default function InvestorList({ investors }: { investors: Investor[] }) {
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
            <Paper
              variant="outlined"
              sx={{
                p: 2,
                borderRadius: 3,
                bgcolor: 'background.paper',
                borderColor: 'rgba(2,6,23,0.10)',
              }}
            >
              <Typography fontWeight={800} sx={{ mb: 0.5 }}>
                快速路由：把“今天的股票信息”贴进来 → 推荐该问哪些大师
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                这是一个“很简单但很好用”的功能：先用关键词/情境把问题路由到合适的大师，再点进去 Ask AI 获取依据与溯源。
              </Typography>

              <TextField
                fullWidth
                multiline
                minRows={3}
                placeholder="示例：\n今天AAPL涨5%，成交放大。我担心估值太贵且市场过热，该追吗？如果回撤到哪里更合适？\n（你也可以粘贴：新闻、财报摘要、K线描述、仓位与止损计划…）"
                value={routeText}
                onChange={(e) => setRouteText(e.target.value)}
                disabled={routeLoading}
              />

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
            </Paper>
          </Box>
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
    </Box>
  );
}
