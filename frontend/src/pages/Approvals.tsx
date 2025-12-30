import React, { useEffect, useState } from 'react';
import {
  Container,
  Box,
  Typography,
  Card,
  CardContent,
  CardActions,
  Button,
  Chip,
  Grid,
  CircularProgress,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
} from '@mui/material';
import {
  Email as EmailIcon,
  Work as WorkIcon,
  Chat as ChatIcon,
  CheckCircle as CheckIcon,
  Cancel as CancelIcon,
} from '@mui/icons-material';
import apiClient from '../api/client';

interface ApprovalRequest {
  request_id: string;
  action: string;
  title: string;
  description: string;
  data: any;
  status: string;
  created_at: string;
}

const Approvals: React.FC = () => {
  const [requests, setRequests] = useState<ApprovalRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedRequest, setSelectedRequest] = useState<ApprovalRequest | null>(null);
  const [notes, setNotes] = useState('');
  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    loadPendingRequests();
  }, []);

  const loadPendingRequests = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await apiClient.getPendingApprovals();
      setRequests(data.requests || []);
    } catch (err: any) {
      setError(err.message || 'Failed to load approvals');
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async () => {
    if (!selectedRequest) return;

    setActionLoading(true);
    try {
      await apiClient.approveRequest(selectedRequest.request_id, notes);
      setRequests(requests.filter(r => r.request_id !== selectedRequest.request_id));
      handleCloseDialog();
    } catch (err: any) {
      setError(err.message || 'Failed to approve request');
    } finally {
      setActionLoading(false);
    }
  };

  const handleReject = async () => {
    if (!selectedRequest) return;

    setActionLoading(true);
    try {
      await apiClient.rejectRequest(selectedRequest.request_id, notes);
      setRequests(requests.filter(r => r.request_id !== selectedRequest.request_id));
      handleCloseDialog();
    } catch (err: any) {
      setError(err.message || 'Failed to reject request');
    } finally {
      setActionLoading(false);
    }
  };

  const handleOpenDialog = (request: ApprovalRequest) => {
    setSelectedRequest(request);
    setNotes('');
  };

  const handleCloseDialog = () => {
    setSelectedRequest(null);
    setNotes('');
  };

  const getActionIcon = (action: string) => {
    switch (action) {
      case 'SEND_EMAIL':
        return <EmailIcon />;
      case 'APPLY_TO_JOB':
        return <WorkIcon />;
      case 'SEND_OUTREACH':
        return <ChatIcon />;
      default:
        return <CheckIcon />;
    }
  };

  const getActionColor = (action: string) => {
    switch (action) {
      case 'SEND_EMAIL':
        return 'primary';
      case 'APPLY_TO_JOB':
        return 'success';
      case 'SEND_OUTREACH':
        return 'info';
      default:
        return 'default';
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        Pending Approvals
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        Review and approve automated actions
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {requests.length === 0 ? (
        <Box sx={{ textAlign: 'center', py: 8 }}>
          <CheckIcon sx={{ fontSize: 80, color: 'success.main', mb: 2 }} />
          <Typography variant="h6" color="text.secondary">
            No pending approvals
          </Typography>
          <Typography variant="body2" color="text.secondary">
            All actions have been reviewed
          </Typography>
        </Box>
      ) : (
        <Grid container spacing={3}>
          {requests.map((request) => (
            <Grid item xs={12} key={request.request_id}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <Box sx={{ mr: 2 }}>
                      {getActionIcon(request.action)}
                    </Box>
                    <Box sx={{ flexGrow: 1 }}>
                      <Typography variant="h6" component="div">
                        {request.title}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {request.description}
                      </Typography>
                    </Box>
                    <Chip
                      label={request.action.replace('_', ' ')}
                      color={getActionColor(request.action) as any}
                      size="small"
                    />
                  </Box>

                  <Box sx={{ bgcolor: 'grey.100', p: 2, borderRadius: 1 }}>
                    <Typography variant="body2" component="pre" sx={{ whiteSpace: 'pre-wrap' }}>
                      {JSON.stringify(request.data, null, 2)}
                    </Typography>
                  </Box>

                  <Typography variant="caption" color="text.secondary" sx={{ mt: 2, display: 'block' }}>
                    Requested: {new Date(request.created_at).toLocaleString()}
                  </Typography>
                </CardContent>

                <CardActions sx={{ justifyContent: 'flex-end', px: 2, pb: 2 }}>
                  <Button
                    startIcon={<CancelIcon />}
                    onClick={() => handleOpenDialog(request)}
                    color="error"
                  >
                    Reject
                  </Button>
                  <Button
                    variant="contained"
                    startIcon={<CheckIcon />}
                    onClick={() => handleOpenDialog(request)}
                    color="success"
                  >
                    Approve
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      <Dialog open={selectedRequest !== null} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>
          {selectedRequest?.title}
        </DialogTitle>
        <DialogContent>
          <Typography variant="body2" sx={{ mb: 2 }}>
            {selectedRequest?.description}
          </Typography>
          <TextField
            fullWidth
            multiline
            rows={3}
            label="Notes (optional)"
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Add any notes about this decision..."
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog} disabled={actionLoading}>
            Cancel
          </Button>
          <Button
            onClick={handleReject}
            color="error"
            disabled={actionLoading}
          >
            Reject
          </Button>
          <Button
            onClick={handleApprove}
            variant="contained"
            color="success"
            disabled={actionLoading}
          >
            {actionLoading ? 'Processing...' : 'Approve'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default Approvals;
