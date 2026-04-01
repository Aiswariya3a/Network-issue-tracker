import { Navigate, useLocation } from "react-router-dom";
import { clearAuthToken, getAuthFailureReason, isAuthenticated } from "../utils/auth";

function ProtectedRoute({ children, requireCoordinatorRole = false }) {
  const location = useLocation();
  const reason = getAuthFailureReason(requireCoordinatorRole);

  if (!isAuthenticated() || reason === "unauthorized") {
    clearAuthToken();
    return (
      <Navigate
        to="/login"
        replace
        state={{
          from: location,
          sessionExpired: reason === "expired",
          unauthorized: reason === "unauthorized"
        }}
      />
    );
  }
  return children;
}

export default ProtectedRoute;
