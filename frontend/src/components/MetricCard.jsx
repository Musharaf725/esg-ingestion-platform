export default function MetricCard({ label, value, accent = "ops" }) {
  const accentMap = {
    ops: "from-ops-600/20 to-ops-300/5 border-ops-400/30",
    amber: "from-amber-500/20 to-amber-300/5 border-amber-400/30",
    green: "from-emerald-500/20 to-emerald-300/5 border-emerald-400/30",
    rose: "from-rose-500/20 to-rose-300/5 border-rose-400/30",
  };

  return (
    <article className={`glass-panel bg-gradient-to-br p-4 ${accentMap[accent] || accentMap.ops}`}>
      <p className="text-xs uppercase tracking-wide text-slate-300">{label}</p>
      <p className="mt-2 font-heading text-3xl font-semibold text-white">{value}</p>
    </article>
  );
}
