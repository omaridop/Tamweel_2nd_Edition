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
      currentDetailedAssessment: null,

      setDetailedAssessment: (assessment) => {
        set({ currentDetailedAssessment: assessment });
      },

      register: async (name, email, password) => {
        set({ isLoading: true });
        try {
          const result = await scoringService.register({ name, email, password });
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
          const { user, role } = response;
          set({ user, isAuthenticated: true, role, isLoading: false });
          return user;
        } catch (error) {
          set({ isLoading: false });
          throw error;
        }
      },

      logout: () => {
        set({ user: null, isAuthenticated: false, role: null });
      },
    }),
    {
      name: 'tamweel-auth-storage',
    }
  )
);

export default useAuthStore;
