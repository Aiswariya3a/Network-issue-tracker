function LoadingSpinner({ label = "Loading..." }) {
  return (
    <div className="flex items-center justify-center py-16">
      <div className="flex items-center gap-3 text-primaryDark">
        <div className="h-6 w-6 animate-spin rounded-full border-2 border-primary border-t-transparent" />
        <span className="text-sm font-medium">{label}</span>
      </div>
    </div>
  );
}

export default LoadingSpinner;
