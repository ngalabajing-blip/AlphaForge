import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";

import { Badge } from "@/components/ui/Badge";

describe("<Badge />", () => {
  it("renders the label", () => {
    render(<Badge>completed</Badge>);
    expect(screen.getByText("completed")).toBeDefined();
  });

  it("applies a bullish tone class", () => {
    render(<Badge tone="bullish">ok</Badge>);
    const el = screen.getByText("ok");
    expect(el.className).toMatch(/emerald|green/);
  });

  it("renders a bearish tone badge", () => {
    render(<Badge tone="bearish">danger</Badge>);
    const el = screen.getByText("danger");
    expect(el.className).toMatch(/rose|red/);
  });
});
