import type { Edge, Node } from "reactflow";

import type { BuilderNodeData } from "@/store/builder";
import type { ValidationIssue } from "@/strategyBuilder/types";

export function validateGraph(
  nodes: Node<BuilderNodeData>[],
  edges: Edge[],
): ValidationIssue[] {
  const issues: ValidationIssue[] = [];

  if (nodes.length === 0) {
    issues.push({ level: "error", message: "Strategy has no nodes" });
    return issues;
  }

  const indicators = nodes.filter((n) => n.data.kind === "indicator");
  if (indicators.length === 0) {
    issues.push({ level: "warning", message: "No indicators wired in" });
  }

  const aliases = new Set<string>();
  for (const n of indicators) {
    const alias = String(n.data.params?.alias ?? "");
    if (!alias) {
      issues.push({
        level: "error",
        message: "Indicator missing alias",
        node_id: n.id,
      });
    } else if (aliases.has(alias)) {
      issues.push({
        level: "error",
        message: `Duplicate indicator alias: ${alias}`,
        node_id: n.id,
      });
    } else {
      aliases.add(alias);
    }
  }

  const rules = nodes.filter((n) => n.data.kind === "rule");
  if (rules.length === 0) {
    issues.push({ level: "error", message: "Strategy has no rules" });
  }

  for (const rule of rules) {
    const incoming = edges.filter((e) => e.target === rule.id);
    if (incoming.length === 0) {
      issues.push({
        level: "error",
        message: "Rule has no operator wired",
        node_id: rule.id,
      });
    }
  }

  for (const edge of edges) {
    if (!nodes.find((n) => n.id === edge.source)) {
      issues.push({ level: "error", message: "Dangling source", edge_id: edge.id });
    }
    if (!nodes.find((n) => n.id === edge.target)) {
      issues.push({ level: "error", message: "Dangling target", edge_id: edge.id });
    }
  }

  return issues;
}
