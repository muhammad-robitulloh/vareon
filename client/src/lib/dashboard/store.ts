import { create } from 'zustand';

interface SystemStatus {
  arcana: 'online' | 'offline' | 'degraded';
  myntrix: 'online' | 'offline' | 'degraded';
  neosyntis: 'online' | 'offline' | 'degraded';
  cognisys: 'online' | 'offline' | 'degraded';
}

interface WorkspaceState {
  currentModule: string;
  theme: 'dark' | 'light';
  performanceMode: boolean;
  systemStatus: SystemStatus;
  commandPaletteOpen: boolean;
  sidebarCollapsed: boolean;
  notifications: Array<{ id: string; message: string; type: 'info' | 'success' | 'error' | 'warning' }>;
  
  setCurrentModule: (module: string) => void;
  toggleTheme: () => void;
  togglePerformanceMode: () => void;
  setSystemStatus: (system: keyof SystemStatus, status: SystemStatus[keyof SystemStatus]) => void;
  toggleCommandPalette: () => void;
  toggleSidebar: () => void;
  addNotification: (message: string, type: 'info' | 'success' | 'error' | 'warning') => void;
  removeNotification: (id: string) => void;
}

export const useStore = create<WorkspaceState>((set) => ({
  currentModule: 'vareon',
  theme: typeof window !== 'undefined' && window.localStorage.getItem('theme') === 'light' ? 'light' : 'dark',
  performanceMode: false,
  systemStatus: {
    arcana: 'online',
    myntrix: 'online',
    neosyntis: 'online',
    cognisys: 'online',
  },
  commandPaletteOpen: false,
  sidebarCollapsed: false,
  notifications: [],

  setCurrentModule: (module) => set({ currentModule: module }),
  
  toggleTheme: () => set((state) => {
    const newTheme = state.theme === 'dark' ? 'light' : 'dark';
    if (typeof window !== 'undefined') {
      window.localStorage.setItem('theme', newTheme);
      document.documentElement.classList.toggle('dark', newTheme === 'dark');
    }
    return { theme: newTheme };
  }),
  
  togglePerformanceMode: () => set((state) => ({ performanceMode: !state.performanceMode })),
  
  setSystemStatus: (system, status) => set((state) => ({
    systemStatus: { ...state.systemStatus, [system]: status }
  })),
  
  toggleCommandPalette: () => set((state) => ({ commandPaletteOpen: !state.commandPaletteOpen })),
  
  toggleSidebar: () => set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),
  
  addNotification: (message, type) => set((state) => ({
    notifications: [...state.notifications, { id: Date.now().toString(), message, type }]
  })),
  
  removeNotification: (id) => set((state) => ({
    notifications: state.notifications.filter(n => n.id !== id)
  })),
}));

if (typeof window !== 'undefined') {
  const theme = useStore.getState().theme;
  document.documentElement.classList.toggle('dark', theme === 'dark');
}
