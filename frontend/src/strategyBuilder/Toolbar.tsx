import { useBuilderStore } from "@/store/builder";

type Props = {
  onSave: () => void | Promise<void>;
  onValidate: () => void;
  saving?: boolean;
};

export default function Toolbar({ onSave, onValidate, saving }: Props) {
  const symbols = useBuilderStore((s) => s.symbols);
  const timeframe = useBuilderStore((s) => s.timeframe);
  const setSymbols = (v: string) =>
    useBuilderStore.setState({ symbols: v.split(",").map((x) => x.trim()).filter(Boolean) });
  const setTimeframe = (v: string) => useBuilderStore.setState({ timeframe: v });

  return (
    <div className="flex flex-wrap items-center gap-2 rounded border border-slate-700 bg-slate-900 p-2">
      <label className="text-xs text-slate-400">
        Symbols
        <input
          value={symbols.join(", ")}
          onChange={(e) => setSymbols(e.target.value)}
          className="ml-2 rounded border border-slate-700 bg-slate-800 px-2 py-1 text-sm text-slate-100"
        />
      </label>
      <label className="text-xs text-slate-400">
        Timeframe
        <select
          value={timeframe}
          onChange={(e) => setTimeframe(e.target.value)}
          className="ml-2 rounded border border-slate-700 bg-slate-800 px-2 py-1 text-sm text-slate-100"
        >
          {["1m", "5m", "15m", "30m", "1h", "4h", "1d"].map((tf) => (
            <option key={tf} value={tf}>{tf}</option>
          ))}
        </select>
      </label>
      <div className="ml-auto flex gap-2">
        <button
          onClick={onValidate}
          className="rounded border border-slate-600 px-3 py-1.5 text-xs hover:bg-slate-800"
        >
          Validate
        </button>
        <button
          onClick={() => onSave()}
          disabled={saving}
          className="rounded bg-emerald-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-emerald-500 disabled:opacity-60"
        >
          {saving ? "Saving…" : "Save strategy"}
        </button>
      </div>
    </div>
  );
}
