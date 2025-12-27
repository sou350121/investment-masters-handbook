'use client';
import { createTheme } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1a73e8', // Google Blue
    },
    secondary: {
      main: '#fabb05', // Google Yellow
    },
    background: {
      default: '#f8fafc',
    },
  },
  typography: {
    fontFamily: [
      'Google Sans',
      'Roboto',
      'Arial',
      'sans-serif',
    ].join(','),
    h4: { letterSpacing: -0.3 },
    h3: { letterSpacing: -0.4 },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: 8,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: '0 1px 2px 0 rgba(60,64,67,.30), 0 1px 3px 1px rgba(60,64,67,.15)',
          border: '1px solid rgba(2,6,23,0.06)',
          transition: 'transform 160ms ease, box-shadow 160ms ease',
        },
      },
    },
    MuiCardActionArea: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          '&:hover .imh-card': {
            transform: 'translateY(-2px)',
            boxShadow: '0 10px 25px rgba(2,6,23,0.10)',
          },
        },
      },
    },
  },
});

export default theme;








