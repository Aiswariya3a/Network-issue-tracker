import "./chartSetup";
import { Bar } from "react-chartjs-2";

function LocationBarChart({ locationStats }) {
  const labels = Object.keys(locationStats || {});
  const values = labels.map((label) => locationStats[label]);

  const data = {
    labels,
    datasets: [
      {
        label: "Issues",
        data: values,
        backgroundColor: "#1E88E5",
        borderRadius: 6
      }
    ]
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { display: false } },
    scales: {
      y: {
        beginAtZero: true,
        ticks: { stepSize: 1 }
      }
    }
  };

  return <Bar data={data} options={options} />;
}

export default LocationBarChart;
