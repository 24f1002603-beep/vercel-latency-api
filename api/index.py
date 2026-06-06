from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import json
import os
import numpy as np
from typing import List, Dict

app = FastAPI()

# Enable CORS so dashboards from anywhere can call it
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Any website can call it
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the sample telemetry data once when the function starts
# (In real life you'd load from a database, but here we use the file)
DATA_FILE = "q-vercel-latency.json"

try:
    with open(DATA_FILE, "r") as f:
        telemetry_data = json.load(f)
except:
    telemetry_data = []  # Empty if file missing

@app.post("/analytics")  # This is the POST endpoint
async def analytics(request: Request):
    body = await request.json()
    
    regions = body.get("regions", [])
    threshold_ms = body.get("threshold_ms", 180)
    
    results = {}
    
    # Group data by region
    for region in regions:
        region_data = [record for record in telemetry_data if record.get("region") == region]
        
        if not region_data:
            results[region] = {
                "avg_latency": 0,
                "p95_latency": 0,
                "avg_uptime": 0,
                "breaches": 0
            }
            continue
        
        # Extract numbers
        latencies = [r.get("latency_ms", 0) for r in region_data]
        uptimes = [r.get("uptime", 0) for r in region_data]  # assuming uptime % or 0-1
        
        # Calculations
        avg_latency = float(np.mean(latencies)) if latencies else 0
        p95_latency = float(np.percentile(latencies, 95)) if latencies else 0
        avg_uptime = float(np.mean(uptimes)) if uptimes else 0
        breaches = sum(1 for lat in latencies if lat > threshold_ms)
        
        results[region] = {
            "avg_latency": round(avg_latency, 2),
            "p95_latency": round(p95_latency, 2),
            "avg_uptime": round(avg_uptime, 2),
            "breaches": breaches
        }
    
    return results
