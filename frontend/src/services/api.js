import axios from 'axios';

// Auth
export const authService = {
  register: async (userData) => {
    const response = await axios.post(`/api/auth/register`, userData);
    return response.data;
  },
  login: async (credentials) => {
    const response = await axios.post(`/api/auth/token`, credentials);
    return response.data;
  },
};

// Expenses
export const expenseService = {
  uploadReceipt: async (formData) => {
    const response = await axios.post(`/api/expenses/upload-receipt/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
  listExpenses: async () => {
    const response = await axios.get(`/api/expenses/list/`);
    return response.data;
  },
};

// Tax Alerts
export const taxService = {
  getAlerts: async () => {
    const response = await axios.get(`/api/tax-alerts/alerts/`);
    return response.data;
  },
  calculateLiability: async (data) => {
    const response = await axios.post(`/api/tax-alerts/calculate-liability/`, data);
    return response.data;
  },
};

// Forecasting
export const forecastingService = {
  predictTaxLiability: async () => {
    const response = await axios.get(`/api/forecasting/tax-liability-prediction/`);
    return response.data;
  },
  getCashFlowInsights: async () => {
    const response = await axios.get(`/api/forecasting/cash-flow-insights/`);
    return response.data;
  },
};
