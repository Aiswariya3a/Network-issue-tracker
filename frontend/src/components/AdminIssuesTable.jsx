import { getStatusClasses } from "../utils/statusStyles";

const STATUS_OPTIONS = ["Resolved", "Not Resolved"];

function AdminIssuesTable({
  issues,
  pendingMap,
  selectedStatusMap,
  resolutionNoteMap,
  onStatusChange,
  onResolutionNoteChange,
  onUpdate
}) {
  return (
    <div className="overflow-x-auto rounded-xl2 border border-cardBorder bg-white shadow-soft">
      <table className="min-w-full divide-y divide-slate-200 text-sm">
        <thead className="bg-slate-50">
          <tr>
            <th className="px-4 py-3 text-left font-semibold text-slate-600">Row</th>
            <th className="px-4 py-3 text-left font-semibold text-slate-600">Location</th>
            <th className="px-4 py-3 text-left font-semibold text-slate-600">Issue Type</th>
            <th className="px-4 py-3 text-left font-semibold text-slate-600">Description</th>
            <th className="px-4 py-3 text-left font-semibold text-slate-600">Current</th>
            <th className="px-4 py-3 text-left font-semibold text-slate-600">Update Status</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100 bg-white">
          {issues.map((issue) => {
            const isPending = Boolean(pendingMap[issue.row_index]);
            const selectedStatus = selectedStatusMap[issue.row_index] || issue.status;
            return (
              <tr key={issue.row_index} className="transition hover:bg-slate-50">
                <td className="px-4 py-3 text-slate-600">{issue.row_index}</td>
                <td className="px-4 py-3 text-slate-700">{issue.location || `${issue.floor}-${issue.room}`}</td>
                <td className="px-4 py-3 text-slate-700">{issue.issue_type || "-"}</td>
                <td className="px-4 py-3 text-slate-700">{issue.description || "-"}</td>
                <td className="px-4 py-3">
                  <span className={`rounded-full px-2.5 py-1 text-xs font-semibold ${getStatusClasses(issue.status)}`}>
                    {issue.status}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <div className="flex flex-wrap items-center gap-2">
                    <select
                      value={selectedStatus}
                      onChange={(e) => onStatusChange(issue.row_index, e.target.value)}
                      className="rounded-lg border border-slate-300 px-2.5 py-1.5 text-sm focus:border-primary focus:outline-none"
                    >
                      {STATUS_OPTIONS.map((status) => (
                        <option key={status} value={status}>
                          {status}
                        </option>
                      ))}
                    </select>
                    {selectedStatus === "Resolved" ? (
                      <input
                        type="text"
                        value={resolutionNoteMap[issue.row_index] || ""}
                        onChange={(e) => onResolutionNoteChange(issue.row_index, e.target.value)}
                        placeholder="Optional resolution note"
                        className="min-w-[220px] rounded-lg border border-slate-300 px-2.5 py-1.5 text-sm focus:border-primary focus:outline-none"
                      />
                    ) : null}
                    <button
                      type="button"
                      disabled={isPending}
                      onClick={() => onUpdate(issue.row_index)}
                      className="rounded-lg bg-primary px-3 py-1.5 text-xs font-semibold text-white transition hover:bg-primaryDark disabled:cursor-not-allowed disabled:opacity-60"
                    >
                      {isPending ? "Updating..." : "Update"}
                    </button>
                  </div>
                </td>
              </tr>
            );
          })}
          {issues.length === 0 && (
            <tr>
              <td colSpan={6} className="px-4 py-6 text-center text-slate-500">
                No matching issues found.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}

export default AdminIssuesTable;
