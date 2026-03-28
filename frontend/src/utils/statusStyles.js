export function getStatusClasses(status) {
  switch (status) {
    case "Resolved":
      return "bg-green-100 text-success";
    case "Not Resolved":
      return "bg-red-100 text-danger";
    default:
      return "bg-slate-100 text-slate-600";
  }
}
