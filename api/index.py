from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
import numpy as np

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load telemetry data
with open("q-vercel-latency.json", "r") as f:
    telemetry = json.load(f)


@app.post("/")
def analyze(data: dict):

    regions = data.get("regions", [])
    threshold = data.get("threshold_ms", 180)

    result = {}

    for region in regions:

        rows = [
            r for r in telemetry
            if r["region"] == region
        ]

        if not rows:
            result[region] = {
                "avg_latency": 0,
                "p95_latency": 0,
                "avg_uptime": 0,
                "breaches": 0
            }
            continue

        latencies = [r["latency_ms"] for r in rows]
        uptimes = [r["uptime_pct"] for r in rows]

        result[region] = {
            "avg_latency": round(float(np.mean(latencies)), 2),
            "p95_latency": round(float(np.percentile(latencies, 95)), 2),
            "avg_uptime": round(float(np.mean(uptimes)), 2),
            "breaches": sum(
                1 for x in latencies
                if x > threshold
            )
        }

    return result


@app.get("/")
def root():
    return {"message": "Latency Analytics API"}
