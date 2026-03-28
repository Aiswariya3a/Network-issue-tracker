import IssueTypePieChart from "../charts/IssueTypePieChart";
import LocationBarChart from "../charts/LocationBarChart";
import StatusPieChart from "../charts/StatusPieChart";

function ChartCard({ title, children, heightClass = "h-72" }) {
  return (
    <div className="rounded-xl2 border border-cardBorder bg-white p-4 shadow-soft">
      <h3 className="mb-3 text-sm font-semibold text-slate-700">{title}</h3>
      <div className={heightClass}>{children}</div>
    </div>
  );
}

function DashboardCharts({ dashboard }) {
  return (
    <section className="grid grid-cols-1 gap-4 xl:grid-cols-3">
      <ChartCard title="Status Distribution">
        <StatusPieChart statusSummary={dashboard.status_summary} />
      </ChartCard>
      <ChartCard title="Issue Type Distribution">
        <IssueTypePieChart issueTypes={dashboard.issue_types} />
      </ChartCard>
      <ChartCard title="Location-wise Issues" heightClass="h-72">
        <LocationBarChart locationStats={dashboard.location_stats} />
      </ChartCard>
    </section>
  );
}

export default DashboardCharts;
