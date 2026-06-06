import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getAccessToken } from "@/lib/auth-storage";
import { getApiUrl } from "@/lib/api";
import { RefreshCw, Wifi } from "lucide-react";
import { useCallback, useEffect, useState } from "react";

type ToolSyncItem = {
  connector: string;
  enabled: boolean;
  status: string;
  last_sync_at: string | null;
  tools_count: number;
};

export default function ToolSyncPanel() {
  const [items, setItems] = useState<ToolSyncItem[]>([]);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const headers: HeadersInit = {};
      const token = getAccessToken();
      if (token) headers.Authorization = `Bearer ${token}`;

      const response = await fetch(`${getApiUrl()}/sync/tools`, { headers });
      if (!response.ok) return;
      const data = (await response.json()) as { connectors: ToolSyncItem[] };
      setItems(data.connectors);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
    const interval = window.setInterval(() => void load(), 20_000);
    return () => window.clearInterval(interval);
  }, [load]);

  return (
    <Card className="border-primary/30 bg-card/60 backdrop-blur-xl shadow-[0_0_40px_rgba(0,217,255,0.08)]">
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="flex items-center gap-2 text-base">
          <Wifi className="h-4 w-4 text-primary" />
          Synchronisation des outils externes
        </CardTitle>
        <Button variant="ghost" size="sm" onClick={() => void load()} disabled={loading}>
          <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
        </Button>
      </CardHeader>
      <CardContent className="grid gap-2 sm:grid-cols-2">
        {items.length === 0 ? (
          <p className="text-sm text-muted-foreground">Aucun connecteur configuré.</p>
        ) : (
          items.map((item) => (
            <div
              key={item.connector}
              className="rounded-lg border border-border/60 bg-background/40 px-3 py-2"
            >
              <div className="flex items-center justify-between gap-2">
                <span className="font-medium capitalize">{item.connector}</span>
                <Badge variant={item.status === "online" ? "default" : "secondary"}>
                  {item.status}
                </Badge>
              </div>
              <p className="mt-1 text-xs text-muted-foreground">
                {item.tools_count} outil{item.tools_count > 1 ? "s" : ""}
                {item.last_sync_at
                  ? ` — sync ${new Date(item.last_sync_at).toLocaleTimeString("fr-FR")}`
                  : ""}
              </p>
            </div>
          ))
        )}
      </CardContent>
    </Card>
  );
}
