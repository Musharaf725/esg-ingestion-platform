import { useEffect, useState } from "react";
import { getDashboardData } from "../api/dashboardApi";
import ErrorState from "../components/ErrorState";
import LoadingState from "../components/LoadingState";
import MetricCard from "../components/MetricCard";
import StatusBadge from "../components/StatusBadge";
import { formatDate } from "../utils/format";

export default function DashboardPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = async () => {
    setLoading(true);
    setError("");
    try {
      const payload = await getDashboardData();
      setData(payload);
    } catch (err) {
      setError(err?.response?.data?.error || "Unable to load dashboard data.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  if (loading) return <LoadingState message="Loading dashboard metrics..." />;
  if (error) return <ErrorState message={error} onRetry={load} />;

  return (
    <div className="space-y-5">
      <section className="metric-grid">
        <MetricCard label="Total Records" value={data.totals.total} />
        <MetricCard label="Pending Review" value={data.totals.pendingReview} accent="amber" />
        <MetricCard label="Approved" value={data.totals.approved} accent="green" />
        <MetricCard label="Rejected" value={data.totals.rejected} accent="rose" />
        <MetricCard label="Suspicious" value={data.totals.suspicious} accent="amber" />
        <MetricCard label="Failed Ingestion Rows" value={data.totals.failedRows} accent="rose" />
      </section>

      <section className="grid gap-5 xl:grid-cols-[1.4fr_1fr]">
        <article className="glass-panel p-4">
          <div className="mb-3 flex items-center justify-between">
            <h2 className="font-heading text-lg font-semibold">Ingestion Activity</h2>
            <p className="text-xs text-slate-400">Failed rows: {data.totals.failedRows}</p>
          </div>

          <div className="space-y-3">
            {(data.recentJobs || []).length ? (
              data.recentJobs.map((job, idx) => (
                <div key={`${job.fileName || "job"}-${idx}`} className="rounded-lg border border-slate-700/70 bg-slate-900/70 p-3">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <p className="text-sm font-medium">{job.fileName || "Uploaded file"}</p>
                    <StatusBadge value={job.failed > 0 ? "pending_review" : "approved"} />
                  </div>
                  <p className="mt-1 text-xs text-slate-400">{formatDate(job.createdAt)}</p>
                  <p className="mt-1 text-xs text-slate-300">Total: {job.total || 0} | Saved: {job.saved || 0} | Failed: {job.failed || 0}</p>
                </div>
              ))
            ) : (
              <p className="rounded-lg border border-slate-700/70 bg-slate-900/70 p-3 text-sm text-slate-400">No ingestion jobs yet. Upload a source file to start.</p>
            )}
          </div>
        </article>

        <article className="glass-panel p-4">
          <h2 className="font-heading text-lg font-semibold">Source Type Breakdown</h2>
          <div className="mt-3 space-y-3">
            {data.sourceBreakdown.map((item) => {
              const max = Math.max(...data.sourceBreakdown.map((s) => s.count), 1);
              const width = `${Math.max(8, Math.round((item.count / max) * 100))}%`;
              return (
                <div key={item.source}>
                  <div className="mb-1 flex items-center justify-between text-xs text-slate-300">
                    <span className="uppercase tracking-wide">{item.source}</span>
                    <span>{item.count}</span>
                  </div>
                  <div className="h-2 rounded-full bg-slate-800">
                    <div className="h-2 rounded-full bg-gradient-to-r from-ops-500 to-cyan-300" style={{ width }} />
                  </div>
                </div>
              );
            })}
          </div>
        </article>
      </section>

      <section className="glass-panel p-4">
        <h2 className="font-heading text-lg font-semibold">Suspicious Records Overview</h2>
        <div className="mt-3 space-y-2">
          {(data.suspiciousRecords || []).length ? (
            data.suspiciousRecords.map((record) => (
              <div key={record.id} className="rounded-lg border border-amber-300/30 bg-amber-400/10 p-3">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <p className="text-sm">
                    {record.source_type.toUpperCase()} | Period {record.period} | Scope {record.scope}
                  </p>
                  <StatusBadge value="suspicious" />
                </div>
                <p className="mt-1 text-xs text-amber-100">Flags: {(record.flag_reasons || []).join(", ") || "-"}</p>
              </div>
            ))
          ) : (
            <p className="text-sm text-slate-400">No suspicious records currently flagged.</p>
          )}
        </div>
      </section>
    </div>
  );
}
