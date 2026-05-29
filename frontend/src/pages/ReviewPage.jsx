import { useEffect, useMemo, useState } from "react";
import {
  approveRecord,
  bulkApprove,
  flagRecord,
  getReviewRecords,
  rejectRecord,
} from "../api/reviewApi";
import DataTable from "../components/DataTable";
import ErrorState from "../components/ErrorState";
import LoadingState from "../components/LoadingState";
import RecordDetailsModal from "../components/RecordDetailsModal";
import StatusBadge from "../components/StatusBadge";
import { formatDate } from "../utils/format";

const defaultFilters = {
  status: "",
  source_type: "",
  scope: "",
  suspicious_only: false,
  page_size: 20,
};

export default function ReviewPage() {
  const [rows, setRows] = useState([]);
  const [count, setCount] = useState(0);
  const [page, setPage] = useState(1);
  const [filters, setFilters] = useState(defaultFilters);
  const [searchText, setSearchText] = useState("");
  const [sortKey, setSortKey] = useState("created_at");
  const [sortDirection, setSortDirection] = useState("desc");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [activeRecord, setActiveRecord] = useState(null);
  const [selectedIds, setSelectedIds] = useState([]);

  const fetchRecords = async () => {
    setLoading(true);
    setError("");

    try {
      const query = {
        page,
        page_size: filters.page_size,
      };
      if (filters.status) query.status = filters.status;
      if (filters.source_type) query.source_type = filters.source_type;
      if (filters.scope) query.scope = filters.scope;
      if (filters.suspicious_only) query.suspicious_only = true;

      const data = await getReviewRecords(query);
      setRows(data.results || []);
      setCount(data.count || 0);
    } catch (err) {
      setError(err?.response?.data?.error || "Unable to load review records.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecords();
  }, [page, filters.status, filters.source_type, filters.scope, filters.suspicious_only, filters.page_size]);

  const processedRows = useMemo(() => {
    const search = searchText.trim().toLowerCase();
    const filtered = rows.filter((row) => {
      if (!search) return true;
      const source = row.raw_payload || {};
      const values = [
        source.plant,
        source.plant_code,
        source.meter,
        source.meter_id,
        row.period,
      ]
        .filter(Boolean)
        .map((v) => String(v).toLowerCase());
      return values.some((v) => v.includes(search));
    });

    const sorted = [...filtered].sort((a, b) => {
      const left = a[sortKey] ?? "";
      const right = b[sortKey] ?? "";

      if (left === right) return 0;
      if (sortDirection === "asc") return left > right ? 1 : -1;
      return left < right ? 1 : -1;
    });

    return sorted;
  }, [rows, searchText, sortDirection, sortKey]);

  const handleSort = (key) => {
    if (sortKey === key) {
      setSortDirection((current) => (current === "asc" ? "desc" : "asc"));
      return;
    }
    setSortKey(key);
    setSortDirection("asc");
  };

  const setFilter = (key, value) => {
    setPage(1);
    setFilters((prev) => ({ ...prev, [key]: value }));
  };

  const runRowAction = async (action) => {
    setError("");
    try {
      await action();
      await fetchRecords();
      setSelectedIds([]);
    } catch (err) {
      setError(err?.response?.data?.error || "Action failed.");
    }
  };

  const columns = [
    {
      key: "created_at",
      header: "Created",
      sortable: true,
      render: (row) => <span className="text-xs text-slate-300">{formatDate(row.created_at)}</span>,
    },
    {
      key: "source_type",
      header: "Source",
      sortable: true,
      render: (row) => <span className="uppercase">{row.source_type}</span>,
    },
    {
      key: "period",
      header: "Period",
      sortable: true,
    },
    {
      key: "scope",
      header: "Scope",
      sortable: true,
    },
    {
      key: "status",
      header: "Status",
      sortable: true,
      render: (row) => (
        <div className="flex flex-wrap gap-1">
          <StatusBadge value={row.status} />
          {(row.flag_reasons || []).length ? <StatusBadge value="suspicious" /> : null}
          {row.status === "approved" ? <StatusBadge value="locked" /> : null}
        </div>
      ),
    },
    {
      key: "actions",
      header: "Actions",
      sortable: false,
      render: (row) => (
        <div className="flex flex-wrap gap-1" onClick={(e) => e.stopPropagation()}>
          <button
            disabled={row.status !== "pending_review"}
            onClick={() => runRowAction(() => approveRecord(row.id, "Approved from review table"))}
            className="rounded border border-emerald-400/40 px-2 py-1 text-xs text-emerald-100 disabled:opacity-40"
          >
            Approve
          </button>
          <button
            disabled={row.status !== "pending_review"}
            onClick={() => {
              const reason = window.prompt("Rejection reason");
              if (!reason) return;
              runRowAction(() => rejectRecord(row.id, reason));
            }}
            className="rounded border border-rose-400/40 px-2 py-1 text-xs text-rose-100 disabled:opacity-40"
          >
            Reject
          </button>
          <button
            disabled={row.status === "approved"}
            onClick={() => {
              const reason = window.prompt("Flag reason");
              if (!reason) return;
              runRowAction(() => flagRecord(row.id, reason, "Flagged from review table"));
            }}
            className="rounded border border-amber-400/40 px-2 py-1 text-xs text-amber-100 disabled:opacity-40"
          >
            Flag
          </button>
        </div>
      ),
    },
  ];

  const totalPages = Math.max(1, Math.ceil(count / filters.page_size));

  return (
    <div className="space-y-4">
      <section className="glass-panel space-y-3 p-4">
        <div className="grid gap-3 md:grid-cols-5">
          <input
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            placeholder="Search plant / meter / period"
            className="rounded-lg border border-slate-600 bg-slate-950 px-3 py-2 text-sm md:col-span-2"
          />

          <select className="rounded-lg border border-slate-600 bg-slate-950 px-3 py-2 text-sm" value={filters.status} onChange={(e) => setFilter("status", e.target.value)}>
            <option value="">All Statuses</option>
            <option value="pending">Pending</option>
            <option value="pending_review">Pending Review</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
          </select>

          <select className="rounded-lg border border-slate-600 bg-slate-950 px-3 py-2 text-sm" value={filters.source_type} onChange={(e) => setFilter("source_type", e.target.value)}>
            <option value="">All Sources</option>
            <option value="sap">SAP</option>
            <option value="utility">Utility</option>
            <option value="travel">Travel</option>
          </select>

          <select className="rounded-lg border border-slate-600 bg-slate-950 px-3 py-2 text-sm" value={filters.scope} onChange={(e) => setFilter("scope", e.target.value)}>
            <option value="">All Scopes</option>
            <option value="scope_1">Scope 1</option>
            <option value="scope_2">Scope 2</option>
            <option value="scope_3">Scope 3</option>
          </select>
        </div>

        <div className="flex flex-wrap items-center justify-between gap-2">
          <label className="inline-flex items-center gap-2 text-sm text-slate-300">
            <input
              type="checkbox"
              checked={filters.suspicious_only}
              onChange={(e) => setFilter("suspicious_only", e.target.checked)}
              className="h-4 w-4 rounded border-slate-500 bg-slate-900"
            />
            Suspicious only
          </label>

          <button
            disabled={!selectedIds.length}
            onClick={() => runRowAction(() => bulkApprove(selectedIds, "Bulk approved by analyst"))}
            className="rounded-lg bg-ops-600 px-3 py-1.5 text-sm font-medium text-white disabled:opacity-50"
          >
            Bulk Approve ({selectedIds.length})
          </button>
        </div>
      </section>

      {loading ? <LoadingState message="Loading review queue..." /> : null}
      {error ? <ErrorState message={error} onRetry={fetchRecords} /> : null}

      {!loading ? (
        <section className="glass-panel p-2">
          <DataTable
            columns={columns}
            rows={processedRows}
            sortKey={sortKey}
            sortDirection={sortDirection}
            onSort={handleSort}
            rowKey={(row) => row.id}
            onRowClick={setActiveRecord}
            selectedIds={selectedIds}
            onToggleSelect={(id) =>
              setSelectedIds((prev) => (prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]))
            }
          />

          <div className="flex items-center justify-between px-3 py-3 text-sm text-slate-300">
            <p>
              Page {page} / {totalPages} | {count} records
            </p>
            <div className="flex gap-2">
              <button
                disabled={page <= 1}
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                className="rounded border border-slate-600 px-2 py-1 disabled:opacity-40"
              >
                Prev
              </button>
              <button
                disabled={page >= totalPages}
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                className="rounded border border-slate-600 px-2 py-1 disabled:opacity-40"
              >
                Next
              </button>
            </div>
          </div>
        </section>
      ) : null}

      <RecordDetailsModal record={activeRecord} onClose={() => setActiveRecord(null)} />
    </div>
  );
}
