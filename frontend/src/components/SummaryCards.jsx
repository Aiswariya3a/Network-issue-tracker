function Card({ title, value, color }) {
  return (
    <div className="rounded-xl2 border border-cardBorder bg-white p-5 shadow-soft transition hover:-translate-y-0.5">
      <p className="text-sm font-medium text-slate-500">{title}</p>
      <p className={`mt-2 text-3xl font-bold ${color}`}>{value}</p>
    </div>
  );
}

function SummaryCards({ summary }) {
  return (
    <section className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
      <Card title="Total Issues" value={summary.total} color="text-primaryDark" />
      <Card title="Resolved" value={summary.resolved} color="text-success" />
      <Card title="Acknowledged" value={summary.acknowledged} color="text-amber-600" />
      <Card title="Not Resolved" value={summary.notResolved} color="text-danger" />
    </section>
  );
}

export default SummaryCards;
