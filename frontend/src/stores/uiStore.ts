/**
 * UI Store — global UI state (sidebar, theme, active page).
 */

import { create } from 'zustand';

interface UIStore {
  sidebarOpen: boolean;
  activePage: string;

  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
  setActivePage: (page: string) => void;
}

export const useUIStore = create<UIStore>((set) => ({
  sidebarOpen: true,
  activePage: 'graph-explorer',

  toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
  setSidebarOpen: (sidebarOpen) => set({ sidebarOpen }),
  setActivePage: (activePage) => set({ activePage }),
}));
