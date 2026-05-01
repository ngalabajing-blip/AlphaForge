import { useEffect, useState } from "react";
import ReactFlow, {
  Background, Controls, MiniMap,
  addEdge, applyEdgeChanges, applyNodeChanges,
  type Connection, type Edge, type Node, type EdgeChange, type NodeChange,
} from "reactflow";
import "reactflow/dist/style.css";

import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { useBuilderStore } from "@/store/builder";
import { compileGraphToDSL } from "@/strategyBuilder/compile";
import { Palette } from "@/strategyBuilder/Palette";
import { Inspector } from "@/strategyBuilder/Inspector";
import { nodeTypes } from "@/strategyBuilder/nodes";
import api from "@/lib/api";

let _idCounter = 1;
const newId = (kind: string) => `${kind}-${_idCounter++}`;

export default function StrategyBuilderPage() {
  const {
    nodes, edges, setGraph, upsertNode, upsertEdge, removeEdge,
    symbols, timeframe, setTimeframe, parameters, reset,
  } = useBuilderStore();
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [name, setName] = useState("My Strategy");
  const [saved, setSaved] = useState(false);

  useEffect(() => () => reset(), [reset]);

  const onNodesChange = (changes: NodeChange[]) => setGraph(applyNodeChanges(changes, nodes), edges);
  const onEdgesChange = (changes: EdgeChange[]) => setGraph(nodes, applyEdgeChanges(changes, edges));
  const onConnect = (conn: Connection) => {
    const id = `e-${conn.source}-${conn.target}-${Date.now()}`;
    setGraph(nodes, addEdge({ ...conn, id, animated: true, style: { stroke: "#22d3ee" } } as Edge, edges));
  };

  const handleAddFromPalette = (kind: string, label: string, params: Record<string, unknown>) => {
    const id = newId(kind);
    upsertNode({
      id,
      position: { x: 80 + Math.random() * 480, y: 80 + Math.random() * 320 },
      data: { kind: kind as any, label, params },
      type: "alphaNode",
    } as Node);
  };

  const handleSave = async () => {
    const compiled = compileGraphToDSL({
      name, symbols, timeframe, parameters, nodes, edges,
    });
    try {
      await api.post("/strategies", {
        name,
        is_public: false,
        tags: [],
        raw_source: compiled.yaml,
        parameters: compiled.parameters,
      });
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (err) {
      console.error("save failed", err);
    }
  };

  const selectedNode = nodes.find((n) => n.id === selectedId) || null;

  return (
    <div className="grid grid-cols-1 xl:grid-cols-[260px_1fr_320px] gap-4 h-[calc(100vh-7rem)]">
      <Card title="Palette" subtitle="Drag or click to add">
        <Palette onAdd={handleAddFromPalette} />
      </Card>

      <div className="bg-slate-950/50 border border-white/10 rounded-xl overflow-hidden">
        <div className="px-4 py-2 flex items-center justify-between border-b border-white/10">
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="bg-transparent text-base font-semibold focus:outline-none"
          />
          <div className="flex items-center gap-2">
            <Badge tone="info">{timeframe}</Badge>
            <Badge tone="primary">{symbols.length} symbol(s)</Badge>
            <button className="btn-primary" onClick={handleSave}>Save</button>
            {saved && <Badge tone="bullish">saved</Badge>}
          </div>
        </div>
        <div className="h-[calc(100%-3rem)]">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onNodeClick={(_, n) => setSelectedId(n.id)}
            onPaneClick={() => setSelectedId(null)}
            onEdgeClick={(_, e) => removeEdge(e.id)}
            nodeTypes={nodeTypes}
            fitView
          >
            <Background gap={24} color="#1e293b" />
            <Controls className="bg-slate-900 border border-white/10" />
            <MiniMap
              maskColor="#0f172a99"
              nodeColor={() => "#6366f1"}
              style={{ background: "#0b1220", border: "1px solid #1e293b" }}
            />
          </ReactFlow>
        </div>
      </div>

      <Card title="Inspector" subtitle={selectedNode ? selectedNode.data.label : "Select a node"}>
        <Inspector
          selectedNode={selectedNode}
          onChange={(node) => upsertNode(node)}
          timeframe={timeframe}
          setTimeframe={setTimeframe}
          symbols={symbols}
        />
      </Card>
    </div>
  );
}
