import React, { useEffect, useState } from 'react';
import {
  Container,
  Box,
  Typography,
  TextField,
  Button,
  Grid,
  Card,
  CardContent,
  CardActions,
  Chip,
  CircularProgress,
  Alert,
  InputAdornment,
} from '@mui/material';
import {
  Search as SearchIcon,
  LocationOn as LocationIcon,
  Business as BusinessIcon,
} from '@mui/icons-material';
import apiClient from '../api/client';

interface Job {
  job_id: string;
  title: string;
  company: string;
  location?: string;
  description?: string;
  url?: string;
  match_score?: number;
  skills?: string[];
  salary_range?: string;
  created_at?: string;
}

const Jobs: React.FC = () => {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [keywords, setKeywords] = useState('');
  const [location, setLocation] = useState('');

  useEffect(() => {
    loadJobs();
  }, []);

  const loadJobs = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await apiClient.searchJobs({});
      setJobs(data.jobs || []);
    } catch (err: any) {
      setError(err.message || 'Failed to load jobs');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const data = await apiClient.searchJobs({ keywords, location });
      setJobs(data.jobs || []);
    } catch (err: any) {
      setError(err.message || 'Search failed');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveJob = async (jobId: string) => {
    try {
      await apiClient.updateJob(jobId, { saved: true });
      setJobs(jobs.map(job =>
        job.job_id === jobId ? { ...job } : job
      ));
    } catch (err: any) {
      console.error('Failed to save job:', err);
    }
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        Job Search
      </Typography>

      <Box component="form" onSubmit={handleSearch} sx={{ mb: 4 }}>
        <Grid container spacing={2}>
          <Grid item xs={12} md={5}>
            <TextField
              fullWidth
              placeholder="Job title, keywords, or company"
              value={keywords}
              onChange={(e) => setKeywords(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon />
                  </InputAdornment>
                ),
              }}
            />
          </Grid>
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              placeholder="City, state, or remote"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <LocationIcon />
                  </InputAdornment>
                ),
              }}
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <Button
              type="submit"
              variant="contained"
              fullWidth
              size="large"
              disabled={loading}
            >
              {loading ? 'Searching...' : 'Search'}
            </Button>
          </Grid>
        </Grid>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {loading && !jobs.length ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
          <CircularProgress />
        </Box>
      ) : (
        <Grid container spacing={3}>
          {jobs.length === 0 ? (
            <Grid item xs={12}>
              <Box sx={{ textAlign: 'center', py: 8 }}>
                <Typography variant="h6" color="text.secondary">
                  No jobs found. Try searching with different keywords.
                </Typography>
              </Box>
            </Grid>
          ) : (
            jobs.map((job) => (
              <Grid item xs={12} key={job.job_id}>
                <Card>
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                      <Typography variant="h6" component="div">
                        {job.title}
                      </Typography>
                      {job.match_score !== undefined && (
                        <Chip
                          label={`${Math.round(job.match_score * 100)}% Match`}
                          color={job.match_score > 0.7 ? 'success' : 'default'}
                          size="small"
                        />
                      )}
                    </Box>

                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      <BusinessIcon sx={{ mr: 1, fontSize: 20, color: 'text.secondary' }} />
                      <Typography variant="body1" color="text.secondary">
                        {job.company}
                      </Typography>
                    </Box>

                    {job.location && (
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                        <LocationIcon sx={{ mr: 1, fontSize: 20, color: 'text.secondary' }} />
                        <Typography variant="body2" color="text.secondary">
                          {job.location}
                        </Typography>
                      </Box>
                    )}

                    {job.salary_range && (
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                        {job.salary_range}
                      </Typography>
                    )}

                    {job.description && (
                      <Typography variant="body2" sx={{ mb: 2 }}>
                        {job.description.substring(0, 200)}
                        {job.description.length > 200 ? '...' : ''}
                      </Typography>
                    )}

                    {job.skills && job.skills.length > 0 && (
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                        {job.skills.slice(0, 5).map((skill, index) => (
                          <Chip key={index} label={skill} size="small" />
                        ))}
                      </Box>
                    )}
                  </CardContent>

                  <CardActions sx={{ justifyContent: 'flex-end', px: 2, pb: 2 }}>
                    <Button size="small" onClick={() => handleSaveJob(job.job_id)}>
                      Save
                    </Button>
                    {job.url && (
                      <Button
                        size="small"
                        variant="outlined"
                        href={job.url}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        View Job
                      </Button>
                    )}
                    <Button size="small" variant="contained">
                      Apply
                    </Button>
                  </CardActions>
                </Card>
              </Grid>
            ))
          )}
        </Grid>
      )}
    </Container>
  );
};

export default Jobs;
