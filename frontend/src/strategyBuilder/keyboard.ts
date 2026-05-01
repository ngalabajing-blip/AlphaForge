import { useEffect } from "react";
import { useBuilderStore } from "@/store/builder";

export function useBuilderKeyboard() {
  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "Delete" || event.key === "Backspace") {
        const active = document.activeElement?.tagName;
        if (active === "INPUT" || active === "TEXTAREA") return;
        const selected = useBuilderStore.getState().nodes.filter((n) => n.selected);
        const selectedEdges = useBuilderStore.getState().edges.filter((e) => e.selected);
        for (const node of selected) {
          useBuilderStore.getState().removeNode(node.id);
        }
        for (const edge of selectedEdges) {
          useBuilderStore.getState().removeEdge(edge.id);
        }
      }
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "s") {
        event.preventDefault();
        const e = new CustomEvent("alphaforge:builder:save");
        window.dispatchEvent(e);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);
}
