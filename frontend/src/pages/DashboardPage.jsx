import { useEffect, useMemo, useState } from "react";
import DashboardCharts from "../components/DashboardCharts";
import ErrorMessage from "../components/ErrorMessage";
import Header from "../components/Header";
import IssuesTable from "../components/IssuesTable";
import LoadingSpinner from "../components/LoadingSpinner";
import SummaryCards from "../components/SummaryCards";
import { fetchDashboard, fetchIssues } from "../services/api";

function DashboardPage() {
  const [issues, setIssues] = useState([]);
  const [dashboard, setDashboard] = useState({
    issue_types: {},
    status_summary: { Resolved: 0, "Not Resolved": 0 },
    location_stats: {},
    clusters: []
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadData = async () => {
    try {
      setError("");
      const [issuesData, dashboardData] = await Promise.all([fetchIssues(), fetchDashboard()]);
      console.log("GET /issues response:", issuesData);
      console.log("GET /dashboard response:", dashboardData);
      setIssues(issuesData);
      setDashboard(dashboardData);
    } catch (err) {
      console.error("Dashboard load error:", err?.response || err);
      const message = err?.response?.data?.detail || "Unable to load data";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    const intervalId = setInterval(loadData, 30000);
    return () => clearInterval(intervalId);
  }, []);

  const summary = useMemo(() => {
    const resolved = dashboard.status_summary?.Resolved || 0;
    const notResolved = dashboard.status_summary?.["Not Resolved"] || 0;
    return {
      total: resolved + notResolved,
      resolved,
      notResolved
    };
  }, [dashboard.status_summary]);

  const hasAnyData = useMemo(() => {
    return (
      summary.total > 0 ||
      Object.keys(dashboard.issue_types || {}).length > 0 ||
      Object.keys(dashboard.location_stats || {}).length > 0 ||
      issues.length > 0
    );
  }, [dashboard.issue_types, dashboard.location_stats, issues.length, summary.total]);

  return (
    <div className="min-h-screen bg-bgLight">
      <Header />
      <main className="mx-auto flex w-full max-w-7xl flex-col gap-6 px-4 py-6 sm:px-6 lg:px-8">
        {loading ? <LoadingSpinner label="Loading dashboard..." /> : null}
        {!loading && error ? <ErrorMessage message={error} /> : null}
        {!loading && !error ? (
          <>
            <SummaryCards summary={summary} />
            {!hasAnyData ? (
              <div className="rounded-xl2 border border-cardBorder bg-white p-8 text-center text-slate-500 shadow-soft">
                No data available.
              </div>
            ) : (
              <>
                <DashboardCharts dashboard={dashboard} />
                <section className="space-y-3">
                  <h2 className="text-lg font-semibold text-primaryDark">Recent Issues</h2>
                  <IssuesTable issues={issues} />
                </section>
              </>
            )}
          </>
        ) : null}
      </main>
    </div>
  );
}

export default DashboardPage;
