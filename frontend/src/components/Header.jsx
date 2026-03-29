import { Link, useLocation } from "react-router-dom";
import { clearAuthToken, isAuthenticated, triggerLogoutRedirect } from "../utils/auth";

function Header() {
  const location = useLocation();
  const loggedIn = isAuthenticated();

  const handleLogout = () => {
    clearAuthToken();
    triggerLogoutRedirect();
  };

  return (
    <header className="sticky top-0 z-10 border-b border-cardBorder bg-white/95 backdrop-blur">
      <div className="mx-auto flex w-full max-w-7xl flex-col gap-3 px-4 py-3 sm:flex-row sm:items-center sm:justify-between sm:px-6 lg:px-8">
        <div className="flex items-center gap-3">
          <div className="flex h-9 min-w-[4.75rem] items-center justify-center rounded-lg bg-primary px-2 text-xs font-bold tracking-wide text-white sm:h-16 sm:min-w-[5rem] sm:rounded-full sm:px-3 sm:text-lg">
            kgNIMS
          </div>
          <div>
            <h1 className="max-w-[14rem] font-poppins text-base font-semibold leading-tight text-primaryDark sm:max-w-none sm:text-xl">
              Network Issues Monitoring System
            </h1>
          </div>
        </div>

        <nav className="flex items-center gap-2 self-start sm:self-auto">
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
