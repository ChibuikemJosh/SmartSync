import { BASE_URL } from '../config';

async function parseResponse(response) {
  const text = await response.text();
  let data = {};

  try {
    data = text ? JSON.parse(text) : {};
  } catch {
    data = { detail: text };
  }

  if (!response.ok) {
    const message = data.detail || data.message || 'Request failed';
    throw new Error(message);
  }

  return data;
}

async function request(path, options = {}) {
  const token = localStorage.getItem('token');
  const skipAuth = options.skipAuth === true;
  const headers = {
    Accept: 'application/json',
    ...(options.headers || {}),
  };

  if (token && !skipAuth) {
    headers.Authorization = `Bearer ${token}`;
  }

  console.log(`DEBUG: Dispatching ${options.method || 'GET'} ${BASE_URL.replace(/\/$/, '')}${path}`);

  const response = await fetch(`${BASE_URL.replace(/\/$/, '')}${path}`, {
    ...options,
    headers,
  });

  const data = await parseResponse(response);
  console.log(`DEBUG: Response ${path}`, data);
  return data;
}

export async function loginRequest(email, password) {
  const body = new URLSearchParams();
  body.set('username', email);
  body.set('password', password);

  return request('/auth/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    skipAuth: true,
    body,
  });
}

export async function registerRequest(userData) {
  return request('/auth/auth/register', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    skipAuth: true,
    body: JSON.stringify(userData),
  });
}

export async function fetchMeRequest() {
  return request('/auth/auth/me');
}

export async function processVoiceRequest(file) {
  const formData = new FormData();
  formData.append('file', file);

  return request('/ai/ai/process-voice', {
    method: 'POST',
    body: formData,
  });
}

export async function processLedgerRequest(file) {
  const formData = new FormData();
  formData.append('file', file);

  return request('/ai/ai/process-ledger', {
    method: 'POST',
    body: formData,
  });
}

export async function fetchAiStatusRequest(jobId) {
  return request(`/ai/ai/status/${jobId}`);
}

export async function confirmTransactionRequest(payload) {
  return request('/ai/ai/confirm-transaction', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });
}

export async function createVirtualAccountRequest(payload) {
  return request('/payments/create-virtual-account', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });
}

export async function generatePaymentLinkRequest(payload) {
  return request('/payments/generate-payment-link', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });
}

export async function withdrawRequest(payload) {
  return request('/payments/withdraw', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });
}

export async function chatRequest(payload) {
  return request('/chat/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });
}
