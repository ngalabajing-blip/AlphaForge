import { describe, expect, it } from "vitest";

import {
  formatNumber,
  formatPercent,
  truncateAddr,
  severityClass,
} from "@/lib/format";

describe("formatNumber", () => {
  it("returns plain numbers under 1k unchanged", () => {
    expect(formatNumber(123)).toMatch(/123/);
  });

  it("uses K suffix for thousands", () => {
    expect(formatNumber(12_345)).toMatch(/K/);
  });

  it("uses M for millions", () => {
    expect(formatNumber(7_500_000)).toMatch(/M/);
  });

  it("handles zero", () => {
    expect(formatNumber(0)).toMatch(/0/);
  });
});

describe("formatPercent", () => {
  it("multiplies by 100 and adds %", () => {
    expect(formatPercent(0.123, 1)).toBe("12.3%");
  });

  it("rounds at the requested precision", () => {
    expect(formatPercent(0.987654, 2)).toBe("98.77%");
  });

  it("works for negative", () => {
    expect(formatPercent(-0.05, 2)).toBe("-5.00%");
  });
});

describe("truncateAddr", () => {
  it("preserves head and tail", () => {
    const addr = "0xabcdef1234567890abcdef1234567890abcdef12";
    const out = truncateAddr(addr, 6, 4);
    expect(out.startsWith("0xabcd")).toBe(true);
    expect(out.endsWith("ef12")).toBe(true);
    expect(out).toContain("…");
  });

  it("returns full string when shorter than head+tail", () => {
    expect(truncateAddr("0x12", 6, 4)).toBe("0x12");
  });
});

describe("severityClass", () => {
  it("returns rose for critical", () => {
    expect(severityClass("critical")).toContain("rose");
  });

  it("returns orange for high", () => {
    expect(severityClass("high")).toContain("orange");
  });

  it("returns slate for unknown", () => {
    expect(severityClass("___unknown___")).toContain("slate");
  });
});
