import { beforeEach, describe, expect, it } from "vitest";

import { useBuilderStore } from "@/store/builder";

describe("builder store", () => {
  beforeEach(() => {
    useBuilderStore.getState().setGraph([], []);
    useBuilderStore.setState({
      symbols: ["ETH/USDT"],
      timeframe: "1h",
      parameters: {},
    });
  });

  it("starts empty", () => {
    expect(useBuilderStore.getState().nodes).toEqual([]);
    expect(useBuilderStore.getState().edges).toEqual([]);
  });

  it("upserts nodes idempotently", () => {
    const node = {
      id: "ind-1",
      position: { x: 0, y: 0 },
      type: "alphaNode",
      data: { kind: "indicator" as const, label: "EMA", params: { period: 14 } },
    };
    useBuilderStore.getState().upsertNode(node);
    useBuilderStore.getState().upsertNode(node);
    expect(useBuilderStore.getState().nodes).toHaveLength(1);
  });

  it("removes nodes and incident edges", () => {
    const a = { id: "n1", position: { x: 0, y: 0 }, type: "alphaNode",
      data: { kind: "indicator" as const, label: "fast", params: {} } };
    const b = { id: "n2", position: { x: 0, y: 0 }, type: "alphaNode",
      data: { kind: "indicator" as const, label: "slow", params: {} } };
    useBuilderStore.getState().upsertNode(a);
    useBuilderStore.getState().upsertNode(b);
    useBuilderStore.getState().upsertEdge({ id: "e1", source: "n1", target: "n2" });
    useBuilderStore.getState().removeNode("n1");
    expect(useBuilderStore.getState().nodes).toHaveLength(1);
    expect(useBuilderStore.getState().edges).toHaveLength(0);
  });

  it("stores parameters", () => {
    useBuilderStore.setState({ parameters: { period: 14 } });
    expect(useBuilderStore.getState().parameters.period).toBe(14);
  });
});
