import DashboardNav from "@/components/dashboard/DashboardNav";
import type { ReactNode } from "react";

type DashboardLayoutProps = {
  title: string;
  description?: string;
  children: ReactNode;
};

export default function DashboardLayout({
  title,
  description,
  children,
}: DashboardLayoutProps) {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <DashboardNav />
      <main className="mx-auto max-w-7xl px-4 py-8">
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
