import { Handle, Position, type NodeProps } from "reactflow";
import clsx from "clsx";

import type { BuilderNodeData } from "@/store/builder";

const styles: Record<string, string> = {
  indicator: "border-cyan-700/40 bg-cyan-900/20",
  operator: "border-violet-700/40 bg-violet-900/20",
  rule: "border-emerald-700/40 bg-emerald-900/20",
  trigger: "border-amber-700/40 bg-amber-900/20",
  execution: "border-rose-700/40 bg-rose-900/20",
  constant: "border-slate-700/40 bg-slate-900/20",
};

// eslint-disable-next-line react-refresh/only-export-components
const AlphaNode = ({ data, selected }: NodeProps<BuilderNodeData>) => (
  <div
    className={clsx(
      "rounded-lg border px-3 py-2 min-w-[140px] text-sm shadow",
      styles[data.kind] || styles.indicator,
      selected && "ring-2 ring-primary-500",
    )}
  >
    <Handle type="target" position={Position.Top} className="!bg-slate-300" />
    <div className="text-[10px] uppercase text-slate-400">{data.kind}</div>
    <div className="font-semibold">{data.label}</div>
    <div className="text-[11px] text-slate-300/80 max-w-[200px] truncate">
      {Object.entries(data.params).slice(0, 3).map(([k, v]) => `${k}=${String(v)}`).join("  ")}
    </div>
    <Handle type="source" position={Position.Bottom} className="!bg-slate-300" />
  </div>
);

export const nodeTypes = { alphaNode: AlphaNode };
