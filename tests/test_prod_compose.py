import os
import sys
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
COMPOSE_PATH = ROOT / "docker-compose.prod.yml"

REQUIRED_SERVICES = [
    "traefik",
    "luthor-ui",
    "api",
    "postgres",
    "chromadb",
    "prometheus",
    "grafana",
    "n8n",
    "clickhouse",
    "plausible",
    "calcom",
    "fooocus",
    "watchtower",
]

REQUIRED_NETWORKS = ["luthor_public", "luthor_internal"]

REQUIRED_VOLUMES = [
    "postgres_data",
    "chroma_data",
    "prometheus_data",
    "grafana_data",
    "n8n_data",
    "clickhouse_data",
    "fooocus_outputs",
    "demo_outputs",
    "ytdlp_downloads",
    "traefik_letsencrypt",
]


class ProdComposeTests(unittest.TestCase):
    def test_compose_file_exists(self):
        self.assertTrue(COMPOSE_PATH.exists(), f"Missing {COMPOSE_PATH}")

    def test_compose_yaml_is_valid(self):
        with COMPOSE_PATH.open(encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
        self.assertIsInstance(data, dict)
        self.assertIn("services", data)

    def test_all_required_services_defined(self):
        with COMPOSE_PATH.open(encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
        services = set(data.get("services", {}).keys())
        for name in REQUIRED_SERVICES:
            with self.subTest(service=name):
                self.assertIn(name, services)

    def test_api_uses_production_dockerfile(self):
        with COMPOSE_PATH.open(encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
        api = data["services"]["api"]
        self.assertEqual(api["build"]["dockerfile"], "Dockerfile.prod")

    def test_ui_uses_ui_dockerfile(self):
        with COMPOSE_PATH.open(encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
        ui = data["services"]["luthor-ui"]
        self.assertEqual(ui["build"]["dockerfile"], "Dockerfile.ui")

    def test_networks_and_volumes_present(self):
        with COMPOSE_PATH.open(encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
        networks = set(data.get("networks", {}).keys())
        volumes = set(data.get("volumes", {}).keys())
        for name in REQUIRED_NETWORKS:
            with self.subTest(network=name):
                self.assertIn(name, networks)
        for name in REQUIRED_VOLUMES:
            with self.subTest(volume=name):
                self.assertIn(name, volumes)

    def test_traefik_exposes_http_and_https(self):
        with COMPOSE_PATH.open(encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
        ports = data["services"]["traefik"].get("ports", [])
        joined = " ".join(str(port) for port in ports)
        self.assertIn("80:80", joined)
        self.assertIn("443:443", joined)

    def test_deploy_script_exists(self):
        script = ROOT / "scripts" / "deploy_prod.sh"
        self.assertTrue(script.exists())
        self.assertTrue(os.access(script, os.X_OK))


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT / "src"))
    unittest.main()
