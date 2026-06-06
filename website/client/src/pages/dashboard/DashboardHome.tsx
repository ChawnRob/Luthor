import DashboardLayout from "@/components/dashboard/DashboardLayout";
import QuotaPanel from "@/components/dashboard/QuotaPanel";
import ToolSyncPanel from "@/components/dashboard/ToolSyncPanel";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import {
  getApiUrl,
  getHealth,
  getLogs,
  getMcpTools,
  type HealthResponse,
  type InferenceLogItem,
  type MCPToolsResponse,
} from "@/lib/api";
import { CheckCircle2, Plug, Server, XCircle } from "lucide-react";
import { useEffect, useState } from "react";

function StatusBadge({ ok }: { ok: boolean }) {
  return ok ? (
    <Badge className="bg-emerald-500/15 text-emerald-400 hover:bg-emerald-500/20">
      <CheckCircle2 className="mr-1 h-3 w-3" />
      OK
    </Badge>
  ) : (
    <Badge variant="destructive">
      <XCircle className="mr-1 h-3 w-3" />
      Erreur
    </Badge>
  );
}

export default function DashboardHome() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [mcp, setMcp] = useState<MCPToolsResponse | null>(null);
  const [lastLog, setLastLog] = useState<InferenceLogItem | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      setError(null);
      try {
        const [healthData, mcpData, logsData] = await Promise.all([
          getHealth(),
          getMcpTools(),
          getLogs({ page: 1, page_size: 1 }),
        ]);
        if (!cancelled) {
          setHealth(healthData);
          setMcp(mcpData);
          setLastLog(logsData.items[0] || null);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Impossible de charger l'état de l'agent");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    void load();
    const interval = window.setInterval(() => void load(), 30_000);
    return () => {
      cancelled = true;
      window.clearInterval(interval);
    };
  }, []);

  const activeConnectors = mcp
    ? Object.entries(mcp.connectors).filter(([, enabled]) => enabled).length
    : 0;

  return (
    <DashboardLayout
      title="Tableau de bord"
      description="Vue d'ensemble de l'état de l'agent LUTHOR et des services connectés."
      futuristic
    >
      {error ? (
        <div className="mb-6 rounded-lg border border-destructive/40 bg-destructive/10 px-4 py-3 text-sm text-destructive">
          {error}
        </div>
      ) : null}

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Modèle JEPA
            </CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <Skeleton className="h-8 w-24" />
            ) : (
              <StatusBadge ok={Boolean(health?.model_loaded)} />
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Connecteurs MCP
            </CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <Skeleton className="h-8 w-16" />
            ) : (
              <p className="text-2xl font-semibold">
                {activeConnectors}
                <span className="ml-1 text-sm font-normal text-muted-foreground">
                  actifs
                </span>
              </p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Statut global
            </CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <Skeleton className="h-8 w-24" />
            ) : (
              <StatusBadge ok={health?.status === "ok"} />
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              API
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="truncate text-sm font-mono text-primary">{getApiUrl()}</p>
          </CardContent>
        </Card>
      </div>

      <div className="mt-6 grid gap-4 xl:grid-cols-3">
        <QuotaPanel />
        <div className="xl:col-span-2">
          <ToolSyncPanel />
        </div>
      </div>

      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <Card className="border-primary/15 bg-card/70 backdrop-blur">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <Server className="h-4 w-4 text-primary" />
              Santé des services
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {loading ? (
              <>
                <Skeleton className="h-10 w-full" />
                <Skeleton className="h-10 w-full" />
              </>
            ) : (
              <>
                <div className="flex items-center justify-between rounded-md border px-3 py-2">
                  <span>PostgreSQL</span>
                  <StatusBadge ok={health?.postgres === "ok"} />
                </div>
                <div className="flex items-center justify-between rounded-md border px-3 py-2">
                  <span>ChromaDB</span>
                  <StatusBadge ok={health?.chromadb === "ok"} />
                </div>
                {health && health.postgres !== "ok" ? (
                  <p className="text-xs text-muted-foreground">{health.postgres}</p>
                ) : null}
                {health && health.chromadb !== "ok" ? (
                  <p className="text-xs text-muted-foreground">{health.chromadb}</p>
                ) : null}
              </>
            )}
          </CardContent>
        </Card>

        <Card className="border-primary/15 bg-card/70 backdrop-blur">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <Plug className="h-4 w-4 text-primary" />
              Connecteurs MCP
            </CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <Skeleton className="h-32 w-full" />
            ) : mcp ? (
              <div className="flex flex-wrap gap-2">
                {Object.entries(mcp.connectors).map(([name, enabled]) => (
                  <Badge
                    key={name}
                    variant={enabled ? "default" : "secondary"}
                    className={enabled ? "bg-primary/20 text-primary" : ""}
                  >
                    {name}
                  </Badge>
                ))}
              </div>
            ) : null}
          </CardContent>
        </Card>
      </div>

      <Card className="mt-6">
        <CardHeader>
          <CardTitle className="text-base">Dernière inférence</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <Skeleton className="h-24 w-full" />
          ) : lastLog ? (
            <div className="space-y-2 text-sm">
              <p>
                <span className="text-muted-foreground">Endpoint :</span>{" "}
                <span className="font-mono">{lastLog.endpoint}</span>
              </p>
              <p>
                <span className="text-muted-foreground">Modèle :</span>{" "}
                {lastLog.model_version || "default"}
              </p>
              <p>
                <span className="text-muted-foreground">Date :</span>{" "}
                {lastLog.created_at
                  ? new Date(lastLog.created_at).toLocaleString("fr-FR")
                  : "—"}
              </p>
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">Aucune inférence enregistrée.</p>
          )}
        </CardContent>
      </Card>
    </DashboardLayout>
  );
}
