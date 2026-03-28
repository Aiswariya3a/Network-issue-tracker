import { useEffect, useMemo, useState } from "react";
import AdminIssuesTable from "../components/AdminIssuesTable";
import ErrorMessage from "../components/ErrorMessage";
import FilterBar from "../components/FilterBar";
import Header from "../components/Header";
import LoadingSpinner from "../components/LoadingSpinner";
import Toast from "../components/Toast";
import { fetchIssues, updateIssueStatus } from "../services/api";

function AdminPage() {
  const [issues, setIssues] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [filters, setFilters] = useState({ floor: "", issueType: "", status: "" });
  const [selectedStatusMap, setSelectedStatusMap] = useState({});
  const [resolutionNoteMap, setResolutionNoteMap] = useState({});
  const [pendingMap, setPendingMap] = useState({});
  const [toast, setToast] = useState({ message: "", type: "success" });

  const loadIssues = async () => {
    try {
      setError("");
      const data = await fetchIssues();
      setIssues(data);
    } catch (err) {
      const message = err?.response?.data?.detail || "Failed to load issues.";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadIssues();
  }, []);

  const filteredIssues = useMemo(() => {
    return issues.filter((issue) => {
      const floorMatch = !filters.floor || issue.floor === filters.floor;
      const issueTypeMatch = !filters.issueType || issue.issue_type === filters.issueType;
      const statusMatch = !filters.status || issue.status === filters.status;
      return floorMatch && issueTypeMatch && statusMatch;
    });
  }, [issues, filters]);

  const options = useMemo(
    () => ({
      floors: Array.from(new Set(issues.map((item) => item.floor).filter(Boolean))).sort(),
      issueTypes: Array.from(new Set(issues.map((item) => item.issue_type).filter(Boolean))).sort(),
      statuses: ["Resolved", "Not Resolved"]
    }),
    [issues]
  );

  const showToast = (message, type = "success") => {
    setToast({ message, type });
    window.setTimeout(() => setToast({ message: "", type: "success" }), 2500);
  };

  const handleStatusChange = (rowIndex, value) => {
    setSelectedStatusMap((prev) => ({ ...prev, [rowIndex]: value }));
    if (value !== "Resolved") {
      setResolutionNoteMap((prev) => ({ ...prev, [rowIndex]: "" }));
    }
  };

  const handleResolutionNoteChange = (rowIndex, value) => {
    setResolutionNoteMap((prev) => ({ ...prev, [rowIndex]: value }));
  };

  const handleUpdate = async (rowIndex) => {
    const issue = issues.find((item) => item.row_index === rowIndex);
    if (!issue) return;
    const statusToSend = selectedStatusMap[rowIndex] || issue.status;
    const resolutionNote = resolutionNoteMap[rowIndex] || "";

    setPendingMap((prev) => ({ ...prev, [rowIndex]: true }));
    try {
      await updateIssueStatus(rowIndex, statusToSend, resolutionNote);
      setIssues((prev) =>
        prev.map((item) => (item.row_index === rowIndex ? { ...item, status: statusToSend } : item))
      );
      showToast("Status updated successfully.", "success");
    } catch (err) {
      if (err?.response?.status === 401) {
        window.location.href = "/login";
        return;
      }
      const message = err?.response?.data?.detail || "Failed to update status.";
      showToast(message, "error");
    } finally {
      setPendingMap((prev) => ({ ...prev, [rowIndex]: false }));
    }
  };

  return (
    <div className="min-h-screen bg-bgLight">
      <Header />
      <main className="mx-auto flex w-full max-w-7xl flex-col gap-5 px-4 py-6 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold text-primaryDark">Admin Panel</h2>
          <button
            type="button"
            onClick={loadIssues}
            className="rounded-lg border border-primary px-3 py-2 text-sm font-semibold text-primary transition hover:bg-primary hover:text-white"
          >
            Refresh
          </button>
        </div>

        <FilterBar
          filters={filters}
          options={options}
          onChange={(key, value) => setFilters((prev) => ({ ...prev, [key]: value }))}
          onClear={() => setFilters({ floor: "", issueType: "", status: "" })}
        />

        {loading ? <LoadingSpinner label="Loading admin data..." /> : null}
        {!loading && error ? <ErrorMessage message={error} /> : null}
        {!loading && !error ? (
          <AdminIssuesTable
            issues={filteredIssues}
            pendingMap={pendingMap}
            selectedStatusMap={selectedStatusMap}
            resolutionNoteMap={resolutionNoteMap}
            onStatusChange={handleStatusChange}
            onResolutionNoteChange={handleResolutionNoteChange}
            onUpdate={handleUpdate}
          />
        ) : null}
      </main>
      <Toast message={toast.message} type={toast.type} />
    </div>
  );
}

export default AdminPage;
