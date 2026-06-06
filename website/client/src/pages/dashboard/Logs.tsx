import DashboardLayout from "@/components/dashboard/DashboardLayout";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { exportLogs, getLogs, type InferenceLogItem } from "@/lib/api";
import { ChevronLeft, ChevronRight, Download } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { toast } from "sonner";

const TABLES = ["inference_logs", "active_learning_runs", "human_labels"];

export default function LogsPage() {
  const [items, setItems] = useState<InferenceLogItem[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(20);
  const [loading, setLoading] = useState(true);
  const [exporting, setExporting] = useState(false);

  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [endpoint, setEndpoint] = useState("");
  const [modelVersion, setModelVersion] = useState("");
  const [table, setTable] = useState("inference_logs");

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await getLogs({
        page,
        page_size: pageSize,
        start_date: startDate || undefined,
        end_date: endDate || undefined,
        endpoint: endpoint || undefined,
        model_version: modelVersion || undefined,
        table,
      });
      setItems(data.items);
      setTotal(data.total);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Échec du chargement des logs");
    } finally {
      setLoading(false);
    }
  }, [page, pageSize, startDate, endDate, endpoint, modelVersion, table]);

  useEffect(() => {
    void load();
  }, [load]);

  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  async function handleExport() {
    setExporting(true);
    try {
      const blob = await exportLogs({
        table,
        format: "csv",
        start_date: startDate || undefined,
        end_date: endDate || undefined,
      });
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = `${table}_export.csv`;
      anchor.click();
      URL.revokeObjectURL(url);
      toast.success("Export téléchargé");
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Échec de l'export");
    } finally {
      setExporting(false);
    }
  }

  return (
    <DashboardLayout
      title="Logs d'inférence"
      description="Historique des appels API enregistrés dans PostgreSQL."
    >
      <Card className="mb-6">
        <CardContent className="grid gap-4 pt-6 md:grid-cols-2 lg:grid-cols-5">
          <div className="space-y-2">
            <Label htmlFor="start-date">Date début</Label>
            <Input
              id="start-date"
              type="date"
              value={startDate}
              onChange={(e) => {
                setPage(1);
                setStartDate(e.target.value);
              }}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="end-date">Date fin</Label>
            <Input
              id="end-date"
              type="date"
              value={endDate}
              onChange={(e) => {
                setPage(1);
                setEndDate(e.target.value);
              }}
            />
          </div>
          <div className="space-y-2">
            <Label>Table</Label>
            <Select
              value={table}
              onValueChange={(value) => {
                setPage(1);
                setTable(value);
              }}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {TABLES.map((name) => (
                  <SelectItem key={name} value={name}>
                    {name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label htmlFor="endpoint">Endpoint</Label>
            <Input
              id="endpoint"
              placeholder="/predict"
              value={endpoint}
              onChange={(e) => {
                setPage(1);
                setEndpoint(e.target.value);
              }}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="model">Modèle</Label>
            <Input
              id="model"
              placeholder="default"
              value={modelVersion}
              onChange={(e) => {
                setPage(1);
                setModelVersion(e.target.value);
              }}
            />
          </div>
        </CardContent>
      </Card>

      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <p className="text-sm text-muted-foreground">
          {total} entrée{total > 1 ? "s" : ""} — page {page} / {totalPages}
        </p>
        <Button onClick={() => void handleExport()} disabled={exporting}>
          <Download className="mr-2 h-4 w-4" />
          Exporter CSV
        </Button>
      </div>

      <Card>
        <CardContent className="p-0">
          {loading ? (
            <div className="p-6">
              <Skeleton className="h-64 w-full" />
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>ID</TableHead>
                  <TableHead>Date</TableHead>
                  <TableHead>Endpoint</TableHead>
                  <TableHead>Modèle</TableHead>
                  <TableHead>Requête</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {items.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={5} className="py-8 text-center text-muted-foreground">
                      Aucun log trouvé.
                    </TableCell>
                  </TableRow>
                ) : (
                  items.map((row) => (
                    <TableRow key={row.id}>
                      <TableCell>{row.id}</TableCell>
                      <TableCell className="whitespace-nowrap text-xs">
                        {row.created_at
                          ? new Date(row.created_at).toLocaleString("fr-FR")
                          : "—"}
                      </TableCell>
                      <TableCell className="font-mono text-xs">{row.endpoint || "—"}</TableCell>
                      <TableCell>{row.model_version || "—"}</TableCell>
                      <TableCell className="max-w-xs truncate font-mono text-xs">
                        {JSON.stringify(row.request_payload || {})}
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      <div className="mt-4 flex justify-end gap-2">
        <Button
          variant="outline"
          size="sm"
          disabled={page <= 1}
          onClick={() => setPage((p) => Math.max(1, p - 1))}
        >
          <ChevronLeft className="h-4 w-4" />
        </Button>
        <Button
          variant="outline"
          size="sm"
          disabled={page >= totalPages}
          onClick={() => setPage((p) => p + 1)}
        >
          <ChevronRight className="h-4 w-4" />
        </Button>
      </div>
    </DashboardLayout>
  );
}
