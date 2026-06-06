export type MetricSample = {
  name: string;
  labels: Record<string, string>;
  value: number;
};

export function parsePrometheusMetrics(text: string): MetricSample[] {
  const samples: MetricSample[] = [];
  const lines = text.split("\n");

  for (const line of lines) {
    if (!line || line.startsWith("#")) {
      continue;
    }

    const spaceIndex = line.lastIndexOf(" ");
    if (spaceIndex <= 0) {
      continue;
    }

    const value = Number(line.slice(spaceIndex + 1));
    if (Number.isNaN(value)) {
      continue;
    }

    const metricPart = line.slice(0, spaceIndex);
    const braceStart = metricPart.indexOf("{");
    if (braceStart === -1) {
      samples.push({ name: metricPart, labels: {}, value });
      continue;
    }

    const name = metricPart.slice(0, braceStart);
    const labelsRaw = metricPart.slice(braceStart + 1, -1);
    const labels: Record<string, string> = {};
    const labelRegex = /([a-zA-Z_][a-zA-Z0-9_]*)="([^"]*)"/g;
    let match: RegExpExecArray | null;
    while ((match = labelRegex.exec(labelsRaw)) !== null) {
      labels[match[1]] = match[2];
    }

    samples.push({ name, labels, value });
  }

  return samples;
}

export function aggregateCounterByLabel(
  samples: MetricSample[],
  metricName: string,
  labelKey: string,
): Array<{ label: string; value: number }> {
  const totals = new Map<string, number>();

  for (const sample of samples) {
    if (sample.name !== metricName) {
      continue;
    }
    const label = sample.labels[labelKey] || "unknown";
    totals.set(label, (totals.get(label) || 0) + sample.value);
  }

  return Array.from(totals.entries()).map(([label, value]) => ({ label, value }));
}

export function sumMetric(samples: MetricSample[], metricName: string): number {
  return samples
    .filter((sample) => sample.name === metricName)
    .reduce((sum, sample) => sum + sample.value, 0);
}
