import { useEffect, useRef } from 'react';
import { useTimelineStore } from '../stores/timelineStore';
import { fetchTimeline } from '../services/api';

export function useTimeline(graphId: number) {
  const { timelineData, setTimelineData, isPlaying, playbackSpeed, nextTimestep, setLoading, currentTimestep } = useTimelineStore();
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Load timeline data
  useEffect(() => {
    let cancelled = false;
    async function load() {
      setLoading(true);
      try {
        const data = await fetchTimeline(graphId);
        if (!cancelled) setTimelineData(data);
      } catch (e) {
        console.error('Timeline load error:', e);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => { cancelled = true; };
  }, [graphId]);

  // Playback timer
  useEffect(() => {
    if (isPlaying) {
      intervalRef.current = setInterval(() => {
        nextTimestep();
      }, 1500 / playbackSpeed);
    }
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [isPlaying, playbackSpeed, nextTimestep]);

  return { timelineData, currentTimestep };
}
