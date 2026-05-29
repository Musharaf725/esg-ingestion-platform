import { useMemo } from "react";

export default function DataTable({
  columns,
  rows,
  sortKey,
  sortDirection,
  onSort,
  rowKey,
  onRowClick,
  selectedIds = [],
  onToggleSelect,
}) {
  const normalizedRows = useMemo(() => rows || [], [rows]);

  return (
    <div className="overflow-x-auto rounded-xl border border-slate-700/60">
      <table className="min-w-full border-collapse text-sm">
        <thead className="bg-slate-900/90">
          <tr>
            {onToggleSelect ? <th className="px-3 py-3 text-left"><span className="sr-only">Select</span></th> : null}
            {columns.map((column) => {
              const isSorted = sortKey === column.key;
              return (
                <th key={column.key} className="px-3 py-3 text-left text-xs uppercase tracking-wide text-slate-300">
                  {column.sortable ? (
                    <button className="inline-flex items-center gap-1" onClick={() => onSort(column.key)}>
                      <span>{column.header}</span>
                      <span className="text-slate-500">{isSorted ? (sortDirection === "asc" ? "▲" : "▼") : "↕"}</span>
                    </button>
                  ) : (
                    column.header
                  )}
                </th>
              );
            })}
          </tr>
        </thead>
        <tbody>
          {normalizedRows.map((row) => {
            const key = rowKey(row);
            return (
              <tr
                key={key}
                className="cursor-pointer border-t border-slate-800/80 bg-slate-950/60 transition hover:bg-slate-800/50"
                onClick={() => onRowClick?.(row)}
              >
                {onToggleSelect ? (
                  <td className="px-3 py-3" onClick={(e) => e.stopPropagation()}>
                    <input
                      type="checkbox"
                      checked={selectedIds.includes(key)}
                      onChange={() => onToggleSelect(key)}
                      className="h-4 w-4 rounded border-slate-500 bg-slate-900 text-ops-500"
                    />
                  </td>
                ) : null}
                {columns.map((column) => (
                  <td key={`${key}:${column.key}`} className="px-3 py-3 text-slate-100">
                    {column.render ? column.render(row) : row[column.key]}
                  </td>
                ))}
              </tr>
            );
          })}
          {normalizedRows.length === 0 ? (
            <tr>
              <td colSpan={columns.length + (onToggleSelect ? 1 : 0)} className="px-3 py-8 text-center text-slate-400">
                No records found.
              </td>
            </tr>
          ) : null}
        </tbody>
      </table>
    </div>
  );
}
