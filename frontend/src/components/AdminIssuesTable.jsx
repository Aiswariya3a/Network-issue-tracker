import { getStatusClasses } from "../utils/statusStyles";

const STATUS_OPTIONS = ["NOT RESOLVED", "ACKNOWLEDGED", "RESOLVED"];

function formatTimestamp(rawTimestamp) {
  if (!rawTimestamp) {
    return { date: "-", time: "-" };
  }

  const parsed = new Date(rawTimestamp);
  if (Number.isNaN(parsed.getTime())) {
    const split = String(rawTimestamp).split(" ");
    return {
      date: split[0] || rawTimestamp,
      time: split.slice(1).join(" ") || "-"
    };
  }

  return {
    date: parsed.toLocaleDateString(),
    time: parsed.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
  };
}

function AdminActions({
  issue,
  pendingMap,
  selectedStatusMap,
  resolutionNoteMap,
  ictNameMap,
  onStatusChange,
  onResolutionNoteChange,
  onIctNameChange,
  onUpdate
}) {
  const isPending = Boolean(pendingMap[issue.row_index]);
  const selectedStatus = selectedStatusMap[issue.row_index] || issue.status;
  const resolutionText = resolutionNoteMap[issue.row_index] ?? issue.resolution_remark ?? "";
  const ictNameText = ictNameMap[issue.row_index] ?? issue.ict_member_name ?? "";
  const needsRemark = selectedStatus === "ACKNOWLEDGED";
  const disableDetailInputs = selectedStatus === "NOT RESOLVED";
  const isUpdated = issue.status === "ACKNOWLEDGED" || issue.status === "RESOLVED";
  const finalIctName = issue.ict_member_name || ictNameText || "-";
  const finalResolutionRemark = issue.resolution_remark || resolutionText || "-";

  if (isUpdated) {
    return (
      <div className="flex w-[220px] max-w-[220px] flex-col gap-2 rounded-lg border border-slate-200 bg-slate-50 p-2">
        <p className="text-[11px] font-semibold uppercase tracking-wide text-slate-500">ICT Name</p>
        <p className="break-words text-sm text-slate-700">{finalIctName}</p>
        <p className="text-[11px] font-semibold uppercase tracking-wide text-slate-500">Resolution Note</p>
        <p className="break-words text-sm text-slate-700">{finalResolutionRemark}</p>
      </div>
    );
  }

  return (
    <div className="flex w-[220px] max-w-[220px] flex-col gap-2">
      <select
        value={selectedStatus}
        onChange={(e) => onStatusChange(issue.row_index, e.target.value)}
        disabled={isPending}
        className="w-full rounded-lg border border-slate-300 px-2.5 py-2 text-sm focus:border-primary focus:outline-none"
      >
        {STATUS_OPTIONS.map((status) => (
          <option key={status} value={status}>
            {status}
          </option>
        ))}
      </select>

      <input
        type="text"
        value={ictNameText}
        onChange={(e) => onIctNameChange(issue.row_index, e.target.value)}
        placeholder="ICT member name (required)"
        disabled={isPending || disableDetailInputs}
        className="w-full rounded-lg border border-slate-300 px-2.5 py-2 text-sm focus:border-primary focus:outline-none"
      />

      <textarea
        value={resolutionText}
        onChange={(e) => onResolutionNoteChange(issue.row_index, e.target.value)}
        placeholder={needsRemark ? "Resolution note (required for ACKNOWLEDGED)" : "Resolution note (optional)"}
        rows={2}
        disabled={isPending || disableDetailInputs}
        className="h-20 w-full resize-none rounded-lg border border-slate-300 px-2.5 py-2 text-sm focus:border-primary focus:outline-none"
      />
      <button
        type="button"
        disabled={isPending}
        onClick={() => onUpdate(issue.row_index)}
        className="rounded-lg bg-primary px-3 py-2 text-xs font-semibold text-white transition hover:bg-primaryDark disabled:cursor-not-allowed disabled:opacity-60"
      >
        {isPending ? "Updating..." : "Update"}
      </button>
    </div>
  );
}

