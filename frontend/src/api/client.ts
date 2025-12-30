import axios, { AxiosInstance, AxiosError } from 'axios';

// In dev, default to localhost backend. In production (Docker/nginx), prefer same-origin
// so nginx can proxy `/api/*` to the backend container.
const API_BASE_URL =
  import.meta.env.VITE_API_URL || (import.meta.env.PROD ? '' : 'http://localhost:8000');

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add auth token
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Unauthorized - clear token and redirect to login
          localStorage.removeItem('token');
          localStorage.removeItem('user');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Authentication
  async register(email: string, password: string, name: string) {
    const response = await this.client.post('/api/v1/auth/register', {
      email,
      password,
      name,
    });
    return response.data;
  }

  async login(email: string, password: string) {
    const response = await this.client.post('/api/v1/auth/login', {
      email,
      password,
    });
    return response.data;
  }

  async getCurrentUser() {
    const response = await this.client.get('/api/v1/auth/me');
    return response.data;
  }

  async updateProfile(data: any) {
    const response = await this.client.put('/api/v1/auth/me', data);
    return response.data;
  }

  // Jobs
  async searchJobs(params: {
    keywords?: string;
    location?: string;
    source?: string;
    limit?: number;
  }) {
    const response = await this.client.get('/api/v1/jobs/search', { params });
    return response.data;
  }

  async getJobs(params?: any) {
    const response = await this.client.get('/api/v1/jobs', { params });
    return response.data;
  }

  async getJob(jobId: string) {
    const response = await this.client.get(`/api/v1/jobs/${jobId}`);
    return response.data;
  }

  async createJob(data: any) {
    const response = await this.client.post('/api/v1/jobs', data);
    return response.data;
  }

  async updateJob(jobId: string, data: any) {
    const response = await this.client.put(`/api/v1/jobs/${jobId}`, data);
    return response.data;
  }

  async deleteJob(jobId: string) {
    const response = await this.client.delete(`/api/v1/jobs/${jobId}`);
    return response.data;
  }

  // Approvals
  async getPendingApprovals() {
    const response = await this.client.get('/api/v1/approvals/pending');
    return response.data;
  }

  async getAllApprovals() {
    const response = await this.client.get('/api/v1/approvals/user/all');
    return response.data;
  }

  async getApproval(approvalId: string) {
    const response = await this.client.get(`/api/v1/approvals/${approvalId}`);
    return response.data;
  }

  async approveRequest(approvalId: string, notes?: string) {
    const response = await this.client.post(
      `/api/v1/approvals/${approvalId}/approve`,
      { notes }
    );
    return response.data;
  }

  async rejectRequest(approvalId: string, notes?: string) {
    const response = await this.client.post(
      `/api/v1/approvals/${approvalId}/reject`,
      { notes }
    );
    return response.data;
  }

  async cancelRequest(approvalId: string) {
    const response = await this.client.delete(`/api/v1/approvals/${approvalId}`);
    return response.data;
  }

  // Documents
  async generateCoverLetter(data: {
    profile: any;
    job: any;
    company_info?: string;
  }) {
    const response = await this.client.post('/api/v1/documents/cover-letter', data);
    return response.data;
  }

  async tailorResume(data: { profile: any; job: any }) {
    const response = await this.client.post('/api/v1/documents/tailor-resume', data);
    return response.data;
  }

  // Analytics
  async getAnalytics() {
    const response = await this.client.get('/api/v1/analytics');
    return response.data;
  }
}

export default new ApiClient();
