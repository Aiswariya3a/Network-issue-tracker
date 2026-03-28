import "./chartSetup";
import { Pie } from "react-chartjs-2";

function StatusPieChart({ statusSummary }) {
  const data = {
    labels: ["Resolved", "Not Resolved"],
    datasets: [
      {
        data: [statusSummary?.Resolved || 0, statusSummary?.["Not Resolved"] || 0],
        backgroundColor: ["#16A34A", "#E53935"],
        borderColor: "#ffffff",
        borderWidth: 2
      }
    ]
  };

  return <Pie data={data} options={{ responsive: true, maintainAspectRatio: false }} />;
}

export default StatusPieChart;
