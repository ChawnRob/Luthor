"""
Light load profile for the LUTHOR engine API.

Run manually (API must be up on :8080):
  pip install locust
  locust -f tests/locustfile.py --headless -u 5 -r 2 -t 30s --host http://localhost:8080
"""

from locust import HttpUser, between, task


class LuthorEngineUser(HttpUser):
    wait_time = between(0.5, 1.5)

    @task(3)
    def health(self):
        self.client.get("/health")

    @task(2)
    def embed(self):
        self.client.post("/embed", json={"observation": [0.1, 0.2, 0.3, 0.4]})

    @task(2)
    def predict(self):
        self.client.post(
            "/predict",
            json={"observation": [0.1, 0.2], "action": [0.3, 0.4], "mc_samples": 2},
        )

    @task(1)
    def metrics(self):
        self.client.get("/metrics")
