import type { Edge, Node } from "reactflow";

import type { BuilderNodeData } from "@/store/builder";

type CompileInput = {
  name: string;
  symbols: string[];
  timeframe: string;
  parameters: Record<string, unknown>;
  nodes: Node<BuilderNodeData>[];
  edges: Edge[];
};

type Compiled = {
  yaml: string;
  parameters: Record<string, unknown>;
  warnings: string[];
};

/**
 * Compile a graph of indicator/operator/rule nodes into the AlphaForge
 * Strategy DSL (YAML). The serialiser is intentionally simple — strict
 * graph shape:
 *
 *   indicators ─▶ operator ─▶ rule
 *                 │
 *                 └─▶ constant (RHS)
 */
export function compileGraphToDSL(input: CompileInput): Compiled {
  const { name, symbols, timeframe, parameters, nodes, edges } = input;
  const warnings: string[] = [];

  const indicators = nodes.filter((n) => n.data.kind === "indicator");
  const ruleNodes = nodes.filter((n) => n.data.kind === "rule");

  const indicatorYAMLs = indicators.map((n) => {
    const p = n.data.params as Record<string, unknown>;
    const inline = Object.entries(p)
      .filter(([k]) => !["name", "alias"].includes(k))
      .map(([k, v]) => `${k}: ${formatScalar(v)}`)
      .join(", ");
    const alias = (p.alias as string) || `ind_${n.id}`;
    return `  - {name: ${p.name}, alias: ${alias}${inline ? `, ${inline}` : ""}}`;
  });

  const adjacency = new Map<string, string[]>();
  edges.forEach((e) => {
    if (!adjacency.has(e.target)) adjacency.set(e.target, []);
    adjacency.get(e.target)!.push(e.source);
  });

  const ruleYAMLs = ruleNodes.map((rule) => {
    const inputs = adjacency.get(rule.id) || [];
    const operatorNode = nodes.find((n) => n.data.kind === "operator" && inputs.includes(n.id));
    if (!operatorNode) {
      warnings.push(`rule ${rule.id} has no operator wired`);
      return `  - when: false\n    then: ${rule.data.params.action}`;
    }
    const opInputs = adjacency.get(operatorNode.id) || [];
    const opChildren = opInputs
      .map((id) => nodes.find((n) => n.id === id))
      .filter(Boolean) as Node<BuilderNodeData>[];

    const fn = String(operatorNode.data.params.fn || ">");
    const args = opChildren.map((c) => emitNode(c));
    const expression = formatOperator(fn, args);

    const rp = rule.data.params as Record<string, unknown>;
    const sizeLine = rp.size != null ? `\n    size: ${formatScalar(rp.size)}` : "";
    return `  - when: ${expression}\n    then: ${rp.action}${sizeLine}`;
  });

  const yaml =
`strategy: ${jsonString(name)}
description: "Visually compiled strategy"
universe:
  symbols: [${symbols.map((s) => jsonString(s)).join(", ")}]
  timeframe: ${jsonString(timeframe)}
indicators:
${indicatorYAMLs.join("\n")}
rules:
${ruleYAMLs.join("\n")}
parameters: ${Object.keys(parameters).length ? "\n" + Object.entries(parameters).map(([k, v]) => `  ${k}: ${formatScalar(v)}`).join("\n") : "{}"}
`;

  return { yaml, parameters, warnings };
}

const emitNode = (n: Node<BuilderNodeData>): string => {
  if (n.data.kind === "indicator") {
    return String(n.data.params.alias || "ind");
  }
  if (n.data.kind === "constant") {
    const v = n.data.params.value;
    return formatScalar(v);
  }
  return "0";
};

const formatOperator = (fn: string, args: string[]): string => {
  if (fn === "and" || fn === "or") {
    return args.length ? args.join(` ${fn} `) : "false";
  }
  if ([">", "<", ">=", "<=", "==", "!="].includes(fn)) {
    return `${args[0] || 0} ${fn} ${args[1] || 0}`;
  }
  return `${fn}(${args.join(", ")})`;
};

const formatScalar = (v: unknown): string => {
  if (typeof v === "number") return Number.isFinite(v) ? String(v) : "0";
  if (typeof v === "boolean") return v ? "true" : "false";
  if (v == null) return "null";
  return jsonString(String(v));
};

const jsonString = (s: string): string => `"${s.replace(/"/g, '\\"')}"`;
