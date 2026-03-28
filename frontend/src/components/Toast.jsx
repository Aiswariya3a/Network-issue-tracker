function Toast({ message, type = "success" }) {
  if (!message) return null;

  const classes =
    type === "error"
      ? "bg-red-600 text-white"
      : "bg-primaryDark text-white";

  return (
    <div className={`fixed bottom-6 right-6 z-50 rounded-xl2 px-4 py-3 text-sm shadow-soft ${classes}`}>
      {message}
    </div>
  );
}

export default Toast;
