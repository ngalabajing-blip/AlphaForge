import { Handle, NodeProps, Position } from "reactflow";

import type { BuilderNodeData } from "@/store/builder";

const KIND_PALETTE: Record<BuilderNodeData["kind"], string> = {
  indicator: "border-sky-400 bg-sky-500/10",
  operator:  "border-fuchsia-400 bg-fuchsia-500/10",
  rule:      "border-emerald-400 bg-emerald-500/10",
  trigger:   "border-amber-400 bg-amber-500/10",
  execution: "border-rose-400 bg-rose-500/10",
  constant:  "border-slate-400 bg-slate-500/10",
};

export default function NodeView({ data, selected }: NodeProps<BuilderNodeData>) {
  const palette = KIND_PALETTE[data.kind] ?? "border-slate-500 bg-slate-700/30";
  return (
    <div
      className={`min-w-[140px] rounded border-2 px-3 py-2 text-xs text-slate-100 backdrop-blur-sm ${palette} ${
        selected ? "ring-2 ring-emerald-300" : ""
      }`}
    >
      <div className="text-[10px] uppercase tracking-wide text-slate-300">{data.kind}</div>
      <div className="text-sm font-semibold">{data.label}</div>
      {data.kind === "indicator" && data.params?.period !== undefined ? (
        <div className="mt-1 text-[11px] text-slate-300">
          period={String(data.params.period)}
        </div>
      ) : null}
      {data.kind !== "trigger" ? <Handle type="target" position={Position.Left} /> : null}
      {data.kind !== "rule" ? <Handle type="source" position={Position.Right} /> : null}
    </div>
  );
}
