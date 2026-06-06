import DashboardLayout from "@/components/dashboard/DashboardLayout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { getMetricsText } from "@/lib/api";
import {
  aggregateCounterByLabel,
  parsePrometheusMetrics,
  sumMetric,
} from "@/lib/prometheus";
import { useEffect, useMemo, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

const GRAFANA_URL = import.meta.env.VITE_GRAFANA_URL || "";

export default function Monitoring() {
  const [metricsText, setMetricsText] = useState("");
  const [loading, setLoading] = useState(!GRAFANA_URL);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (GRAFANA_URL) {
      return;
    }

    let cancelled = false;

    async function load() {
      setLoading(true);
      setError(null);
      try {
        const text = await getMetricsText();
        if (!cancelled) {
          setMetricsText(text);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Impossible de charger /metrics");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    void load();
    const interval = window.setInterval(() => void load(), 15_000);
    return () => {
      cancelled = true;
      window.clearInterval(interval);
    };
  }, []);

  const chartData = useMemo(() => {
    const samples = parsePrometheusMetrics(metricsText);
    return {
      requestsByEndpoint: aggregateCounterByLabel(
        samples,
        "http_requests_total",
        "endpoint",
      ).slice(0, 8),
      modelVersions: aggregateCounterByLabel(
        samples,
        "model_version_requests_total",
        "model_version",
      ),
      activeLearningRounds: sumMetric(samples, "active_learning_rounds_total"),
      httpRequests: sumMetric(samples, "http_requests_total"),
    };
  }, [metricsText]);

  if (GRAFANA_URL) {
    return (
      <DashboardLayout
        title="Monitoring"
        description="Tableau de bord Grafana pour les métriques Prometheus."
      >
        <Card className="overflow-hidden">
          <CardContent className="p-0">
            <iframe
              title="Grafana"
              src={GRAFANA_URL}
              className="h-[70vh] w-full border-0"
              allowFullScreen
            />
          </CardContent>
        </Card>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout
      title="Monitoring"
      description="Métriques Prometheus exposées par l'API LUTHOR (fallback sans Grafana)."
    >
      {error ? (
        <div className="mb-6 rounded-lg border border-destructive/40 bg-destructive/10 px-4 py-3 text-sm text-destructive">
          {error}
        </div>
      ) : null}

      <div className="mb-6 grid gap-4 sm:grid-cols-2">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-muted-foreground">
              Requêtes HTTP totales
            </CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <Skeleton className="h-8 w-20" />
            ) : (
              <p className="text-3xl font-semibold">{chartData.httpRequests}</p>
            )}
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-muted-foreground">
              Rounds active learning
            </CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <Skeleton className="h-8 w-20" />
            ) : (
              <p className="text-3xl font-semibold">{chartData.activeLearningRounds}</p>
            )}
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Requêtes par endpoint</CardTitle>
          </CardHeader>
          <CardContent className="h-72">
            {loading ? (
              <Skeleton className="h-full w-full" />
            ) : chartData.requestsByEndpoint.length === 0 ? (
              <p className="text-sm text-muted-foreground">Aucune métrique disponible.</p>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData.requestsByEndpoint}>
                  <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
                  <XAxis dataKey="label" tick={{ fontSize: 11 }} />
                  <YAxis tick={{ fontSize: 11 }} />
                  <Tooltip />
                  <Bar dataKey="value" fill="var(--color-primary)" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Requêtes par version de modèle</CardTitle>
          </CardHeader>
          <CardContent className="h-72">
            {loading ? (
              <Skeleton className="h-full w-full" />
            ) : chartData.modelVersions.length === 0 ? (
              <p className="text-sm text-muted-foreground">Aucune métrique disponible.</p>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData.modelVersions}>
                  <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
                  <XAxis dataKey="label" tick={{ fontSize: 11 }} />
                  <YAxis tick={{ fontSize: 11 }} />
                  <Tooltip />
                  <Bar dataKey="value" fill="var(--color-chart-2)" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
