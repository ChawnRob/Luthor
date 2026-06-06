import ProtectedRoute from "@/components/dashboard/ProtectedRoute";
import { Toaster } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import Login from "@/pages/auth/Login";
import Signup from "@/pages/auth/Signup";
import NotFound from "@/pages/NotFound";
import ActiveLearning from "@/pages/dashboard/ActiveLearning";
import DashboardHome from "@/pages/dashboard/DashboardHome";
import LogsPage from "@/pages/dashboard/Logs";
import Monitoring from "@/pages/dashboard/Monitoring";
import Settings from "@/pages/dashboard/Settings";
import { Route, Switch } from "wouter";
import ErrorBoundary from "./components/ErrorBoundary";
import { AuthProvider } from "./contexts/AuthContext";
import { ThemeProvider } from "./contexts/ThemeContext";
import Home from "./pages/Home";
import HomeFR from "./pages/HomeFR";


function Router() {
  return (
    <Switch>
      <ProtectedRoute path="/" component={DashboardHome} />
      <ProtectedRoute path="/active-learning" component={ActiveLearning} />
      <ProtectedRoute path="/monitoring" component={Monitoring} />
      <ProtectedRoute path="/logs" component={LogsPage} />
      <ProtectedRoute path="/settings" component={Settings} />
      <Route path="/login" component={Login} />
      <Route path="/signup" component={Signup} />
      <Route path="/landing" component={Home} />
      <Route path="/en" component={Home} />
      <Route path="/fr" component={HomeFR} />
      <Route path="/404" component={NotFound} />
      <Route component={NotFound} />
    </Switch>
  );
}

// NOTE: About Theme
// - First choose a default theme according to your design style (dark or light bg), than change color palette in index.css
//   to keep consistent foreground/background color across components
// - If you want to make theme switchable, pass `switchable` ThemeProvider and use `useTheme` hook

function App() {
  return (
    <ErrorBoundary>
      <ThemeProvider defaultTheme="dark">
        <AuthProvider>
          <TooltipProvider>
            <Toaster />
            <Router />
          </TooltipProvider>
        </AuthProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
}

export default App;
