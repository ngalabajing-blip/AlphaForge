import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";

import { Badge } from "@/components/ui/Badge";

describe("<Badge />", () => {
  it("renders the label", () => {
    render(<Badge>completed</Badge>);
    expect(screen.getByText("completed")).toBeDefined();
  });

  it("applies a variant class", () => {
    render(<Badge variant="success">ok</Badge>);
    const el = screen.getByText("ok");
    expect(el.className).toMatch(/emerald|green/);
  });

  it("renders critical severity badge", () => {
    render(<Badge variant="critical">danger</Badge>);
    const el = screen.getByText("danger");
    expect(el.className).toMatch(/rose|red/);
  });
});
