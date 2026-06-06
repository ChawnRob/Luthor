import DashboardNav from "@/components/dashboard/DashboardNav";
import type { ReactNode } from "react";

type DashboardLayoutProps = {
  title: string;
  description?: string;
  futuristic?: boolean;
  children: ReactNode;
};

export default function DashboardLayout({
  title,
  description,
  futuristic = false,
  children,
}: DashboardLayoutProps) {
  return (
    <div className="relative min-h-screen bg-background text-foreground">
      {futuristic ? (
        <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_top,rgba(0,217,255,0.12),transparent_50%),radial-gradient(ellipse_at_bottom_right,rgba(99,102,241,0.1),transparent_45%)]" />
      ) : null}
      <DashboardNav />
      <main className="relative z-10 mx-auto max-w-7xl px-4 py-8">
        <div className="mb-8">
          <h1 className="text-2xl font-semibold tracking-tight">{title}</h1>
          {description ? (
            <p className="mt-1 text-sm text-muted-foreground">{description}</p>
          ) : null}
        </div>
        {children}
      </main>
    </div>
  );
}
