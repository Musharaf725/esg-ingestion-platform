import { useState } from "react";
import { pushRecentIngestionJob, uploadIngestionFile } from "../api/ingestionApi";
import ErrorState from "../components/ErrorState";
import LoadingState from "../components/LoadingState";

const sourceTypes = [
  { value: "sap", label: "SAP" },
  { value: "utility", label: "Utility" },
  { value: "travel", label: "Travel" },
];

export default function UploadPage() {
  const [file, setFile] = useState(null);
  const [sourceType, setSourceType] = useState("sap");
  const [progress, setProgress] = useState(0);
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  const onSubmit = async (event) => {
    event.preventDefault();
    if (!file) return;

    setSubmitting(true);
    setProgress(0);
    setResult(null);
    setError("");

    try {
      const data = await uploadIngestionFile({
        file,
        sourceType,
        onUploadProgress: (evt) => {
          if (!evt.total) return;
          setProgress(Math.round((evt.loaded / evt.total) * 100));
        },
      });

      setResult(data);
      pushRecentIngestionJob({
        fileName: file.name,
        sourceType,
        total: data.total || 0,
        saved: data.saved || 0,
        failed: data.failed || 0,
        createdAt: new Date().toISOString(),
        errors: data.error_log?.errors || [],
        warnings: data.normalization_warnings || [],
      });
    } catch (err) {
      setError(err?.response?.data?.error || "Upload failed.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-5">
      <section className="glass-panel p-5">
        <h2 className="font-heading text-lg font-semibold">Upload ESG Source File</h2>
        <p className="mt-1 text-sm text-slate-300">Accepted formats: CSV or JSON. Uploads are processed synchronously for analyst review.</p>

        <form className="mt-4 grid gap-4 md:grid-cols-3" onSubmit={onSubmit}>
          <label className="md:col-span-2">
            <span className="mb-1 block text-xs uppercase tracking-wide text-slate-400">File</span>
            <input
              type="file"
              accept=".csv,.json"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
              className="w-full rounded-lg border border-slate-600 bg-slate-950 px-3 py-2 text-sm"
            />
          </label>

          <label>
            <span className="mb-1 block text-xs uppercase tracking-wide text-slate-400">Source Type</span>
            <select
              value={sourceType}
              onChange={(e) => setSourceType(e.target.value)}
              className="w-full rounded-lg border border-slate-600 bg-slate-950 px-3 py-2 text-sm"
            >
              {sourceTypes.map((source) => (
                <option key={source.value} value={source.value}>{source.label}</option>
              ))}
            </select>
          </label>

          <button
            disabled={submitting || !file}
            className="md:col-span-3 rounded-xl bg-gradient-to-r from-ops-600 to-cyan-500 px-4 py-2 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-60"
          >
            {submitting ? "Uploading..." : "Start Ingestion"}
          </button>
        </form>

        {submitting ? (
          <div className="mt-4">
            <LoadingState message={`Uploading ${progress}%`} />
          </div>
        ) : null}
        {error ? <div className="mt-4"><ErrorState message={error} /></div> : null}
      </section>

      {result ? (
        <section className="glass-panel p-5">
          <h3 className="font-heading text-lg font-semibold">Ingestion Result Summary</h3>
          <div className="mt-3 grid gap-3 sm:grid-cols-3">
            <div className="rounded-lg border border-slate-700/70 bg-slate-900/70 p-3 text-sm">Total Rows: <span className="font-semibold">{result.total || 0}</span></div>
            <div className="rounded-lg border border-emerald-500/30 bg-emerald-500/10 p-3 text-sm">Saved Rows: <span className="font-semibold">{result.saved || 0}</span></div>
            <div className="rounded-lg border border-rose-500/30 bg-rose-500/10 p-3 text-sm">Failed Rows: <span className="font-semibold">{result.failed || 0}</span></div>
          </div>

          <div className="mt-4 grid gap-4 lg:grid-cols-2">
            <article className="rounded-lg border border-slate-700/70 bg-slate-900/70 p-3">
              <p className="mb-2 text-sm font-medium">Row-Level Ingestion Errors</p>
              {(result.error_log?.errors || []).length ? (
                <ul className="space-y-2 text-xs text-slate-300">
                  {result.error_log.errors.map((err, idx) => (
                    <li key={`${err.row || idx}-${idx}`} className="rounded bg-slate-950/80 p-2">
                      Row {err.row || "?"}: {(err.errors || []).join(" | ") || "Unknown error"}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-xs text-slate-400">No row-level errors returned. If failed rows exist, inspect IngestionJob.error_log in backend.</p>
              )}
            </article>

            <article className="rounded-lg border border-slate-700/70 bg-slate-900/70 p-3">
              <p className="mb-2 text-sm font-medium">Normalization Warnings</p>
              {(result.normalization_warnings || []).length ? (
                <ul className="space-y-2 text-xs text-amber-100">
                  {result.normalization_warnings.map((warning, idx) => (
                    <li key={`${warning}-${idx}`} className="rounded bg-amber-500/10 p-2">{warning}</li>
                  ))}
                </ul>
              ) : (
                <p className="text-xs text-slate-400">No normalization warnings returned for this upload.</p>
              )}
            </article>
          </div>
        </section>
      ) : null}
    </div>
  );
}
