import { describe, expect, it } from "vitest";

import { compileGraphToDSL } from "@/strategyBuilder/compile";

describe("compileGraphToDSL", () => {
  it("produces valid YAML for a tiny graph", () => {
    const result = compileGraphToDSL({
      name: "EMA Cross",
      symbols: ["ETH/USDT"],
      timeframe: "1h",
      parameters: { threshold: 0.5 },
      nodes: [
        { id: "ind-1", position: { x: 0, y: 0 }, type: "alphaNode",
          data: { kind: "indicator", label: "EMA fast", params: { name: "ema", alias: "fast", period: 12 } } },
        { id: "ind-2", position: { x: 0, y: 0 }, type: "alphaNode",
          data: { kind: "indicator", label: "EMA slow", params: { name: "ema", alias: "slow", period: 26 } } },
        { id: "op-1", position: { x: 0, y: 0 }, type: "alphaNode",
          data: { kind: "operator", label: "cross_up", params: { fn: "cross_up" } } },
        { id: "rule-1", position: { x: 0, y: 0 }, type: "alphaNode",
          data: { kind: "rule", label: "Buy", params: { action: "buy", size: 0.2 } } },
      ] as any,
      edges: [
        { id: "e1", source: "ind-1", target: "op-1" },
        { id: "e2", source: "ind-2", target: "op-1" },
        { id: "e3", source: "op-1", target: "rule-1" },
      ],
    });
    expect(result.yaml).toContain("strategy: \"EMA Cross\"");
    expect(result.yaml).toContain("ema");
    expect(result.yaml).toContain("cross_up(fast, slow)");
    expect(result.yaml).toContain("then: buy");
    expect(result.yaml).toContain("threshold: 0.5");
  });

  it("warns about disconnected rule", () => {
    const result = compileGraphToDSL({
      name: "Empty",
      symbols: [],
      timeframe: "1h",
      parameters: {},
      nodes: [
        { id: "rule-1", position: { x: 0, y: 0 }, type: "alphaNode",
          data: { kind: "rule", label: "Buy", params: { action: "buy" } } },
      ] as any,
      edges: [],
    });
    expect(result.warnings).toContain("rule rule-1 has no operator wired");
  });
});
