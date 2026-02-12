import axios from 'axios';

const API_BASE = 'http://localhost:8000';

const api = axios.create({
    baseURL: API_BASE,
    timeout: 60000,
    headers: { 'Content-Type': 'application/json' },
});

export const getHealth = () => api.get('/health');
export const getCohort = () => api.get('/cohort');
export const runAnalysis = (query) => api.post(`/analyze?query=${encodeURIComponent(query)}`);
export const getGraph = (company) => api.get('/graph', { params: company ? { company } : {} });
export const queryGraph = (question) => api.post(`/graph/query?question=${encodeURIComponent(question)}`);
export const getCommonPartners = (a, b) => api.get('/graph/common-partners', { params: { company_a: a, company_b: b } });
export const getExposure = (entity) => api.get('/graph/exposure', { params: { entity } });
export const getComparison = () => api.get('/comparison');
export const getSummary = () => api.get('/summary');
export const exportData = (fmt) => api.get(`/export/${fmt}`, { responseType: fmt === 'pdf' ? 'blob' : 'json' });

export default api;
