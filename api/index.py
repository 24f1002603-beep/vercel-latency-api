from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import json
import numpy as np

app = FastAPI()

# CORS fix
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load data (make sure the JSON file is in the root)
try:
    with open("q-vercel-latency.json", "r") as f:
        telemetry_data = json.load(f)
except Exception as e:
    telemetry_data = []
    print("Warning: Could not load data file", e)

@app.post("/analytics")
async def analytics(request: Request):
    try:
        body = await request.json()
        regions = body.get("regions", [])
        threshold_ms = body.get("threshold_ms", 180)

        results = {}

        for region in regions:
            region_data = [r for r in telemetry_data if r.get("region") == region]
            
            if not region_data:
                results[region] = {"avg_latency": 0, "p95_latency": 0, "avg_uptime": 0, "breaches": 0}
                continue

            latencies = [r.get("latency_ms", 0) for r in region_data]
            uptimes = [r.get("uptime", 0) for r in region_data]

            results[region] = {
                "avg_latency": round(float(np.mean(latencies)), 2) if latencies else 0,
                "p95_latency": round(float(np.percentile(latencies, 95)), 2) if latencies else 0,
                "avg_uptime": round(float(np.mean(uptimes)), 2) if uptimes else 0,
                "breaches": sum(1 for lat in latencies if lat > threshold_ms)
            }
        
        return results
    except Exception as e:
        return {"error": str(e)}, 400
