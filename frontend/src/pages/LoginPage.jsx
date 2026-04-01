import { useEffect, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import ErrorMessage from "../components/ErrorMessage";
import FooterNote from "../components/FooterNote";
import Toast from "../components/Toast";
import { login } from "../services/api";
import { setAuthToken } from "../utils/auth";

function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState({ message: "", type: "success" });

  const from = location.state?.from?.pathname || "/admin";

  useEffect(() => {
    if (!location.state?.sessionExpired && !location.state?.unauthorized) {
      return;
    }

    const message = location.state?.unauthorized
      ? "Not authorized for admin access. Please login with an ICT/Infra account."
      : "Session expired. Please login again.";
    setToast({ message, type: "error" });
    const timerId = window.setTimeout(() => {
      setToast({ message: "", type: "success" });
    }, 2500);

    navigate("/login", {
      replace: true,
      state: { from: location.state?.from }
    });
    return () => window.clearTimeout(timerId);
  }, [location.state, navigate]);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError("");
    try {
      const response = await login({ username, password });
      setAuthToken(response.access_token);
      navigate(from, { replace: true });
    } catch (err) {
      const message = err?.response?.data?.detail || "Login failed. Please check credentials.";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen flex-col bg-bgLight p-4">
      <div className="flex flex-1 items-center justify-center">
        <div className="w-full max-w-md rounded-xl2 border border-cardBorder bg-white p-8 shadow-soft">
          <div className="mb-6 text-center">
            <h1 className="font-poppins text-2xl font-semibold text-primaryDark">Admin Login</h1>
            <p className="mt-1 text-sm text-slate-500">Sign in to manage issue status updates.</p>
          </div>

          {error ? <ErrorMessage message={error} /> : null}

          <form onSubmit={handleSubmit} className="mt-4 space-y-4">
            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">Username</label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 focus:border-primary focus:outline-none"
                required
              />
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 focus:border-primary focus:outline-none"
                required
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-lg bg-primary px-4 py-2.5 font-semibold text-white transition hover:bg-primaryDark disabled:opacity-70"
            >
              {loading ? "Signing in..." : "Login"}
            </button>
          </form>

          <div className="mt-5 text-center text-sm text-slate-500">
            <Link to="/" className="font-medium text-primary hover:text-primaryDark">
              Back to Dashboard
            </Link>
          </div>
        </div>
      </div>
      <FooterNote />
      <Toast message={toast.message} type={toast.type} />
    </div>
  );
}

export default LoginPage;
