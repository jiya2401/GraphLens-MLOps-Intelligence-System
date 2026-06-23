/**
 * Timeline Store — state for temporal replay engine.
 */

import { create } from 'zustand';
import type { TimelineData } from '../types/graph';

interface TimelineStore {
  timelineData: TimelineData | null;
  currentTimestep: number;
  isPlaying: boolean;
  playbackSpeed: number;
  isLoading: boolean;

  setTimelineData: (data: TimelineData | null) => void;
  setCurrentTimestep: (t: number) => void;
  setIsPlaying: (playing: boolean) => void;
  setPlaybackSpeed: (speed: number) => void;
  setLoading: (loading: boolean) => void;
  nextTimestep: () => void;
  prevTimestep: () => void;
  reset: () => void;
}

export const useTimelineStore = create<TimelineStore>((set, get) => ({
  timelineData: null,
  currentTimestep: 0,
  isPlaying: false,
  playbackSpeed: 1,
  isLoading: false,

  setTimelineData: (timelineData) => set({ timelineData, currentTimestep: 0 }),
  setCurrentTimestep: (currentTimestep) => set({ currentTimestep }),
  setIsPlaying: (isPlaying) => set({ isPlaying }),
  setPlaybackSpeed: (playbackSpeed) => set({ playbackSpeed }),
  setLoading: (isLoading) => set({ isLoading }),

  nextTimestep: () => {
    const { timelineData, currentTimestep } = get();
    if (!timelineData) return;
    const max = timelineData.total_timesteps - 1;
    if (currentTimestep < max) {
      set({ currentTimestep: currentTimestep + 1 });
    } else {
      set({ isPlaying: false });
    }
  },

  prevTimestep: () => {
    const { currentTimestep } = get();
    if (currentTimestep > 0) {
      set({ currentTimestep: currentTimestep - 1 });
    }
  },

  reset: () =>
    set({
      timelineData: null,
      currentTimestep: 0,
      isPlaying: false,
    }),
}));
