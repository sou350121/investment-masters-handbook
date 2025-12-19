'use client';
import React, { useState } from 'react';
import { 
  Box, 
  Typography, 
  Tabs, 
  Tab, 
  Paper, 
  Chip, 
  Breadcrumbs,
  Link as MuiLink,
  Card,
  CardContent,
  Stack,
  Avatar
} from '@mui/material';
import Link from 'next/link';
import ReactMarkdown from 'react-markdown';
import { Investor, Rule } from '@/lib/imh/data';
import AskPanel from '@/components/AskPanel';
import { getAvatarUrl } from '@/lib/imh/avatarMap';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function CustomTabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      {...other}
    >
      {value === index && (
        <Box sx={{ py: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

export default function InvestorDetail({ 
  investor, 
  rules 
}: { 
  investor: Investor; 
  rules: Rule[] 
}) {
  const [tab, setTab] = useState(0);
  const [missingAvatar, setMissingAvatar] = useState(false);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTab(newValue);
  };

  const groupedRules = rules.reduce((acc, rule) => {
    const kind = rule.kind || 'other';
    if (!acc[kind]) acc[kind] = [];
    acc[kind].push(rule);
    return acc;
  }, {} as Record<string, Rule[]>);

  const kindLabels: Record<string, string> = {
    entry: '入场规则 (Entry)',
    exit: '出场规则 (Exit)',
    risk_management: '风险管理 (Risk Management)',
    other: '其他 (Other)'
  };

  return (
    <Box sx={{ maxWidth: 1000, mx: 'auto', p: { xs: 2, md: 4 } }}>
      <Breadcrumbs sx={{ mb: 2 }}>
        <MuiLink component={Link} href="/" color="inherit">
          大师目录
        </MuiLink>
        <Typography color="text.primary">{investor.chinese_name}</Typography>
      </Breadcrumbs>

      <Paper sx={{ p: 4, mb: 4, bgcolor: 'primary.main', color: 'primary.contrastText' }}>
        <Stack direction="row" spacing={2} alignItems="center" sx={{ mb: 1 }}>
          <Avatar
            src={!missingAvatar ? getAvatarUrl(investor) ?? undefined : undefined}
            imgProps={{ onError: () => setMissingAvatar(true) }}
            sx={{
              width: 64,
              height: 64,
              fontSize: 28,
              bgcolor: 'rgba(255,255,255,0.2)',
              border: '1px solid rgba(255,255,255,0.35)',
            }}
          >
            {investor.chinese_name?.slice(0, 1) || investor.full_name?.slice(0, 1) || '?'}
          </Avatar>
          <Box sx={{ minWidth: 0 }}>
            <Typography variant="h3" component="h1" fontWeight="bold" sx={{ lineHeight: 1.05 }}>
              {investor.chinese_name}
            </Typography>
            <Typography variant="h6" sx={{ opacity: 0.9 }}>
              {investor.full_name}
            </Typography>
          </Box>
        </Stack>
        
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
          {investor.style.map(s => (
            <Chip key={s} label={s} sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'inherit' }} />
          ))}
          {investor.best_for.map(b => (
            <Chip key={b} label={b} sx={{ bgcolor: 'rgba(255,255,255,0.1)', color: 'inherit' }} />
          ))}
        </Box>
      </Paper>

      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={tab} onChange={handleTabChange}>
          <Tab label="哲学与框架 (Overview)" />
          <Tab label="交易规则 (Trading Rules)" />
          <Tab label="智能问答 (Ask AI)" />
        </Tabs>
      </Box>

      <CustomTabPanel value={tab} index={0}>
        <Paper sx={{ p: 4 }}>
          <Box className="markdown-body">
            <ReactMarkdown>{investor.content || '暂无内容'}</ReactMarkdown>
          </Box>
        </Paper>
      </CustomTabPanel>

      <CustomTabPanel value={tab} index={1}>
        {Object.entries(groupedRules).length === 0 ? (
          <Typography color="text.secondary">该大师暂无结构化规则</Typography>
        ) : (
          Object.entries(groupedRules).map(([kind, kindRules]) => (
            <Box key={kind} sx={{ mb: 4 }}>
              <Typography variant="h5" gutterBottom color="primary" fontWeight="bold">
                {kindLabels[kind] || kind}
              </Typography>
              <Stack spacing={2}>
                {kindRules.map(rule => (
                  <Card key={rule.rule_id} variant="outlined">
                    <CardContent>
                      <Box sx={{ mb: 1 }}>
                        <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 'bold' }}>
                          WHEN
                        </Typography>
                        <Typography variant="body1">{rule.when}</Typography>
                      </Box>
                      <Box sx={{ mb: 1 }}>
                        <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 'bold' }}>
                          THEN
                        </Typography>
                        <Typography variant="body1" color="primary.main" fontWeight="medium">
                          {rule.then}
                        </Typography>
                      </Box>
                      {rule.because && (
                        <Box>
                          <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 'bold' }}>
                            BECAUSE
                          </Typography>
                          <Typography variant="body2" sx={{ fontStyle: 'italic' }}>{rule.because}</Typography>
                        </Box>
                      )}
                    </CardContent>
                  </Card>
                ))}
              </Stack>
            </Box>
          ))
        )}
      </CustomTabPanel>

      <CustomTabPanel value={tab} index={2}>
        <Paper sx={{ p: 4 }}>
          <Typography variant="h6" gutterBottom>
            针对 {investor.chinese_name} 的智慧提问
          </Typography>
          <Typography color="text.secondary" sx={{ mb: 4 }}>
            基于 RAG (检索增强生成) 技术，从 {investor.chinese_name} 的投资哲学与交易规则中寻找答案。
          </Typography>
          
          <AskPanel investorId={investor.id} />
        </Paper>
      </CustomTabPanel>
    </Box>
  );
}
