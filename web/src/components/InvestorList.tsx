'use client';
import React, { useState } from 'react';
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
  Stack
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
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
    </Box>
  );
}
