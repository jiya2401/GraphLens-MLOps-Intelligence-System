/**
 * Custom React Flow Edge with animated flow particles.
 */

import { memo } from 'react';
import { BaseEdge, getSmoothStepPath, type EdgeProps } from '@xyflow/react';

function CustomEdgeComponent(props: EdgeProps) {
  const { sourceX, sourceY, targetX, targetY, sourcePosition, targetPosition, style, data } = props;

  const [edgePath] = getSmoothStepPath({
    sourceX, sourceY, targetX, targetY,
    sourcePosition, targetPosition,
    borderRadius: 16,
  });

  const isFailurePath = (data as Record<string, unknown>)?.isFailurePath as boolean;

  return (
    <>
      <BaseEdge
        path={edgePath}
        style={{
          ...style,
          strokeWidth: isFailurePath ? 3 : 2,
          stroke: isFailurePath ? 'var(--status-failed)' : 'var(--text-muted)',
          opacity: isFailurePath ? 1 : 0.4,
          filter: isFailurePath ? 'drop-shadow(0 0 6px var(--status-failed))' : 'none',
        }}
      />
      {/* Animated dot along the edge */}
      <circle r={3} fill={isFailurePath ? 'var(--status-failed)' : 'var(--accent-primary)'}>
        <animateMotion dur={isFailurePath ? '1.5s' : '3s'} repeatCount="indefinite" path={edgePath} />
      </circle>
    </>
  );
}

export const CustomEdge = memo(CustomEdgeComponent);
