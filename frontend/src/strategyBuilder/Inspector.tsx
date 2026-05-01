import { useEffect, useState } from "react";
import type { Node } from "reactflow";

import { Card } from "@/components/ui/Card";
import { useBuilderStore, type BuilderNodeData } from "@/store/builder";

type Props = {
  selected: Node<BuilderNodeData> | null;
};

const PARAM_FIELDS: Record<string, { label: string; key: string; type: "number" | "text" }[]> = {
  ema: [
    { label: "Alias",  key: "alias",  type: "text" },
    { label: "Period", key: "period", type: "number" },
  ],
  sma: [
    { label: "Alias",  key: "alias",  type: "text" },
    { label: "Period", key: "period", type: "number" },
  ],
  rsi: [
    { label: "Alias",  key: "alias",  type: "text" },
    { label: "Period", key: "period", type: "number" },
  ],
  macd: [
    { label: "Fast",   key: "fast",   type: "number" },
    { label: "Slow",   key: "slow",   type: "number" },
    { label: "Signal", key: "signal", type: "number" },
  ],
  bollinger: [
    { label: "Period", key: "period", type: "number" },
    { label: "K",      key: "k",      type: "number" },
  ],
  atr: [
    { label: "Period", key: "period", type: "number" },
  ],
};

export default function Inspector({ selected }: Props) {
  const upsertNode = useBuilderStore((s) => s.upsertNode);
  const [draft, setDraft] = useState<Record<string, unknown>>({});

  useEffect(() => {
    setDraft(selected?.data?.params ?? {});
  }, [selected?.id]);

  if (!selected) {
    return (
      <Card className="text-sm text-slate-400">
        Select a node to inspect its parameters.
      </Card>
    );
  }

  const kind = selected.data?.kind ?? "indicator";
  const indicatorName = String(selected.data?.params?.name ?? "");
  const fields = PARAM_FIELDS[indicatorName] ?? [];

  const apply = () => {
    upsertNode({
      ...selected,
      data: { ...selected.data, params: { ...selected.data.params, ...draft } },
    });
  };

  return (
    <Card className="space-y-3">
      <div className="text-xs uppercase tracking-wide text-slate-400">{kind}</div>
      <div className="text-base font-semibold">{selected.data?.label}</div>
      {fields.length === 0 ? (
        <div className="text-sm text-slate-400">No parameters for this node.</div>
      ) : (
        <div className="space-y-2">
          {fields.map((field) => (
            <label key={field.key} className="block text-xs">
              <div className="mb-1 text-slate-400">{field.label}</div>
              <input
                type={field.type === "number" ? "number" : "text"}
                value={String(draft[field.key] ?? "")}
                onChange={(e) =>
                  setDraft((prev) => ({
                    ...prev,
                    [field.key]: field.type === "number" ? Number(e.target.value) : e.target.value,
                  }))
                }
                className="w-full rounded border border-slate-600 bg-slate-900 px-2 py-1 text-sm text-slate-100 focus:border-emerald-400 focus:outline-none"
              />
            </label>
          ))}
          <button
            onClick={apply}
            className="rounded bg-emerald-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-emerald-500"
          >
            Apply
          </button>
        </div>
      )}
    </Card>
  );
}
