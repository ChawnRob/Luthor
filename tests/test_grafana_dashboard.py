import json
import unittest
from pathlib import Path


class GrafanaDashboardTests(unittest.TestCase):
    def test_luthor_dashboard_json_is_valid(self):
        path = (
            Path(__file__).resolve().parents[1]
            / "docker"
            / "grafana"
            / "provisioning"
            / "dashboards"
            / "luthor.json"
        )
        self.assertTrue(path.exists(), f"Missing dashboard: {path}")
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertIn("panels", data)
        self.assertGreaterEqual(len(data["panels"]), 5)

    def test_prometheus_datasource_configured(self):
        path = (
            Path(__file__).resolve().parents[1]
            / "docker"
            / "grafana"
            / "provisioning"
            / "datasources"
            / "prometheus.yml"
        )
        self.assertTrue(path.exists())
        content = path.read_text(encoding="utf-8")
        self.assertIn("prometheus", content.lower())


if __name__ == "__main__":
    unittest.main()
