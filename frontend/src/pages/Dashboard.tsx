import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  AppBar,
  Toolbar,
  IconButton,
  Menu,
  MenuItem,
} from '@mui/material';
import {
  Work as WorkIcon,
  CheckCircle as CheckCircleIcon,
  PendingActions as PendingActionsIcon,
  Description as DescriptionIcon,
  AccountCircle,
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import apiClient from '../api/client';

interface DashboardStats {
  total_jobs: number;
  pending_approvals: number;
  applications_sent: number;
  documents_generated: number;
}

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [stats, setStats] = useState<DashboardStats>({
    total_jobs: 0,
    pending_approvals: 0,
    applications_sent: 0,
    documents_generated: 0,
  });
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const data = await apiClient.getAnalytics();
      setStats({
        total_jobs: data.total_jobs || 0,
        pending_approvals: data.pending_approvals || 0,
        applications_sent: data.applications_sent || 0,
        documents_generated: data.documents_generated || 0,
      });
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  };

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const statCards = [
    {
      title: 'Saved Jobs',
      value: stats.total_jobs,
      icon: <WorkIcon sx={{ fontSize: 40 }} />,
      color: '#1976d2',
      action: () => navigate('/jobs'),
    },
    {
      title: 'Pending Approvals',
      value: stats.pending_approvals,
      icon: <PendingActionsIcon sx={{ fontSize: 40 }} />,
      color: '#ed6c02',
      action: () => navigate('/approvals'),
    },
    {
      title: 'Applications Sent',
      value: stats.applications_sent,
      icon: <CheckCircleIcon sx={{ fontSize: 40 }} />,
      color: '#2e7d32',
      action: () => navigate('/jobs'),
    },
    {
      title: 'Documents Created',
      value: stats.documents_generated,
      icon: <DescriptionIcon sx={{ fontSize: 40 }} />,
      color: '#9c27b0',
      action: () => navigate('/documents'),
    },
  ];

  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Jobly
          </Typography>
          <Button color="inherit" onClick={() => navigate('/dashboard')}>
            Dashboard
          </Button>
          <Button color="inherit" onClick={() => navigate('/jobs')}>
            Jobs
          </Button>
          <Button color="inherit" onClick={() => navigate('/approvals')}>
            Approvals
          </Button>
          <IconButton
            size="large"
            edge="end"
            color="inherit"
            onClick={handleMenuOpen}
          >
            <AccountCircle />
          </IconButton>
          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleMenuClose}
          >
            <MenuItem onClick={() => { handleMenuClose(); navigate('/profile'); }}>
              Profile
            </MenuItem>
            <MenuItem onClick={handleLogout}>Logout</MenuItem>
          </Menu>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Box sx={{ mb: 4 }}>
          <Typography variant="h4" gutterBottom>
            Welcome back, {user?.name}!
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Here's your job search overview
          </Typography>
        </Box>

        <Grid container spacing={3}>
          {statCards.map((card, index) => (
            <Grid item xs={12} sm={6} md={3} key={index}>
              <Card
                sx={{
                  cursor: 'pointer',
                  transition: 'transform 0.2s',
                  '&:hover': {
                    transform: 'scale(1.05)',
                  },
                }}
                onClick={card.action}
              >
                <CardContent>
                  <Box
                    sx={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      mb: 2,
                    }}
                  >
                    <Box sx={{ color: card.color }}>{card.icon}</Box>
                    <Typography variant="h3" component="div">
                      {card.value}
                    </Typography>
                  </Box>
                  <Typography variant="h6" color="text.secondary">
                    {card.title}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>

        <Box sx={{ mt: 4 }}>
          <Grid container spacing={2}>
            <Grid item xs={12} md={4}>
              <Button
                variant="contained"
                fullWidth
                size="large"
                onClick={() => navigate('/jobs/search')}
                sx={{ py: 2 }}
              >
                Search New Jobs
              </Button>
            </Grid>
            <Grid item xs={12} md={4}>
              <Button
                variant="outlined"
                fullWidth
                size="large"
                onClick={() => navigate('/documents/generate')}
                sx={{ py: 2 }}
              >
                Generate Cover Letter
              </Button>
            </Grid>
            <Grid item xs={12} md={4}>
              <Button
                variant="outlined"
                fullWidth
                size="large"
                onClick={() => navigate('/approvals')}
                sx={{ py: 2 }}
              >
                Review Pending Actions
              </Button>
            </Grid>
          </Grid>
        </Box>
      </Container>
    </Box>
  );
};

export default Dashboard;
