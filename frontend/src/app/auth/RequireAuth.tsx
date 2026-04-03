import { Navigate } from "react-router";
import { useAuth } from "./AuthContext";

interface RequireAuthProps {
  children: React.ReactNode;
}

/**
 * Route guard component that ensures user is authenticated.
 * If not authenticated and not initializing, redirects to /login.
 * While initializing, renders null to prevent flash of login page.
 */
export function RequireAuth({ children }: RequireAuthProps) {
  const { isAuthenticated, isInitializing } = useAuth();

  // While bootstrapping auth state from localStorage/API, render nothing to avoid flash.
  if (isInitializing) {
    return null;
  }

  // If not authenticated, redirect to login.
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // User is authenticated; render the protected content.
  return <>{children}</>;
}
