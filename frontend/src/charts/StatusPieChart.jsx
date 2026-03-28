import "./chartSetup";
import { Pie } from "react-chartjs-2";

function StatusPieChart({ statusSummary }) {
  const data = {
    labels: ["RESOLVED", "ACKNOWLEDGED", "NOT RESOLVED"],
    datasets: [
      {
        data: [
          statusSummary?.RESOLVED || 0,
          statusSummary?.ACKNOWLEDGED || 0,
          statusSummary?.["NOT RESOLVED"] || 0
        ],
        backgroundColor: ["#16A34A", "#D97706", "#E53935"],
        borderColor: "#ffffff",
        borderWidth: 2
      }
    ]
  };

  return <Pie data={data} options={{ responsive: true, maintainAspectRatio: false }} />;
}

export default StatusPieChart;
