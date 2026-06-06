import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from luthor.utils.logging import build_run_log, write_run_log


class RunLoggingTests(unittest.TestCase):
    def test_build_run_log_contains_required_fields(self):
        payload = build_run_log(
            run_type="demo",
            hyperparameters={"latent_dim": 4},
            final_loss=0.42,
            success_rate=75.0,
            steps_per_episode=[3, 5, 10],
            timestamp="2026-06-04T12:00:00+00:00",
        )

        self.assertEqual(payload["timestamp"], "2026-06-04T12:00:00+00:00")
        self.assertEqual(payload["run_type"], "demo")
        self.assertEqual(payload["hyperparameters"]["latent_dim"], 4)
        self.assertEqual(payload["final_loss"], 0.42)
        self.assertEqual(payload["success_rate"], 75.0)
        self.assertEqual(payload["steps_per_episode"], [3, 5, 10])

    def test_write_run_log_persists_json(self):
        payload = build_run_log(
            run_type="active_demo",
            hyperparameters={"num_rounds": 2},
            final_loss=1.0,
            success_rate=50.0,
            steps_per_episode=[2, 4],
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            path = write_run_log(os.path.join(tmpdir, "run.json"), payload)
            with open(path, encoding="utf-8") as handle:
                loaded = json.load(handle)

        self.assertEqual(loaded["run_type"], "active_demo")
        self.assertEqual(loaded["success_rate"], 50.0)


if __name__ == "__main__":
    unittest.main()
