function ErrorMessage({ message }) {
  return (
    <div className="rounded-xl2 border border-red-200 bg-red-50 p-4 text-sm text-red-700 shadow-soft">
      {message}
    </div>
  );
}

export default ErrorMessage;
