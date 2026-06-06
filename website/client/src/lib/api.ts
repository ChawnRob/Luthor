const API_URL = String(import.meta.env.VITE_API_URL ?? "http://localhost:8080").replace(
  /\/$/,
  "",
);
const EXPORT_TOKEN = import.meta.env.VITE_EXPORT_TOKEN || "";

export type HealthResponse = {
  status: string;
  postgres: string;
  chromadb: string;
  model_loaded: boolean;
};

export type PendingLabelItem = {
  sample_id: string;
  observation: number[];
  action: number[];
  metadata: Record<string, unknown>;
  created_at: number;
};

export type MCPToolsResponse = {
  enabled: boolean;
  connectors: Record<string, boolean>;
  tools: Array<{
    name: string;
    type: string;
    connector: string;
    description: string;
    endpoint: string;
  }>;
};

export type InferenceLogItem = {
  id: number;
  endpoint?: string | null;
  request_payload?: Record<string, unknown> | null;
  response_payload?: Record<string, unknown> | null;
  metadata?: Record<string, unknown> | null;
  model_version?: string | null;
  created_at?: string | null;
};

export type InferenceLogsResponse = {
  items: InferenceLogItem[];
  total: number;
  page: number;
  page_size: number;
};

export type ConfigResponse = {
  mcp_enabled: boolean;
  mcp_model: string;
  mcp_llm_provider: string;
  postgres_configured: boolean;
  chroma_host: string;
  chroma_port: number;
  connectors: Record<
    string,
    {
      enabled: boolean;
      url: string;
      api_key_set: boolean;
      token_set: boolean;
      site_id: string;
      model?: string | null;
      device?: string | null;
    }
  >;
  message: string;
};

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const headers = new Headers(init?.headers);
  if (init?.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers,
  });

  if (!response.ok) {
    let detail = response.statusText;
    try {
      const body = await response.json();
      detail = body.detail || detail;
    } catch {
      /* ignore */
    }
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }

  if (response.status === 204) {
    return undefined as T;
  }

  const contentType = response.headers.get("content-type") || "";
  if (!contentType.includes("application/json")) {
    return (await response.text()) as T;
  }

  return response.json() as Promise<T>;
}

export function getApiUrl(): string {
  return API_URL;
}

export function getHealth(): Promise<HealthResponse> {
  return request<HealthResponse>("/health");
}

export function getPendingLabels(): Promise<{ pending: PendingLabelItem[] }> {
  return request<{ pending: PendingLabelItem[] }>("/label/pending");
}

export function submitLabel(sampleId: string, correctOutcome: Record<string, unknown>) {
  return request<{ sample_id: string; stored: boolean }>("/label", {
    method: "POST",
    body: JSON.stringify({ sample_id: sampleId, correct_outcome: correctOutcome }),
  });
}

export function getMcpTools(): Promise<MCPToolsResponse> {
  return request<MCPToolsResponse>("/mcp/tools");
}

export function getMetricsText(): Promise<string> {
  return request<string>("/metrics", {
    headers: { Accept: "text/plain" },
  });
}

export function getLogs(params: {
  page?: number;
  page_size?: number;
  start_date?: string;
  end_date?: string;
  endpoint?: string;
  model_version?: string;
  table?: string;
}): Promise<InferenceLogsResponse> {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== "") {
      search.set(key, String(value));
    }
  });
  const query = search.toString();
  return request<InferenceLogsResponse>(`/logs${query ? `?${query}` : ""}`);
}

export function getConfig(): Promise<ConfigResponse> {
  return request<ConfigResponse>("/config");
}

export async function exportLogs(params: {
  table?: string;
  format?: string;
  start_date?: string;
  end_date?: string;
}): Promise<Blob> {
  const search = new URLSearchParams();
  if (params.table) search.set("table", params.table);
  if (params.format) search.set("format", params.format);
  if (params.start_date) search.set("start_date", params.start_date);
  if (params.end_date) search.set("end_date", params.end_date);

  const response = await fetch(`${API_URL}/export/logs?${search.toString()}`, {
    headers: {
      "X-Export-Token": EXPORT_TOKEN,
    },
  });

  if (!response.ok) {
    let detail = response.statusText;
    try {
      const body = await response.json();
      detail = body.detail || detail;
    } catch {
      /* ignore */
    }
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }

  return response.blob();
}
