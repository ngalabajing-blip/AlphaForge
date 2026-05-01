import { create } from "zustand";
import { immer } from "zustand/middleware/immer";
import { Edge, Node } from "reactflow";

export type BuilderNodeKind =
  | "indicator"
  | "operator"
  | "rule"
  | "trigger"
  | "execution"
  | "constant";

export type BuilderNodeData = {
  kind: BuilderNodeKind;
  label: string;
  // generic params (e.g. period, source, comparator)
  params: Record<string, unknown>;
};

export type BuilderState = {
  nodes: Node<BuilderNodeData>[];
  edges: Edge[];
  symbols: string[];
  timeframe: string;
  parameters: Record<string, unknown>;
  setSymbols: (s: string[]) => void;
  setTimeframe: (tf: string) => void;
  setParameters: (p: Record<string, unknown>) => void;
  setGraph: (nodes: Node<BuilderNodeData>[], edges: Edge[]) => void;
  upsertNode: (node: Node<BuilderNodeData>) => void;
  removeNode: (id: string) => void;
  upsertEdge: (edge: Edge) => void;
  removeEdge: (id: string) => void;
  reset: () => void;
};

export const useBuilderStore = create<BuilderState>()(
  immer((set) => ({
    nodes: [],
    edges: [],
    symbols: ["ETH/USDT"],
    timeframe: "1h",
    parameters: {},
    setSymbols: (s) => set((state) => { state.symbols = s; }),
    setTimeframe: (tf) => set((state) => { state.timeframe = tf; }),
    setParameters: (p) => set((state) => { state.parameters = p; }),
    setGraph: (nodes, edges) => set((state) => { state.nodes = nodes; state.edges = edges; }),
    upsertNode: (node) =>
      set((state) => {
        const idx = state.nodes.findIndex((n) => n.id === node.id);
        if (idx >= 0) state.nodes[idx] = node;
        else state.nodes.push(node);
      }),
    removeNode: (id) =>
      set((state) => {
        state.nodes = state.nodes.filter((n) => n.id !== id);
        state.edges = state.edges.filter((e) => e.source !== id && e.target !== id);
      }),
    upsertEdge: (edge) =>
      set((state) => {
        const idx = state.edges.findIndex((e) => e.id === edge.id);
        if (idx >= 0) state.edges[idx] = edge;
        else state.edges.push(edge);
      }),
    removeEdge: (id) =>
      set((state) => { state.edges = state.edges.filter((e) => e.id !== id); }),
    reset: () =>
      set((state) => {
        state.nodes = [];
        state.edges = [];
        state.symbols = ["ETH/USDT"];
        state.timeframe = "1h";
        state.parameters = {};
      }),
  })),
);
