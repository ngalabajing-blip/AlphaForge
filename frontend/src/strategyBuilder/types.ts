import type { Edge, Node } from "reactflow";

import type { BuilderNodeData } from "@/store/builder";

export type CompileInput = {
  name: string;
  symbols: string[];
  timeframe: string;
  parameters: Record<string, unknown>;
  nodes: Node<BuilderNodeData>[];
  edges: Edge[];
};

export type Compiled = {
  yaml: string;
  parameters: Record<string, unknown>;
  warnings: string[];
};

export type ValidationIssue = {
  level: "error" | "warning";
  message: string;
  node_id?: string;
  edge_id?: string;
};
