import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

export const ProtectedRoute = () => {
  const { user, initializing } = useAuth();
  const location = useLocation();

  if (initializing) {
    return <div className="page-state">Відновлюємо сесію...</div>;
  }

  if (!user) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }

  return <Outlet />;
};
