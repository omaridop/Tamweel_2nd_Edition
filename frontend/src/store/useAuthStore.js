import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { scoringService } from '../services/api';

const useAuthStore = create(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      role: null, // 'user' or 'sponsor'
      token: null,
      currentDetailedAssessment: null,

      setDetailedAssessment: (assessment) => {
        set({ currentDetailedAssessment: assessment });
      },

      register: async (name, email, password) => {
        set({ isLoading: true });
        try {
          await scoringService.register({ name, email, password });
          const user = { id: Date.now().toString(), name, email };
          set({ user, isAuthenticated: true, role: 'user', isLoading: false });
          return user;
        } catch (error) {
          set({ isLoading: false });
          throw error;
        }
      },

      login: async (email, password) => {
        set({ isLoading: true });
        try {
          const response = await scoringService.login({ email, password });
          const { user, role, access_token } = response;
          set({ user, isAuthenticated: true, role, token: access_token, isLoading: false });
          return user;
        } catch (error) {
          set({ isLoading: false });
          throw error;
        }
      },

      logout: () => {
        set({ user: null, isAuthenticated: false, role: null, token: null });
      },
    }),
    {
      name: 'tamweel-auth-storage',
    }
  )
);

export default useAuthStore;
