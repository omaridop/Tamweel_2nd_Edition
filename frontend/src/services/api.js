const BASE_URL = 'http://localhost:8000';

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
        },
        body: JSON.stringify(financialData),
      });

      if (!response.ok) {
        throw new Error('Failed to fetch credit score');
      }

      return await response.json();
    } catch (error) {
      console.error('Scoring Service Error:', error);
      throw error;
    }
  },

  /**
   * Fetch all results for Sponsor Dashboard
   */
  getAllResults: async () => {
    try {
      const response = await fetch(`${BASE_URL}/api/v1/results/all_users`);
      if (!response.ok) {
        throw new Error('Failed to fetch portfolio data');
      }
      return await response.json();
    } catch (error) {
      console.error('All Results Fetch Error:', error);
      throw error;
    }
  },

  /**
   * Fetch historical results for a user
   */
  getUserResults: async (userId) => {
    try {
      const response = await fetch(`${BASE_URL}/api/v1/results/${userId}`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch user history');
      }

      return await response.json();
    } catch (error) {
      console.error('History Fetch Error:', error);
      throw error;
    }
  },

  /**
   * Check if backend is alive
   */
  checkHealth: async () => {
    try {
      const response = await fetch(`${BASE_URL}/health`);
      return response.ok;
    } catch (error) {
      return false;
    }
  },

  /**
   * Chat with AI about credit score
   */
  chat: async (userId, message, role = 'user') => {
    try {
      const response = await fetch(`${BASE_URL}/api/v1/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ user_id: userId, message, role }),
      });

      if (!response.ok) {
        throw new Error('Failed to chat with AI');
      }

      return await response.json();
    } catch (error) {
      console.error('Chat Service Error:', error);
      throw error;
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
  }
};
