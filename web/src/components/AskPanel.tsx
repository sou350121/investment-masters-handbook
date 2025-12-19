'use client';
import React, { useState } from 'react';
import { 
  Box, 
  TextField, 
  Button, 
  Typography, 
  Card, 
  CardContent, 
  CircularProgress,
  Stack,
  Chip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Alert
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import SendIcon from '@mui/icons-material/Send';
import InfoIcon from '@mui/icons-material/Info';

interface RAGResult {
  content: string;
  metadata: any;
  similarity_estimate: number;
}

export default function AskPanel({ investorId }: { investor_id?: string }) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<RAGResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async () => {
    if (!query.trim()) return;
    
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('/api/rag/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query,
          investor_id: investorId,
          top_k: 5
        }),
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.error || '检索失败');
      }

      const data = await response.json();
      setResults(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      <Stack direction="row" spacing={1} sx={{ mb: 3 }}>
        <TextField
          fullWidth
          variant="outlined"
          placeholder="输入你的投资问题..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          disabled={loading}
        />
        <Button 
          variant="contained" 
          onClick={handleSearch} 
          disabled={loading}
          startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <SendIcon />}
        >
          提问
        </Button>
      </Stack>

      {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}

      {results.length === 0 && !loading && !error && (
        <Box sx={{ textAlign: 'center', py: 4, color: 'text.secondary' }}>
          <InfoIcon sx={{ fontSize: 40, mb: 1, opacity: 0.5 }} />
          <Typography>向大师提问，AI 将从知识库中检索最相关的回答</Typography>
        </Box>
      )}

      <Stack spacing={2}>
        {results.map((result, idx) => (
          <Card key={idx} variant="outlined" sx={{ borderLeft: 6, borderLeftColor: 'primary.main' }}>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                <Box sx={{ display: 'flex', gap: 1 }}>
                  <Chip 
                    label={result.metadata.source_type === 'rule' ? '规则' : '文档'} 
                    size="small" 
                    color={result.metadata.source_type === 'rule' ? 'secondary' : 'primary'}
                  />
                  <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5 }}>
                    相似度: {(result.similarity_estimate * 100).toFixed(1)}%
                  </Typography>
                </Box>
                <Typography variant="caption" color="text.secondary">
                  #{idx + 1}
                </Typography>
              </Box>

              <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap', mb: 2 }}>
                {result.content}
              </Typography>

              <Accordion variant="outlined" sx={{ border: 'none', '&:before': { display: 'none' }, bgcolor: 'grey.50' }}>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography variant="caption" fontWeight="bold">查看溯源信息</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Typography variant="caption" component="div" sx={{ fontFamily: 'monospace' }}>
                    <strong>来源:</strong> {result.metadata.source}<br />
                    <strong>引用 ID:</strong> {result.metadata.rule_id || result.metadata.chunk_id}<br />
                    {result.metadata.title_hint && <><strong>章节:</strong> {result.metadata.title_hint}<br /></>}
                    {result.metadata.start_index !== undefined && <><strong>字符偏移:</strong> {result.metadata.start_index}</>}
                  </Typography>
                </AccordionDetails>
              </Accordion>
            </CardContent>
          </Card>
        ))}
      </Stack>
    </Box>
  );
}
