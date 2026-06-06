from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import json
import numpy as np

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Explicit OPTIONS handler for preflight requests
@app.options("/{rest_of_path:path}")
async def options_handler(rest_of_path: str):
    response = JSONResponse(content={})
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response

# Load telemetry data
with open("q-vercel-latency.json", "r") as f:
    telemetry = json.load(f)

@app.post("/")
def analyze(data: dict):

    regions = data.get("regions", [])
    threshold = data.get("threshold_ms", 180)

    result = {}

    for region in regions:

        rows = [r for r in telemetry if r["region"] == region]

        if not rows:
            continue

        latencies = [r["latency_ms"] for r in rows]
        uptimes = [r["uptime_pct"] for r in rows]

        result[region] = {
            "avg_latency": round(float(np.mean(latencies)), 2),
            "p95_latency": round(float(np.percentile(latencies, 95)), 2),
            "avg_uptime": round(float(np.mean(uptimes)), 2),
            "breaches": sum(1 for x in latencies if x > threshold)
        }

    response = JSONResponse(content=result)
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response

@app.get("/")
def root():
    response = JSONResponse(content={"message": "API is running"})
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response
