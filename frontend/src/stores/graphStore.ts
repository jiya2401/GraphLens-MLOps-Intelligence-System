/**
 * Graph Store — Zustand state management for graph data.
 *
 * Zustand creates a "store" — a global state container that any
 * React component can read from. When the store updates, only
 * components reading the changed values re-render.
 *
 * Interview Q: "How does Zustand compare to Redux?"
 * Answer: Both are global state managers. Redux uses actions + reducers
 * (lots of boilerplate). Zustand uses simple set() calls.
 * Zustand is 1kb vs Redux's ~7kb. Both support middleware and devtools.
 */

import { create } from 'zustand';
import type { GraphData, GraphListItem, GraphNode } from '../types/graph';

interface GraphStore {
  // Data
  graphs: GraphListItem[];
  currentGraph: GraphData | null;
  selectedNode: GraphNode | null;
  selectedGraphId: number;
  selectedTimestep: number;

  // UI State
  searchQuery: string;
  healthFilter: string[];
  isLoading: boolean;
  error: string | null;

  // Actions
  setGraphs: (graphs: GraphListItem[]) => void;
  setCurrentGraph: (graph: GraphData | null) => void;
  setSelectedNode: (node: GraphNode | null) => void;
  setSelectedGraphId: (id: number) => void;
  setSelectedTimestep: (timestep: number) => void;
  setSearchQuery: (query: string) => void;
  setHealthFilter: (filters: string[]) => void;
  toggleHealthFilter: (health: string) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

export const useGraphStore = create<GraphStore>((set) => ({
  // Initial state
  graphs: [],
  currentGraph: null,
  selectedNode: null,
  selectedGraphId: 0,
  selectedTimestep: 0,
  searchQuery: '',
  healthFilter: [],
  isLoading: false,
  error: null,

  // Setters
  setGraphs: (graphs) => set({ graphs }),
  setCurrentGraph: (currentGraph) => set({ currentGraph }),
  setSelectedNode: (selectedNode) => set({ selectedNode }),
  setSelectedGraphId: (selectedGraphId) => set({ selectedGraphId, selectedTimestep: 0, selectedNode: null }),
  setSelectedTimestep: (selectedTimestep) => set({ selectedTimestep }),
  setSearchQuery: (searchQuery) => set({ searchQuery }),
  setHealthFilter: (healthFilter) => set({ healthFilter }),
  toggleHealthFilter: (health) =>
    set((state) => {
      const current = state.healthFilter;
      const next = current.includes(health)
        ? current.filter((h) => h !== health)
        : [...current, health];
      return { healthFilter: next };
    }),
  setLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error }),
}));
