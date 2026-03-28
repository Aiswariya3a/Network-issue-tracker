export function getStatusClasses(status) {
  switch (status) {
    case "RESOLVED":
      return "bg-green-100 text-success";
    case "ACKNOWLEDGED":
      return "bg-amber-100 text-amber-700";
    case "NOT RESOLVED":
      return "bg-red-100 text-danger";
    default:
      return "bg-slate-100 text-slate-600";
  }
}
