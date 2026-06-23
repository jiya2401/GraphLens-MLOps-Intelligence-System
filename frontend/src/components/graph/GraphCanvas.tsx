/**
 * Graph Canvas — the main React Flow graph visualization component.
 *
 * Uses dagre for automatic hierarchical layout of DAG nodes.
 * dagre is a JavaScript library for directed graph layout — it positions
 * nodes in a top-to-bottom or left-to-right hierarchy automatically.
 */

import { useCallback, useEffect, useMemo } from 'react';
import {
  ReactFlow, Background, Controls, MiniMap,
  useNodesState, useEdgesState,
  type Node, type Edge,
  BackgroundVariant,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import dagre from 'dagre';
import { CustomNode } from './CustomNode';
import { CustomEdge } from './CustomEdge';
import { useGraphStore } from '../../stores/graphStore';
import type { GraphData } from '../../types/graph';

const nodeTypes = { custom: CustomNode };
const edgeTypes = { custom: CustomEdge };

function getLayoutedElements(graphData: GraphData, selectedNodeId: string | null, searchQuery: string, healthFilter: string[]) {
  const g = new dagre.graphlib.Graph();
  g.setDefaultEdgeLabel(() => ({}));
  g.setGraph({ rankdir: 'LR', nodesep: 60, ranksep: 120 });

  const nodes: Node[] = graphData.nodes.map((node) => {
    const matchesSearch = searchQuery ? node.id.toLowerCase().includes(searchQuery.toLowerCase()) : false;
    const isFiltered = healthFilter.length > 0 && !healthFilter.includes(node.health);

    g.setNode(node.id, { width: 200, height: 140 });
    return {
      id: node.id,
      type: 'custom',
      position: { x: 0, y: 0 },
      data: {
        label: node.id,
        health: node.health,
        failed: node.failed,
        cpu_usage: node.telemetry.cpu_usage,
        memory_usage: node.telemetry.memory_usage,
        latency: node.telemetry.network_latency,
        anomaly_score: node.anomaly_score,
        isSelected: node.id === selectedNodeId,
        isSearchMatch: matchesSearch && searchQuery !== '',
        isFiltered,
      },
    };
  });

  const failedNodeIds = new Set(graphData.nodes.filter((n) => n.failed).map((n) => n.id));

  const edges: Edge[] = graphData.edges.map((edge, i) => {
    g.setEdge(edge.source, edge.target);
    const isFailurePath = failedNodeIds.has(edge.source) || failedNodeIds.has(edge.target);
    return {
      id: `e-${i}`,
      source: edge.source,
      target: edge.target,
      type: 'custom',
      data: { isFailurePath },
      animated: isFailurePath,
    };
  });

  dagre.layout(g);

  nodes.forEach((node) => {
    const pos = g.node(node.id);
    node.position = { x: pos.x - 100, y: pos.y - 70 };
  });

  return { nodes, edges };
}

interface GraphCanvasProps {
  graphData: GraphData;
}

export function GraphCanvas({ graphData }: GraphCanvasProps) {
  const { selectedNode, setSelectedNode, searchQuery, healthFilter } = useGraphStore();
  const selectedNodeId = selectedNode?.id ?? null;

  const { nodes: layoutedNodes, edges: layoutedEdges } = useMemo(
    () => getLayoutedElements(graphData, selectedNodeId, searchQuery, healthFilter),
    [graphData, selectedNodeId, searchQuery, healthFilter],
  );

  const [nodes, setNodes, onNodesChange] = useNodesState(layoutedNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(layoutedEdges);

  useEffect(() => {
    setNodes(layoutedNodes);
    setEdges(layoutedEdges);
  }, [layoutedNodes, layoutedEdges, setNodes, setEdges]);

  const onNodeClick = useCallback(
    (_: React.MouseEvent, node: Node) => {
      const graphNode = graphData.nodes.find((n) => n.id === node.id);
      if (graphNode) setSelectedNode(graphNode);
    },
    [graphData, setSelectedNode],
  );

  const onPaneClick = useCallback(() => setSelectedNode(null), [setSelectedNode]);

  return (
    <div className="w-full h-full rounded-xl overflow-hidden" style={{ background: 'var(--bg-primary)' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={onNodeClick}
        onPaneClick={onPaneClick}
        nodeTypes={nodeTypes}
        edgeTypes={edgeTypes}
        fitView
        fitViewOptions={{ padding: 0.2 }}
        minZoom={0.3}
        maxZoom={2}
        proOptions={{ hideAttribution: true }}
      >
        <Background variant={BackgroundVariant.Dots} gap={20} size={1} color="rgba(148,163,184,0.08)" />
        <Controls showInteractive={false} />
        <MiniMap
          nodeColor={(node) => {
            const d = node.data as Record<string, unknown>;
            const h = d.health as string;
            const colors: Record<string, string> = { healthy: '#10b981', warning: '#f59e0b', failed: '#ef4444', unstable: '#f97316' };
            return colors[h] || '#6b7280';
          }}
          maskColor="rgba(10, 14, 26, 0.8)"
          style={{ borderRadius: 8 }}
        />
      </ReactFlow>
    </div>
  );
}