function AdminIssuesTable({
  issues,
  pendingMap,
  selectedStatusMap,
  resolutionNoteMap,
  ictNameMap,
  onStatusChange,
  onResolutionNoteChange,
  onIctNameChange,
  onUpdate
}) {
  return (
    <div className="rounded-xl2 border border-cardBorder bg-white shadow-soft">
      <div className="divide-y divide-slate-100 md:hidden">
        {issues.map((issue, index) => {
          const when = formatTimestamp(issue.timestamp);
          return (
            <article key={issue.complaint_key || issue.row_index} className="space-y-3 p-4">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="text-sm font-semibold text-slate-700">S.No: {index + 1}</p>
                  <p className="text-xs text-slate-500">{when.date} {when.time}</p>
                </div>
                <span className={`rounded-full px-2.5 py-1 text-xs font-semibold ${getStatusClasses(issue.status)}`}>
                  {issue.status}
                </span>
              </div>
              <p className="text-sm text-slate-700">{issue.issue_type || "-"}</p>
              <p className="text-sm text-slate-600">{issue.location || `${issue.floor}-${issue.room}` || "-"}</p>
              <p className="break-all text-xs text-slate-500">{issue.email || "-"}</p>
              <p className="text-sm text-slate-600">{issue.description || "-"}</p>
              <AdminActions
                issue={issue}
                pendingMap={pendingMap}
                selectedStatusMap={selectedStatusMap}
                resolutionNoteMap={resolutionNoteMap}
                ictNameMap={ictNameMap}
                onStatusChange={onStatusChange}
                onResolutionNoteChange={onResolutionNoteChange}
                onIctNameChange={onIctNameChange}
                onUpdate={onUpdate}
              />
            </article>
          );
        })}
        {issues.length === 0 ? <p className="p-6 text-center text-sm text-slate-500">No matching issues found.</p> : null}
      </div>

      <div className="hidden overflow-x-auto md:block">
        <table className="w-full table-fixed divide-y divide-slate-200 text-sm">
          <thead className="bg-slate-50">
            <tr>
              <th className="w-14 px-2 py-3 text-left font-semibold text-slate-600">S.No</th>
              <th className="w-24 px-2 py-3 text-left font-semibold text-slate-600">Date</th>
              <th className="w-20 px-2 py-3 text-left font-semibold text-slate-600">Time</th>
              <th className="w-40 px-2 py-3 text-left font-semibold text-slate-600">Email</th>
              <th className="w-36 px-2 py-3 text-left font-semibold text-slate-600">Location</th>
              <th className="w-32 px-2 py-3 text-left font-semibold text-slate-600">Issue Type</th>
              <th className="px-2 py-3 text-left font-semibold text-slate-600">Description</th>
              <th className="w-32 px-2 py-3 text-left font-semibold text-slate-600">Current</th>
              <th className="w-[240px] px-4 py-3 text-left font-semibold text-slate-600">Update</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 bg-white">
            {issues.map((issue, index) => {
              const when = formatTimestamp(issue.timestamp);
              return (
                <tr key={issue.complaint_key || issue.row_index} className="align-top transition hover:bg-slate-50">
                  <td className="whitespace-nowrap px-2 py-3 text-slate-600">{index + 1}</td>
                  <td className="whitespace-nowrap px-2 py-3 text-slate-700">{when.date}</td>
                  <td className="whitespace-nowrap px-2 py-3 text-slate-700">{when.time}</td>
                  <td className="break-all px-2 py-3 text-slate-700">
                    {issue.email || "-"}
                  </td>
                  <td className="break-words px-2 py-3 text-slate-700">
                    {issue.location || `${issue.floor}-${issue.room}` || "-"}
                  </td>
                  <td className="break-words px-2 py-3 text-slate-700">
                    {issue.issue_type || "-"}
                  </td>
                  <td className="break-words px-2 py-3 text-slate-700">{issue.description || "-"}</td>
                  <td className="px-2 py-3">
                    <span className={`rounded-full px-2.5 py-1 text-xs font-semibold ${getStatusClasses(issue.status)}`}>
                      {issue.status}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <AdminActions
                      issue={issue}
                      pendingMap={pendingMap}
                      selectedStatusMap={selectedStatusMap}
                      resolutionNoteMap={resolutionNoteMap}
                      ictNameMap={ictNameMap}
                      onStatusChange={onStatusChange}
                      onResolutionNoteChange={onResolutionNoteChange}
                      onIctNameChange={onIctNameChange}
                      onUpdate={onUpdate}
                    />
                  </td>
                </tr>
              );
            })}
            {issues.length === 0 && (
              <tr>
                <td colSpan={9} className="px-4 py-6 text-center text-slate-500">
                  No matching issues found.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default AdminIssuesTable;
