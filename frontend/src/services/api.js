const BASE_URL = import.meta.env.VITE_API_URL;

const getAuthHeaders = () => {
  try {
    const storageStr = localStorage.getItem('tamweel-auth-storage');
    if (storageStr) {
      const state = JSON.parse(storageStr).state;
      if (state && state.token) {
        return { 'Authorization': `Bearer ${state.token}` };
      }
    }
  } catch {
    console.error('Failed to parse auth token');
  }
  return {};
};

export const fetchWithAuth = async (endpoint, options = {}) => {
  const headers = new Headers(options.headers || {});
  
  if (!headers.has('Content-Type') && !(options.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json');
  }
  
  const authHeaders = getAuthHeaders();
  if (authHeaders.Authorization) {
    headers.set('Authorization', authHeaders.Authorization);
  } else {
    const token = sessionStorage.getItem('tamweel_token');
    if (token) {
      headers.set('Authorization', `Bearer ${token}`);
    }
  }

  const config = {
    ...options,
    headers,
  };

  const response = await fetch(`${BASE_URL}/api/v1${endpoint}`, config);
  
  if (!response.ok) {
    if (response.status === 401) {
      console.warn("Unauthorized request, clearing session...");
      sessionStorage.removeItem('tamweel_token');
      localStorage.removeItem('tamweel-auth-storage');
      window.dispatchEvent(new Event('auth-expired'));
    }
    const errorBody = await response.json().catch(() => ({}));
    throw new Error(errorBody.message || `API Error: ${response.status}`);
  }
  
  return response.json();
};




export const scoringService = {
  /**
   * Request a new credit score based on user data
   */
  getScore: async (financialData) => {
    try {
      const response = await fetch(`${BASE_URL}/api/v1/score`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...getAuthHeaders(),
        },
        body: JSON.stringify(financialData),
      });

      if (!response.ok) {
        throw new Error('Failed to fetch credit score');
      }

      return await response.json();
    } catch (e) {
      console.error('Scoring Service Error:', e);
      throw e;
    }
  },

  /**
   * Fetch all results for Sponsor Dashboard
   */
  getAllResults: async () => {
    try {
      const response = await fetch(`${BASE_URL}/api/v1/results/all_users`, {
        headers: getAuthHeaders(),
      });
      if (!response.ok) {
        throw new Error('Failed to fetch portfolio data');
      }
      return await response.json();
    } catch (e) {
      console.error('All Results Fetch Error:', e);
      throw e;
    }
  },

  /**
   * Fetch historical results for a user
   */
  getUserResults: async (userId) => {
    try {
      const response = await fetch(`${BASE_URL}/api/v1/results/${userId}`, {
        headers: getAuthHeaders(),
      });
      
      if (!response.ok) {
        throw new Error('Failed to fetch user history');
      }

      return await response.json();
    } catch (e) {
      console.error('History Fetch Error:', e);
      throw e;
    }
  },

  /**
   * Check if backend is alive
   */
  checkHealth: async () => {
    try {
      const response = await fetch(`${BASE_URL}/health`);
      return response.ok;
    } catch {
      return false;
    }
  },

  /**
   * Chat with AI about credit score
   */
  chat: async (userId, message, role = 'user', history = [], signal) => {
    try {
      return await fetchWithAuth('/chat', {
        method: 'POST',
        body: JSON.stringify({ user_id: userId, message, role, history }),
        signal,
      });
    } catch (error) {
      console.error('Chat Service Error:', error);
      throw error;
    }
  },

  /**
   * Streaming chat — calls /api/v1/chat/stream (SSE).
   * @param {string}   userId
   * @param {string}   message
   * @param {string}   role
   * @param {Array}    history
   * @param {Function} onToken  — called with each string token as it arrives
   * @param {Function} onDone   — called once with the final meta object {sources, confidence, ...}
   * @param {AbortSignal} signal
   */
  chatStream: async (userId, message, role = 'user', history = [], onToken, onDone, signal) => {
    const authHeaders = getAuthHeaders();
    const response = await fetch(`${BASE_URL}/api/v1/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...authHeaders,
      },
      body: JSON.stringify({ user_id: userId, message, role, history }),
      signal,
    });

    if (!response.ok) {
      const errorBody = await response.json().catch(() => ({}));
      throw new Error(errorBody.detail || `Stream Error: ${response.status}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop(); // keep incomplete line in buffer

      for (const line of lines) {
        if (!line.startsWith('data: ')) continue;
        try {
          const parsed = JSON.parse(line.slice(6));
          if (parsed.done) {
            onDone && onDone(parsed.meta);
          } else if (parsed.token !== undefined) {
            onToken && onToken(parsed.token);
          }
        } catch {
          // ignore malformed SSE lines
        }
      }
    }
  },

  /**
   * Register a new user
   */
  register: async (userData) => {
    try {
      const response = await fetch(`${BASE_URL}/api/v1/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to register');
      }

      return await response.json();
    } catch (error) {
      console.error('Register Service Error:', error);
      throw error;
    }
  },

  /**
   * Login user
   */
  login: async (credentials) => {
    try {
      const response = await fetch(`${BASE_URL}/api/v1/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Invalid credentials');
      }

      return await response.json();
    } catch (error) {
      console.error('Login Service Error:', error);
      throw error;
    }
  },

  /**
   * Generate Improvement Plan
   */
  generateImprovementPlan: async (userId, email) => {
    try {
      const response = await fetch(`${BASE_URL}/api/v1/ai/improvement-plan`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...getAuthHeaders(),
        },
        body: JSON.stringify({ user_id: userId, email }),
      });

      if (!response.ok) {
        throw new Error('Failed to generate improvement plan');
      }

      return await response.json();
    } catch (error) {
      console.error('Improvement Plan Service Error:', error);
      throw error;
    }
  },

  /**
   * Generate a structured 90-day credit score improvement roadmap
   */
  generateRoadmap: async (userId, email) => {
    try {
      const response = await fetch(`${BASE_URL}/api/v1/ai/roadmap`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...getAuthHeaders(),
        },
        body: JSON.stringify({ user_id: userId, email }),
      });

      if (!response.ok) {
        throw new Error('Failed to generate roadmap');
      }

      return await response.json();
    } catch (error) {
      console.error('Roadmap Service Error:', error);
      throw error;
    }
  },

  /**
   * Upload a policy PDF file
   */
  uploadPolicy: async (file) => {
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${BASE_URL}/api/v1/admin/upload-policy`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to upload policy');
      }

      return await response.json();
    } catch (error) {
      console.error('Upload Policy Error:', error);
      throw error;
    }
  }
};
