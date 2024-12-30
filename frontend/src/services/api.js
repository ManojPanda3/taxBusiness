import axios from 'axios';

const API_URL = 'http://127.0.0.1:8000/api'; // Base API URL

// Auth
export const authService = {
  register: async (userData) => {
    const response = await axios.post(`${API_URL}/auth/register`, userData);
    return response.data;
  },
  login: async (credentials) => {
    const response = await axios.post(`${API_URL}/auth/token`, credentials);
    return response.data;
  },
};

// Expenses
export const expenseService = {
  uploadReceipt: async (formData) => {
    const response = await axios.post(`${API_URL}/expenses/upload-receipt/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
  listExpenses: async () => {
    const response = await axios.get(`${API_URL}/expenses/list/`);
    return response.data;
  },
};

// Tax Alerts
export const taxService = {
  getAlerts: async () => {
    const response = await axios.get(`${API_URL}/tax-alerts/alerts/`);
    return response.data;
  },
  calculateLiability: async (data) => {
    const response = await axios.post(`${API_URL}/tax-alerts/calculate-liability/`, data);
    return response.data;
  },
};

// Forecasting
export const forecastingService = {
  predictTaxLiability: async () => {
    const response = await axios.get(`${API_URL}/forecasting/tax-liability-prediction/`);
    return response.data;
  },
  getCashFlowInsights: async () => {
    const response = await axios.get(`${API_URL}/forecasting/cash-flow-insights/`);
    return response.data;
  },
};
