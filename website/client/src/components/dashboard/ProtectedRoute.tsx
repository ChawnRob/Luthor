import { useAuth } from "@/contexts/AuthContext";
import { Redirect, Route, type RouteProps } from "wouter";

const AUTH_REQUIRED =
  String(import.meta.env.VITE_AUTH_REQUIRED ?? "false").toLowerCase() === "true";

type ProtectedRouteProps = RouteProps;

export default function ProtectedRoute({ component: Component, ...rest }: ProtectedRouteProps) {
  const { token, loading } = useAuth();

  if (!AUTH_REQUIRED) {
    return <Route {...rest} component={Component} />;
  }

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background text-muted-foreground">
        Chargement…
      </div>
    );
  }

  if (!token) {
    return <Redirect to="/login" />;
  }

  return <Route {...rest} component={Component} />;
}
