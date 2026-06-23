/**
 * useGraphData — custom hook for fetching graph data from the API.
 *
 * Custom hooks are functions that start with "use" and can call other hooks.
 * They let you extract reusable logic from components.
 *
 * Interview Q: "What is a custom hook and why use one?"
 * Answer: A custom hook encapsulates stateful logic (data fetching,
 * subscriptions, timers) so multiple components can reuse it.
 * It follows the DRY principle and keeps components focused on rendering.
 */

import { useEffect } from 'react';
import { useGraphStore } from '../stores/graphStore';
import { fetchGraphList, fetchGraph } from '../services/api';

export function useGraphData() {
  const {
    graphs, setGraphs, currentGraph, setCurrentGraph,
    selectedGraphId, selectedTimestep,
    isLoading, setLoading, error, setError,
  } = useGraphStore();

  // Load graph list on mount
  useEffect(() => {
    let cancelled = false;
    async function load() {
      if (graphs.length > 0) return;
      setLoading(true);
      try {
        const data = await fetchGraphList();
        if (!cancelled) setGraphs(data.graphs);
      } catch (e) {
        if (!cancelled) setError(e instanceof Error ? e.message : 'Failed to load graphs');
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => { cancelled = true; };
  }, []);

  // Load selected graph when ID/timestep changes
  useEffect(() => {
    let cancelled = false;
    async function load() {
      setLoading(true);
      try {
        const data = await fetchGraph(selectedGraphId, selectedTimestep);
        if (!cancelled) {
          setCurrentGraph(data);
          setError(null);
        }
      } catch (e) {
        if (!cancelled) setError(e instanceof Error ? e.message : 'Failed to load graph');
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => { cancelled = true; };
  }, [selectedGraphId, selectedTimestep]);

  return { graphs, currentGraph, isLoading, error };
}
