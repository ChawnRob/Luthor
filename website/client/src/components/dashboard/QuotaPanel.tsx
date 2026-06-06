import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { useAuth } from "@/contexts/AuthContext";
import { Gauge } from "lucide-react";

function pct(used: number, limit: number): number {
  if (limit <= 0) return 0;
  return Math.min(100, Math.round((used / limit) * 100));
}

export default function QuotaPanel() {
  const { user } = useAuth();
  if (!user) return null;

  const apiUsed = Number(user.usage.api_calls_today ?? 0);
  const apiLimit = Number(user.usage.api_calls_limit ?? 50);
  const complexUsed = Number(user.usage.complex_tasks_month ?? 0);
  const complexLimit = Number(user.usage.complex_tasks_limit ?? 5);
  const storageUsed = Number(user.usage.storage_used_mb ?? 0);
  const storageLimit = Number(user.usage.storage_limit_mb ?? 10);

  return (
    <Card className="border-primary/20 bg-gradient-to-br from-card/90 to-primary/5 backdrop-blur">
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center gap-2 text-base">
          <Gauge className="h-4 w-4 text-primary" />
          Quotas — plan {user.quota_tier.toUpperCase()}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <div className="mb-1 flex justify-between text-xs text-muted-foreground">
            <span>Appels API / jour</span>
            <span>
              {apiUsed} / {apiLimit}
            </span>
          </div>
          <Progress value={pct(apiUsed, apiLimit)} className="h-2" />
        </div>
        <div>
          <div className="mb-1 flex justify-between text-xs text-muted-foreground">
            <span>Tâches complexes / mois</span>
            <span>
              {complexUsed} / {complexLimit}
            </span>
          </div>
          <Progress value={pct(complexUsed, complexLimit)} className="h-2" />
        </div>
        <div>
          <div className="mb-1 flex justify-between text-xs text-muted-foreground">
            <span>Stockage (MB)</span>
            <span>
              {storageUsed} / {storageLimit}
            </span>
          </div>
          <Progress value={pct(storageUsed, storageLimit)} className="h-2" />
        </div>
      </CardContent>
    </Card>
  );
}
