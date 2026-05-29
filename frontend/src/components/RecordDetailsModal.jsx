import { useEffect, useState } from "react";
import { getAuditTrail } from "../api/reviewApi";
import { formatDate } from "../utils/format";
import AuditTimeline from "./AuditTimeline";
import LoadingState from "./LoadingState";
import StatusBadge from "./StatusBadge";

export default function RecordDetailsModal({ record, onClose }) {
  const [auditItems, setAuditItems] = useState([]);
  const [loadingAudit, setLoadingAudit] = useState(false);

  useEffect(() => {
    let mounted = true;
    const loadAudit = async () => {
      if (!record?.id) return;
      setLoadingAudit(true);
      try {
        const items = await getAuditTrail(record.id);
        if (mounted) setAuditItems(Array.isArray(items) ? items : []);
      } finally {
        if (mounted) setLoadingAudit(false);
      }
    };

    loadAudit();
    return () => {
      mounted = false;
    };
  }, [record?.id]);

  if (!record) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center bg-slate-950/70 p-3 sm:p-8" onClick={onClose}>
      <div className="glass-panel max-h-[92vh] w-full max-w-5xl overflow-y-auto p-5" onClick={(e) => e.stopPropagation()}>
        <div className="mb-4 flex items-start justify-between gap-3">
          <div>
            <h3 className="font-heading text-xl font-semibold">Record Details</h3>
            <p className="text-xs text-slate-400">Ingestion Job: {record.ingestion_job || "-"}</p>
          </div>
          <button className="rounded-lg border border-slate-600 px-3 py-1 text-xs hover:bg-slate-800" onClick={onClose}>
            Close
          </button>
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          <div className="space-y-2 rounded-xl border border-slate-700/70 bg-slate-900/70 p-4 text-sm">
            <p><span className="text-slate-400">Source:</span> {record.source_type}</p>
            <p><span className="text-slate-400">Period:</span> {record.period}</p>
            <p><span className="text-slate-400">Scope:</span> {record.scope}</p>
            <p><span className="text-slate-400">Status:</span> <StatusBadge value={record.status} /></p>
            {record.status === "approved" ? <StatusBadge value="locked" /> : null}
            <p><span className="text-slate-400">Normalized At:</span> {formatDate(record.normalized_at)}</p>
            <p><span className="text-slate-400">Version:</span> {record.normalization_version || "-"}</p>
            <p><span className="text-slate-400">Notes:</span> {record.normalization_notes || "-"}</p>
            <p><span className="text-slate-400">Reviewed At:</span> {formatDate(record.reviewed_at)}</p>
            <p><span className="text-slate-400">Rejection Reason:</span> {record.rejection_reason || "-"}</p>
          </div>

          <div className="rounded-xl border border-slate-700/70 bg-slate-900/70 p-4">
            <p className="mb-2 text-sm font-medium text-slate-200">Suspicious Flags</p>
            <ul className="space-y-1 text-sm text-slate-300">
              {(record.flag_reasons || []).length ? (
                record.flag_reasons.map((flag) => <li key={flag}>- {flag}</li>)
              ) : (
                <li>None</li>
              )}
            </ul>
          </div>
        </div>

        <div className="mt-4 grid gap-4 lg:grid-cols-2">
          <section className="rounded-xl border border-slate-700/70 bg-slate-900/70 p-4">
            <p className="mb-2 text-sm font-medium text-slate-200">Raw Payload</p>
            <pre className="max-h-72 overflow-auto rounded bg-slate-950/80 p-3 text-xs text-slate-200">{JSON.stringify(record.raw_payload || {}, null, 2)}</pre>
          </section>

          <section className="rounded-xl border border-slate-700/70 bg-slate-900/70 p-4">
            <p className="mb-2 text-sm font-medium text-slate-200">Normalized Payload</p>
            <pre className="max-h-72 overflow-auto rounded bg-slate-950/80 p-3 text-xs text-slate-200">{JSON.stringify(record.normalized_payload || {}, null, 2)}</pre>
          </section>
        </div>

        <section className="mt-4 rounded-xl border border-slate-700/70 bg-slate-900/70 p-4">
          <p className="mb-2 text-sm font-medium text-slate-200">Audit History Timeline</p>
          {loadingAudit ? <LoadingState message="Loading audit history..." /> : <AuditTimeline items={auditItems} />}
        </section>
      </div>
    </div>
  );
}
