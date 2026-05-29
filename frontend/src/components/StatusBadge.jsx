const statusStyles = {
  pending: "bg-slate-700/70 text-slate-100 border-slate-500",
  pending_review: "bg-amber-500/20 text-amber-100 border-amber-400/50",
  approved: "bg-emerald-500/20 text-emerald-100 border-emerald-400/50",
  rejected: "bg-rose-500/20 text-rose-100 border-rose-400/50",
  failed: "bg-rose-500/20 text-rose-100 border-rose-400/50",
  processing: "bg-sky-500/20 text-sky-100 border-sky-400/50",
};

const labels = {
  pending: "Pending",
  pending_review: "Pending Review",
  approved: "Approved",
  rejected: "Rejected",
  failed: "Failed",
  processing: "Processing",
  suspicious: "Suspicious",
  locked: "Locked",
};

export default function StatusBadge({ value }) {
  const style = statusStyles[value] || "bg-slate-700/70 text-slate-100 border-slate-500";

  return (
    <span className={`inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-medium ${style}`}>
      {labels[value] || value}
    </span>
  );
}
