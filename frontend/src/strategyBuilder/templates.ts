import type { Edge, Node } from "reactflow";

import type { BuilderNodeData } from "@/store/builder";

export type StrategyTemplate = {
  id: string;
  name: string;
  description: string;
  symbols: string[];
  timeframe: string;
  parameters: Record<string, unknown>;
  nodes: Node<BuilderNodeData>[];
  edges: Edge[];
};

const indicator = (
  id: string,
  x: number,
  y: number,
  label: string,
  params: Record<string, unknown>,
): Node<BuilderNodeData> => ({
  id,
  type: "alphaNode",
  position: { x, y },
  data: { kind: "indicator", label, params },
});

const operator = (
  id: string,
  x: number,
  y: number,
  label: string,
  params: Record<string, unknown>,
): Node<BuilderNodeData> => ({
  id,
  type: "alphaNode",
  position: { x, y },
  data: { kind: "operator", label, params },
});

const rule = (
  id: string,
  x: number,
  y: number,
  label: string,
  params: Record<string, unknown>,
): Node<BuilderNodeData> => ({
  id,
  type: "alphaNode",
  position: { x, y },
  data: { kind: "rule", label, params },
});

export const TEMPLATES: StrategyTemplate[] = [
  {
    id: "ema-cross",
    name: "EMA cross",
    description: "Classic EMA(12)/EMA(26) crossover with size 0.2.",
    symbols: ["ETH/USDT"],
    timeframe: "1h",
    parameters: { fast_period: 12, slow_period: 26 },
    nodes: [
      indicator("ind-fast", 40, 80,  "EMA fast", { name: "ema", alias: "fast", period: 12 }),
      indicator("ind-slow", 40, 200, "EMA slow", { name: "ema", alias: "slow", period: 26 }),
      operator("op-cross",  280, 140, "cross_up", { fn: "cross_up" }),
      rule("rule-buy",      540, 100, "Buy",     { action: "buy",   size: 0.2 }),
      rule("rule-close",    540, 200, "Close",   { action: "close" }),
      operator("op-cross-d",280, 260, "cross_down", { fn: "cross_down" }),
    ],
    edges: [
      { id: "e1", source: "ind-fast",   target: "op-cross",   animated: true },
      { id: "e2", source: "ind-slow",   target: "op-cross",   animated: true },
      { id: "e3", source: "op-cross",   target: "rule-buy",   animated: true },
      { id: "e4", source: "ind-fast",   target: "op-cross-d", animated: true },
      { id: "e5", source: "ind-slow",   target: "op-cross-d", animated: true },
      { id: "e6", source: "op-cross-d", target: "rule-close", animated: true },
    ],
  },
  {
    id: "rsi-mean-reversion",
    name: "RSI mean reversion",
    description: "Buy oversold RSI(14) < 30, close on RSI(14) > 60.",
    symbols: ["BTC/USDT"],
    timeframe: "15m",
    parameters: { rsi_period: 14, oversold: 30, exit: 60 },
    nodes: [
      indicator("rsi", 40, 140, "RSI(14)", { name: "rsi", alias: "rsi14", period: 14 }),
      operator("lt", 280, 80, "<", { fn: "<" }),
      operator("gt", 280, 200, ">", { fn: ">" }),
      rule("buy", 540, 80, "Buy", { action: "buy", size: 0.15 }),
      rule("close", 540, 200, "Close", { action: "close" }),
    ],
    edges: [
      { id: "e1", source: "rsi", target: "lt", animated: true },
      { id: "e2", source: "rsi", target: "gt", animated: true },
      { id: "e3", source: "lt",  target: "buy", animated: true },
      { id: "e4", source: "gt",  target: "close", animated: true },
    ],
  },
];
