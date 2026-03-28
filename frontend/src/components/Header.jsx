import { Link, useLocation } from "react-router-dom";
import { clearAuthToken, isAuthenticated } from "../utils/auth";

function Header() {
  const location = useLocation();
  const loggedIn = isAuthenticated();

  const handleLogout = () => {
    clearAuthToken();
    window.location.href = "/login";
  };

  return (
    <header className="sticky top-0 z-10 border-b border-cardBorder bg-white/95 backdrop-blur">
      <div className="mx-auto flex w-full max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary text-lg font-bold text-white">
            NI
          </div>
          <div>
            <h1 className="font-poppins text-lg font-semibold text-primaryDark sm:text-xl">
              Network Issue Monitoring System
            </h1>
          </div>
        </div>

        <nav className="flex items-center gap-2">
          <Link
            to="/"
            className={`rounded-lg px-3 py-2 text-sm font-medium transition ${
              location.pathname === "/"
                ? "bg-primary text-white"
                : "text-slate-600 hover:bg-slate-100"
            }`}
          >
            Dashboard
          </Link>
          <Link
            to="/admin"
            className={`rounded-lg px-3 py-2 text-sm font-medium transition ${
              location.pathname === "/admin"
                ? "bg-primary text-white"
                : "text-slate-600 hover:bg-slate-100"
            }`}
          >
            Admin
          </Link>
          {loggedIn ? (
            <button
              type="button"
              onClick={handleLogout}
              className="rounded-lg bg-accentRed px-3 py-2 text-sm font-medium text-white transition hover:opacity-90"
            >
              Logout
            </button>
          ) : (
            <Link
              to="/login"
              className="rounded-lg bg-primary px-3 py-2 text-sm font-medium text-white transition hover:bg-primaryDark"
            >
              Login
            </Link>
          )}
        </nav>
      </div>
    </header>
  );
}

export default Header;
