import { formatDate } from "../utils/format";

export default function AuditTimeline({ items }) {
  if (!items?.length) {
    return <p className="text-sm text-slate-400">No audit events available.</p>;
  }

  return (
    <ul className="space-y-3">
      {items.map((item, idx) => (
        <li key={`${item.id || item.timestamp || idx}`} className="rounded-lg border border-slate-700/70 bg-slate-900/70 p-3">
          <div className="flex flex-wrap items-center justify-between gap-2 text-xs">
            <span className="rounded-full bg-slate-700 px-2 py-0.5 uppercase tracking-wide text-slate-100">{item.action}</span>
            <span className="text-slate-400">{formatDate(item.timestamp)}</span>
          </div>
          <p className="mt-1 text-sm text-slate-200">By: {item.performed_by?.username || item.performed_by || "System"}</p>
          <div className="mt-2 grid gap-2 text-xs text-slate-300 sm:grid-cols-2">
            <pre className="overflow-auto rounded bg-slate-950/80 p-2">Old: {JSON.stringify(item.old_value || {}, null, 2)}</pre>
            <pre className="overflow-auto rounded bg-slate-950/80 p-2">New: {JSON.stringify(item.new_value || {}, null, 2)}</pre>
          </div>
          {item.note ? <p className="mt-2 text-xs text-slate-300">Note: {item.note}</p> : null}
        </li>
      ))}
    </ul>
  );
}
