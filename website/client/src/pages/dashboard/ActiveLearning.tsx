import DashboardLayout from "@/components/dashboard/DashboardLayout";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { getApiUrl, getPendingLabels, submitLabel, type PendingLabelItem } from "@/lib/api";
import { Check, ExternalLink, RefreshCw, X } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { toast } from "sonner";

function buildLabelPayload(sample: PendingLabelItem, isCorrect: boolean) {
  const suggested =
    (sample.metadata?.suggested_next_observation as number[] | undefined) ||
    sample.observation;
  const nextObservation = isCorrect
    ? suggested
    : suggested.map((value, index) => value + (index % 2 === 0 ? 0.1 : -0.1));

  return {
    next_observation: nextObservation,
    human_verdict: isCorrect ? "correct" : "incorrect",
  };
}

export default function ActiveLearning() {
  const [pending, setPending] = useState<PendingLabelItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [submittingId, setSubmittingId] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      const data = await getPendingLabels();
      setPending(data.pending);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Échec du chargement");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
    const interval = window.setInterval(() => void refresh(), 10_000);
    return () => window.clearInterval(interval);
  }, [refresh]);

  async function handleLabel(sample: PendingLabelItem, isCorrect: boolean) {
    setSubmittingId(sample.sample_id);
    try {
      await submitLabel(sample.sample_id, buildLabelPayload(sample, isCorrect));
      toast.success(isCorrect ? "Label « Correct » enregistré" : "Label « Incorrect » enregistré");
      await refresh();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Échec de la soumission");
    } finally {
      setSubmittingId(null);
    }
  }

  return (
    <DashboardLayout
      title="Active Learning"
      description="Validez les échantillons en attente pour l'apprentissage actif human-in-the-loop."
    >
      <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
        <Badge variant="secondary" className="text-sm">
          {pending.length} label{pending.length !== 1 ? "s" : ""} restant
          {pending.length !== 1 ? "s" : ""}
        </Badge>
        <div className="flex flex-wrap gap-2">
          <Button variant="outline" size="sm" asChild>
            <a href={`${getApiUrl()}/label-ui`} target="_blank" rel="noreferrer">
              <ExternalLink className="mr-2 h-4 w-4" />
              Interface legacy
            </a>
          </Button>
          <Button variant="outline" size="sm" onClick={() => void refresh()}>
            <RefreshCw className="mr-2 h-4 w-4" />
            Rafraîchir
          </Button>
        </div>
      </div>

      {loading ? (
        <div className="space-y-4">
          <Skeleton className="h-48 w-full" />
          <Skeleton className="h-48 w-full" />
        </div>
      ) : pending.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center text-muted-foreground">
            Aucun échantillon en attente. Lancez une session d&apos;active learning via l&apos;API.
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {pending.map((sample) => (
            <Card key={sample.sample_id}>
              <CardHeader>
                <CardTitle className="text-base">
                  Échantillon {sample.sample_id}
                  {sample.metadata?.environment ? (
                    <span className="ml-2 text-sm font-normal text-muted-foreground">
                      ({String(sample.metadata.environment)})
                    </span>
                  ) : null}
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <p className="mb-1 text-sm font-medium text-muted-foreground">Observation</p>
                  <pre className="overflow-x-auto rounded-md border bg-muted/30 p-3 text-xs">
                    {JSON.stringify(sample.observation, null, 2)}
                  </pre>
                </div>
                <div>
                  <p className="mb-1 text-sm font-medium text-muted-foreground">
                    Action proposée
                  </p>
                  <pre className="overflow-x-auto rounded-md border bg-muted/30 p-3 text-xs">
                    {JSON.stringify(sample.action, null, 2)}
                  </pre>
                </div>
                <div className="flex flex-wrap gap-2">
                  <Button
                    onClick={() => void handleLabel(sample, true)}
                    disabled={submittingId === sample.sample_id}
                    className="bg-emerald-600 hover:bg-emerald-700"
                  >
                    <Check className="mr-2 h-4 w-4" />
                    Correct
                  </Button>
                  <Button
                    variant="destructive"
                    onClick={() => void handleLabel(sample, false)}
                    disabled={submittingId === sample.sample_id}
                  >
                    <X className="mr-2 h-4 w-4" />
                    Incorrect
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </DashboardLayout>
  );
}
