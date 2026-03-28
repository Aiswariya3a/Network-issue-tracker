import { getStatusClasses } from "../utils/statusStyles";

function IssuesTable({ issues }) {
  return (
    <div className="overflow-x-auto rounded-xl2 border border-cardBorder bg-white shadow-soft">
      <table className="min-w-full divide-y divide-slate-200 text-sm">
        <thead className="bg-slate-50">
          <tr>
            <th className="px-4 py-3 text-left font-semibold text-slate-600">Email</th>
            <th className="px-4 py-3 text-left font-semibold text-slate-600">Location</th>
            <th className="px-4 py-3 text-left font-semibold text-slate-600">Issue Type</th>
            <th className="px-4 py-3 text-left font-semibold text-slate-600">Description</th>
            <th className="px-4 py-3 text-left font-semibold text-slate-600">Status</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100 bg-white">
          {issues.map((issue) => (
            <tr key={issue.row_index} className="transition hover:bg-slate-50">
              <td className="px-4 py-3 text-slate-700">{issue.email || "-"}</td>
              <td className="px-4 py-3 text-slate-700">{issue.location || `${issue.floor}-${issue.room}`}</td>
              <td className="px-4 py-3 text-slate-700">{issue.issue_type || "-"}</td>
              <td className="px-4 py-3 text-slate-700">{issue.description || "-"}</td>
              <td className="px-4 py-3">
                <span className={`rounded-full px-2.5 py-1 text-xs font-semibold ${getStatusClasses(issue.status)}`}>
                  {issue.status}
                </span>
              </td>
            </tr>
          ))}
          {issues.length === 0 && (
            <tr>
              <td colSpan={5} className="px-4 py-6 text-center text-slate-500">
                No issues available.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}

export default IssuesTable;
