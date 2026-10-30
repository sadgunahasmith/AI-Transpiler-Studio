import axios from 'axios';

const API_BASE = '/api';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getLanguages = async () => {
  const resp = await api.get('/languages');
  return resp.data;
};

export const getSamples = async () => {
  const resp = await api.get('/samples');
  return resp.data;
};

export const getSystemInfo = async () => {
  const resp = await api.get('/system-info');
  return resp.data;
};

export const analyzeCode = async (language, code) => {
  const resp = await api.post('/analyze', { language, code });
  return resp.data;
};

export const detectErrors = async (language, code) => {
  const resp = await api.post('/detect-errors', { language, code });
  return resp.data;
};

export const autoCorrectCode = async (language, code, compiler_errors = null) => {
  const resp = await api.post('/correct', { language, code, compiler_errors });
  return resp.data;
};

export const transpileCode = async (source_language, target_language, code, optimize = true, ai_mode = "compiler_only") => {
  const resp = await api.post('/transpile', {
    source_language,
    target_language,
    code,
    optimize,
    ai_mode,
  });
  return resp.data;
};

export const executeCode = async (language, code, stdin = "") => {
  const resp = await api.post('/execute', { language, code, stdin });
  return resp.data;
};

export const compareExecutions = async (source_language, target_language, source_code, target_code, stdin = "") => {
  const resp = await api.post('/compare', {
    source_language,
    target_language,
    source_code,
    target_code,
    stdin,
  });
  return resp.data;
};

export const getHistory = async () => {
  const resp = await api.get('/history');
  return resp.data;
};

export const clearHistory = async () => {
  const resp = await api.delete('/history');
  return resp.data;
};

export default api;
