'use client';
import React, { useState } from 'react';
import { 
  TextField, 
  Grid, 
  Card, 
  CardContent, 
  Typography, 
  Box, 
  Chip, 
  InputAdornment,
  CardActionArea
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import Link from 'next/link';
import { Investor } from '@/lib/imh/data';

export default function InvestorList({ investors }: { investors: Investor[] }) {
  const [search, setSearch] = useState('');

  const filtered = investors.filter(i => 
    i.full_name.toLowerCase().includes(search.toLowerCase()) ||
    i.chinese_name.includes(search) ||
    i.style.some(s => s.toLowerCase().includes(search.toLowerCase())) ||
    i.best_for.some(b => b.toLowerCase().includes(search.toLowerCase()))
  );

  return (
    <Box sx={{ maxWidth: 1200, mx: 'auto', p: 4 }}>
      <Box sx={{ mb: 6, textAlign: 'center' }}>
        <Typography variant="h3" component="h1" gutterBottom fontWeight="bold" color="primary">
          Investment Masters Handbook
        </Typography>
        <Typography variant="h6" color="text.secondary" gutterBottom>
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

      <Grid container spacing={3}>
        {filtered.map((investor) => (
          <Grid item xs={12} sm={6} md={4} key={investor.id}>
            <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
              <CardActionArea component={Link} href={`/investors/${investor.id}`} sx={{ flexGrow: 1 }}>
                <CardContent>
                  <Typography variant="h5" component="div" gutterBottom fontWeight="bold">
                    {investor.chinese_name}
                  </Typography>
                  <Typography variant="subtitle1" color="text.secondary" gutterBottom>
                    {investor.full_name}
                  </Typography>
                  
                  <Box sx={{ mt: 2, display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {investor.style.map(s => (
                      <Chip key={s} label={s} size="small" variant="outlined" color="primary" />
                    ))}
                  </Box>
                  
                  <Box sx={{ mt: 1, display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {investor.best_for.map(b => (
                      <Chip key={b} label={b} size="small" />
                    ))}
                  </Box>
                </CardContent>
              </CardActionArea>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}
