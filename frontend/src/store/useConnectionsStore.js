import { create } from 'zustand';

// Mockup data for connected integrations
const MOCK_CONNECTIONS = [
  { id: '1', provider: 'ZainCash', type: 'E-Wallet', status: 'Active', lastSynced: '2 mins ago', logo: '💳' },
  { id: '2', provider: 'OrangeMoney', type: 'E-Wallet', status: 'Needs Re-auth', lastSynced: '5 days ago', logo: '📱' },
];

const AVAILABLE_PROVIDERS = [
  { id: 'zain', name: 'ZainCash', type: 'E-Wallet' },
  { id: 'orange', name: 'OrangeMoney', type: 'E-Wallet' },
  { id: 'cliq', name: 'Cliq', type: 'Bank Account' },
  { id: 'visa', name: 'Visa', type: 'Credit Card' },
  { id: 'mastercard', name: 'Mastercard', type: 'Credit Card' },
];

const useConnectionsStore = create((set, get) => ({
  connections: [],
  availableProviders: AVAILABLE_PROVIDERS,
  isLoading: false,
  error: null,

  fetchConnections: async () => {
    set({ isLoading: true, error: null });
    try {
      // Simulate network delay
      await new Promise(resolve => setTimeout(resolve, 800));
      set({ connections: MOCK_CONNECTIONS, isLoading: false });
    } catch {
      set({ error: 'Failed to fetch connections.', isLoading: false });
    }
  },

  addConnection: async (providerId) => {
    set({ isLoading: true, error: null });
    try {
      // Simulate OAuth flow network delay
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      const provider = get().availableProviders.find(p => p.id === providerId);
      if (!provider) throw new Error("Provider not found");

      const newConnection = {
        id: Date.now().toString(),
        provider: provider.name,
        type: provider.type,
        status: 'Active',
        lastSynced: 'Just now',
        logo: provider.type === 'E-Wallet' ? '📱' : '💳'
      };

      set((state) => ({
        connections: [...state.connections, newConnection],
        isLoading: false
      }));
    } catch {
      set({ error: 'Failed to add connection.', isLoading: false });
    }
  },

  revokeConnection: async (connectionId) => {
    set({ isLoading: true, error: null });
    try {
      await new Promise(resolve => setTimeout(resolve, 600));
      set((state) => ({
        connections: state.connections.filter(c => c.id !== connectionId),
        isLoading: false
      }));
    } catch {
      set({ error: 'Failed to revoke connection.', isLoading: false });
    }
  }
}));

export default useConnectionsStore;
