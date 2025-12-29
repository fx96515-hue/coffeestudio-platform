"use client";

import { useState, useMemo } from "react";

export type Column<T> = {
  key: string;
  label: string;
  render?: (item: T) => React.ReactNode;
  sortable?: boolean;
};

export type DataTableProps<T> = {
  columns: Column<T>[];
  data: T[];
  keyField: keyof T;
  emptyMessage?: string;
};

export default function DataTable<T extends Record<string, any>>({
  columns,
  data,
  keyField,
  emptyMessage = "No data available",
}: DataTableProps<T>) {
  const [sortKey, setSortKey] = useState<string | null>(null);
  const [sortDir, setSortDir] = useState<"asc" | "desc">("asc");

  const sortedData = useMemo(() => {
    if (!sortKey) return data;
    
    const sorted = [...data].sort((a, b) => {
      const aVal = a[sortKey];
      const bVal = b[sortKey];
      
      if (aVal === bVal) return 0;
      if (aVal == null) return 1;
      if (bVal == null) return -1;
      
      if (typeof aVal === "number" && typeof bVal === "number") {
        return sortDir === "asc" ? aVal - bVal : bVal - aVal;
      }
      
      const aStr = String(aVal).toLowerCase();
      const bStr = String(bVal).toLowerCase();
      return sortDir === "asc" ? aStr.localeCompare(bStr) : bStr.localeCompare(aStr);
    });
    
    return sorted;
  }, [data, sortKey, sortDir]);

  const handleSort = (key: string) => {
    if (sortKey === key) {
      setSortDir(sortDir === "asc" ? "desc" : "asc");
    } else {
      setSortKey(key);
      setSortDir("asc");
    }
  };

  return (
    <div className="tableWrap">
      <table className="table">
        <thead>
          <tr>
            {columns.map((col) => {
              const isSortable = col.sortable !== false;
              const isSortedColumn = sortKey === col.key;
              const ariaSort =
                isSortable && isSortedColumn
                  ? sortDir === "asc"
                    ? "ascending"
                    : "descending"
                  : isSortable
                  ? "none"
                  : undefined;

              return (
                <th
                  key={col.key}
                  onClick={() => isSortable && handleSort(col.key)}
                  onKeyDown={(event) => {
                    if (!isSortable) return;
                    if (event.key === "Enter" || event.key === " ") {
                      event.preventDefault();
                      handleSort(col.key);
                    }
                  }}
                  style={{ cursor: isSortable ? "pointer" : "default" }}
                  role={isSortable ? "button" : undefined}
                  aria-sort={ariaSort as React.AriaAttributes["aria-sort"]}
                  tabIndex={isSortable ? 0 : undefined}
                >
                  {col.label}
                  {isSortedColumn && (
                    <span style={{ marginLeft: 4 }}>
                      {sortDir === "asc" ? "↑" : "↓"}
                    </span>
                  )}
                </th>
              );
            })}
          </tr>
        </thead>
        <tbody>
          {sortedData.length === 0 ? (
            <tr>
              <td colSpan={columns.length} className="muted" style={{ padding: 16, textAlign: "center" }}>
                {emptyMessage}
              </td>
            </tr>
          ) : (
            sortedData.map((item) => (
              <tr key={String(item[keyField])}>
                {columns.map((col) => (
                  <td key={col.key}>
                    {col.render ? col.render(item) : String(item[col.key] ?? "–")}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}
