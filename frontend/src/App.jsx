import { useEffect } from "react";
import { Navigate, Route, Routes, useLocation, useNavigate } from "react-router-dom";
import ProtectedRoute from "./components/ProtectedRoute";
import AdminPage from "./pages/AdminPage";
import DashboardPage from "./pages/DashboardPage";
import LoginPage from "./pages/LoginPage";
import { AUTH_LOGOUT_EVENT } from "./utils/auth";

function App() {
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const handleLogout = (event) => {
      if (location.pathname === "/login") {
        return;
      }
      const reason = event?.detail?.reason;
      navigate("/login", {
        replace: true,
        state: {
          from: location,
          sessionExpired: reason === "expired",
          unauthorized: reason === "unauthorized"
        }
      });
    };

    window.addEventListener(AUTH_LOGOUT_EVENT, handleLogout);
    return () => window.removeEventListener(AUTH_LOGOUT_EVENT, handleLogout);
  }, [location, navigate]);

  return (
    <Routes>
      <Route path="/" element={<DashboardPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/admin"
        element={
          <ProtectedRoute requireCoordinatorRole>
            <AdminPage />
          </ProtectedRoute>
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;
