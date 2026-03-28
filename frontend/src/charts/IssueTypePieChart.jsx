import "./chartSetup";
import { Pie } from "react-chartjs-2";

function IssueTypePieChart({ issueTypes }) {
  const labels = Object.keys(issueTypes || {});
  const values = labels.map((label) => issueTypes[label]);
  const hasData = values.length > 0;

  const data = {
    labels: hasData ? labels : ["No Data"],
    datasets: [
      {
        data: hasData ? values : [1],
        backgroundColor:
          hasData
            ? ["#1E88E5", "#64B5F6", "#1565C0", "#E53935", "#90CAF9", "#42A5F5"]
            : ["#CBD5E1"],
        borderColor: "#ffffff",
        borderWidth: 2
      }
    ]
  };

  return <Pie data={data} options={{ responsive: true, maintainAspectRatio: false }} />;
}

export default IssueTypePieChart;
