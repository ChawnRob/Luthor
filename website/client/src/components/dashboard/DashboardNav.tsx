import { Button } from "@/components/ui/button";
import { useAuth } from "@/contexts/AuthContext";
import { cn } from "@/lib/utils";
import {
  Activity,
  Brain,
  FileText,
  LayoutDashboard,
  LogOut,
  Settings,
  Tags,
} from "lucide-react";
import { Link, useLocation } from "wouter";

const links = [
  { href: "/", label: "Accueil", icon: LayoutDashboard },
  { href: "/active-learning", label: "Active Learning", icon: Tags },
  { href: "/monitoring", label: "Monitoring", icon: Activity },
  { href: "/logs", label: "Logs", icon: FileText },
  { href: "/settings", label: "Paramètres", icon: Settings },
];

export default function DashboardNav() {
  const [location] = useLocation();
  const { user, signOut } = useAuth();

  return (
    <header className="border-b border-border/60 bg-card/80 backdrop-blur-xl">
      <div className="mx-auto flex max-w-7xl flex-col gap-4 px-4 py-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/15 text-primary">
            <Brain className="h-5 w-5" />
          </div>
          <div>
            <p className="text-lg font-semibold tracking-tight">LUTHOR</p>
            <p className="text-xs text-muted-foreground">Console d&apos;administration</p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-3">
        <nav className="flex flex-wrap gap-1">
          {links.map(({ href, label, icon: Icon }) => {
            const active =
              href === "/"
                ? location === "/" || location === ""
                : location.startsWith(href);

            return (
              <Link
                key={href}
                href={href}
                className={cn(
                  "inline-flex items-center gap-2 rounded-md px-3 py-2 text-sm transition-colors",
                  active
                    ? "bg-primary/15 text-primary"
                    : "text-muted-foreground hover:bg-muted hover:text-foreground",
                )}
              >
                <Icon className="h-4 w-4" />
                {label}
              </Link>
            );
          })}
        </nav>
        {user ? (
          <div className="flex items-center gap-2 text-sm">
            <span className="hidden text-muted-foreground sm:inline">{user.email}</span>
            <Button variant="ghost" size="sm" onClick={signOut}>
              <LogOut className="h-4 w-4" />
            </Button>
          </div>
        ) : (
          <Link href="/login" className="text-sm text-primary hover:underline">
            Connexion
          </Link>
        )}
        </div>
      </div>
    </header>
  );
}
