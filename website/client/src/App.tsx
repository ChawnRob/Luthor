import { Toaster } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import NotFound from "@/pages/NotFound";
import ActiveLearning from "@/pages/dashboard/ActiveLearning";
import DashboardHome from "@/pages/dashboard/DashboardHome";
import LogsPage from "@/pages/dashboard/Logs";
import Monitoring from "@/pages/dashboard/Monitoring";
import Settings from "@/pages/dashboard/Settings";
import { Route, Switch } from "wouter";
import ErrorBoundary from "./components/ErrorBoundary";
import { ThemeProvider } from "./contexts/ThemeContext";
import Home from "./pages/Home";
import HomeFR from "./pages/HomeFR";


function Router() {
  return (
    <Switch>
      <Route path="/" component={DashboardHome} />
      <Route path="/active-learning" component={ActiveLearning} />
      <Route path="/monitoring" component={Monitoring} />
      <Route path="/logs" component={LogsPage} />
      <Route path="/settings" component={Settings} />
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
      <ThemeProvider
        defaultTheme="light"
        // switchable
      >
        <TooltipProvider>
          <Toaster />
          <Router />
        </TooltipProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
}

export default App;
