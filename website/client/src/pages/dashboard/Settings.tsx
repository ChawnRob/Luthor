import DashboardLayout from "@/components/dashboard/DashboardLayout";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { getAccessToken } from "@/lib/auth-storage";
import { getApiUrl, getConfig, type ConfigResponse } from "@/lib/api";
import { AlertCircle, KeyRound, ShieldCheck } from "lucide-react";
import { useEffect, useState } from "react";
import { toast } from "sonner";

export default function Settings() {
  const [config, setConfig] = useState<ConfigResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [mfaLoading, setMfaLoading] = useState(false);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      setError(null);
      try {
        const data = await getConfig();
        if (!cancelled) {
          setConfig(data);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Impossible de charger la configuration");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    void load();
    return () => {
      cancelled = true;
    };
  }, []);

  async function enableMfa() {
    const token = getAccessToken();
    if (!token) {
      toast.error("Connectez-vous pour activer la MFA");
      return;
    }
    setMfaLoading(true);
    try {
      const response = await fetch(`${getApiUrl()}/auth/mfa/enable`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ access_token: token }),
      });
      if (!response.ok) {
        const body = await response.json();
        throw new Error(body.detail || "Échec MFA");
      }
      const data = (await response.json()) as { totp_uri?: string; secret?: string };
      toast.success("MFA TOTP activée — scannez le QR dans votre application");
      if (data.totp_uri) {
        console.info("TOTP URI:", data.totp_uri);
      }
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Échec MFA");
    } finally {
      setMfaLoading(false);
    }
  }

  return (
    <DashboardLayout
      title="Paramètres"
      description="Configuration de l'API et des connecteurs MCP (lecture seule)."
    >
      <Card className="mb-6 border-primary/30 bg-primary/5">
        <CardContent className="flex items-start gap-3 pt-6">
          <AlertCircle className="mt-0.5 h-5 w-5 shrink-0 text-primary" />
          <div className="text-sm">
            <p className="font-medium">Configuration côté serveur</p>
            <p className="mt-1 text-muted-foreground">
              {config?.message ||
                "Les clés API et URLs MCP se configurent dans le fichier .env ou .env.prod sur le serveur."}
            </p>
            <p className="mt-2 font-mono text-xs text-primary">API : {getApiUrl()}</p>
          </div>
        </CardContent>
      </Card>

      {error ? (
        <div className="mb-6 rounded-lg border border-destructive/40 bg-destructive/10 px-4 py-3 text-sm text-destructive">
          {error}
        </div>
      ) : null}

      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <ShieldCheck className="h-4 w-4" />
            Double authentification (TOTP)
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="mb-3 text-sm text-muted-foreground">
            Activez la MFA via Supabase pour sécuriser votre compte entreprise.
          </p>
          <Button onClick={() => void enableMfa()} disabled={mfaLoading}>
            Activer MFA
          </Button>
        </CardContent>
      </Card>

      {loading ? (
        <Skeleton className="h-64 w-full" />
      ) : config ? (
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Orchestration MCP</CardTitle>
            </CardHeader>
            <CardContent className="grid gap-3 sm:grid-cols-3">
              <div>
                <p className="text-xs text-muted-foreground">MCP activé</p>
                <Badge className="mt-1" variant={config.mcp_enabled ? "default" : "secondary"}>
                  {config.mcp_enabled ? "Oui" : "Non"}
                </Badge>
              </div>
              <div>
                <p className="text-xs text-muted-foreground">Fournisseur LLM</p>
                <p className="mt-1 font-medium">{config.mcp_llm_provider}</p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground">Modèle</p>
                <p className="mt-1 font-medium">{config.mcp_model}</p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Stockage</CardTitle>
            </CardHeader>
            <CardContent className="grid gap-3 sm:grid-cols-3">
              <div>
                <p className="text-xs text-muted-foreground">PostgreSQL</p>
                <Badge className="mt-1" variant={config.postgres_configured ? "default" : "secondary"}>
                  {config.postgres_configured ? "Configuré" : "Non configuré"}
                </Badge>
              </div>
              <div>
                <p className="text-xs text-muted-foreground">ChromaDB host</p>
                <p className="mt-1 font-mono text-sm">{config.chroma_host}</p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground">ChromaDB port</p>
                <p className="mt-1 font-mono text-sm">{config.chroma_port}</p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base">
                <KeyRound className="h-4 w-4" />
                Connecteurs MCP
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {Object.entries(config.connectors).map(([name, connector]) => (
                <div
                  key={name}
                  className="flex flex-wrap items-center justify-between gap-2 rounded-md border px-3 py-2"
                >
                  <div>
                    <p className="font-medium capitalize">{name}</p>
                    <p className="text-xs text-muted-foreground">
                      {connector.url || "URL non définie"}
                    </p>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    <Badge variant={connector.enabled ? "default" : "secondary"}>
                      {connector.enabled ? "Activé" : "Désactivé"}
                    </Badge>
                    {connector.api_key_set ? (
                      <Badge variant="outline">API key ✓</Badge>
                    ) : null}
                    {connector.token_set ? (
                      <Badge variant="outline">Token ✓</Badge>
                    ) : null}
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>
      ) : null}
    </DashboardLayout>
  );
}
