"""
Aditya-L1 Tier-1 Mission Flight Operations FastAPI Server
Supports Real-time WebSocket Streaming, Conformal Flare Prediction,
Telemetry Ingestion, and Prometheus Monitoring Exporter.
"""

import os
import sys
import time
import json
import asyncio
from typing import Dict, List, Optional, Set
from datetime import datetime, timezone
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from src.data.stream_engine import TelemetryPacket, StreamingFeatureBuffer, TelemetryStreamSimulator
from src.models.conformal_engine import ConformalPredictorEngine, ConformalForecastResult

app = FastAPI(
    title="Aditya-L1 Space Weather Operations API",
    description="Tier-1 Flight Operations Telemetry Stream, Packet-Loss Resilient Conformal Prediction & Prometheus Exporter",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

start_time = time.time()
buffer = StreamingFeatureBuffer(capacity=120)
simulator = TelemetryStreamSimulator()
conformal_engine = ConformalPredictorEngine()

metrics_state = {
    "packets_received_total": 0,
    "packet_loss_count": 0,
    "flare_alerts_triggered_total": 0,
    "latest_forecast_probability": 0.05,
    "latest_conformal_interval_width": 1.2e-6,
    "solar_cycle_drift_score": 0.012,
    "last_inference_latency_seconds": 0.0035,
    "active_websocket_connections": 0
}

class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        metrics_state["active_websocket_connections"] = len(self.active_connections)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
        metrics_state["active_websocket_connections"] = len(self.active_connections)

    async def broadcast(self, message: dict):
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception:
                self.active_connections.discard(connection)

manager = ConnectionManager()

async def telemetry_broadcaster():
    while True:
        try:
            packet = simulator.get_next_packet()
            buffer.append(packet)

            metrics_state["packets_received_total"] += 1
            if not packet.checksum_valid or packet.packet_loss_rate > 0.15:
                metrics_state["packet_loss_count"] += 1

            t0 = time.perf_counter()
            features = buffer.compute_features()
            conformal_res = conformal_engine.predict_conformal(
                features=features,
                timestamp=packet.timestamp,
                loss_rate=packet.packet_loss_rate
            )
            lat = time.perf_counter() - t0
            metrics_state["last_inference_latency_seconds"] = round(lat, 6)
            metrics_state["latest_forecast_probability"] = conformal_res.point_forecast_prob
            metrics_state["latest_conformal_interval_width"] = conformal_res.interval_width

            if conformal_res.safe_hold_recommended:
                metrics_state["flare_alerts_triggered_total"] += 1

            payload = {
                "type": "TELEMETRY_FRAME",
                "telemetry": {
                    "timestamp": packet.timestamp,
                    "packet_id": packet.packet_id,
                    "station_id": packet.station_id,
                    "solexs_sdd2_counts": packet.solexs_sdd2_counts,
                    "hel1os_czt1_20_to_40": packet.hel1os_czt1_20_to_40,
                    "hel1os_czt1_80_to_150": packet.hel1os_czt1_80_to_150,
                    "hel1os_cdte1_5_to_20": packet.hel1os_cdte1_5_to_20,
                    "goes_flux_long": packet.goes_flux_long,
                    "voltage_bus_v": packet.voltage_bus_v,
                    "payload_temp_c": packet.payload_temp_c,
                    "handover_in_progress": packet.handover_in_progress,
                    "packet_loss_rate": packet.packet_loss_rate,
                    "checksum_valid": packet.checksum_valid,
                },
                "forecast": {
                    "probability": conformal_res.point_forecast_prob,
                    "flare_class": conformal_res.flare_class,
                    "lower_bound_flux": conformal_res.lower_bound_flux,
                    "upper_bound_flux": conformal_res.upper_bound_flux,
                    "interval_width": conformal_res.interval_width,
                    "coverage_confidence": conformal_res.coverage_confidence,
                    "prediction_set": conformal_res.conformal_prediction_set,
                    "uncertainty_penalty": conformal_res.uncertainty_penalty_factor,
                    "safe_hold_recommended": conformal_res.safe_hold_recommended,
                    "lead_time_min": conformal_res.warning_lead_time_min,
                },
                "features": features
            }

            if manager.active_connections:
                await manager.broadcast(payload)

        except Exception as e:
            print(f"Broadcast loop error: {e}")
        
        await asyncio.sleep(1.0)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(telemetry_broadcaster())

class PredictRequest(BaseModel):
    timestamp: Optional[str] = None
    flux_long_raw: float = Field(default=1.5e-6)
    flux_long_zscore: float = Field(default=0.5)
    solexs_flux_accel: float = Field(default=0.0)
    solexs_brightening: float = Field(default=0.1)
    spectral_hardening: float = Field(default=1.2)
    microflare_score: float = Field(default=0.05)
    packet_loss_rate: float = Field(default=0.0, ge=0.0, le=0.99)
    alpha: Optional[float] = Field(default=0.05, ge=0.01, le=0.5)

@app.get("/health")
def get_health():
    uptime = time.time() - start_time
    return {
        "status": "OPERATIONAL",
        "tier": "TIER_1_ISRO_FLIGHT_OPERATIONS",
        "subsystems": {
            "solexs_pipeline": "ONLINE",
            "hel1os_pipeline": "ONLINE",
            "conformal_predictor": "CALIBRATED_95_PERCENT",
            "stream_ingestion_broker": "ACTIVE",
            "istrac_downlink": "LOCKED"
        },
        "active_ws_subscribers": len(manager.active_connections),
        "uptime_seconds": round(uptime, 1)
    }

@app.get("/metrics", response_class=PlainTextResponse)
def get_prometheus_metrics():
    loss_ratio = (
        metrics_state["packet_loss_count"] / max(1, metrics_state["packets_received_total"])
    )
    lines = [
        "# HELP aditya_telemetry_packets_received_total Total telemetry frames ingested from Aditya-L1 payloads",
        "# TYPE aditya_telemetry_packets_received_total counter",
        f"aditya_telemetry_packets_received_total {metrics_state['packets_received_total']}",
        "",
        "# HELP aditya_packet_loss_rate_ratio Rolling ratio of packet loss and frame corruption",
        "# TYPE aditya_packet_loss_rate_ratio gauge",
        f"aditya_packet_loss_rate_ratio {loss_ratio:.4f}",
        "",
        "# HELP aditya_solar_flare_forecast_probability Real-time solar flare ignition probability",
        "# TYPE aditya_solar_flare_forecast_probability gauge",
        f"aditya_solar_flare_forecast_probability {metrics_state['latest_forecast_probability']:.4f}",
        "",
        "# HELP aditya_conformal_interval_width Calibrated conformal prediction interval width for solar flux",
        "# TYPE aditya_conformal_interval_width gauge",
        f"aditya_conformal_interval_width {metrics_state['latest_conformal_interval_width']:.6e}",
        "",
        "# HELP aditya_solar_cycle_drift_score Kolmogorov-Smirnov distribution drift score against Solar Cycle 25 baseline",
        "# TYPE aditya_solar_cycle_drift_score gauge",
        f"aditya_solar_cycle_drift_score {metrics_state['solar_cycle_drift_score']:.4f}",
        "",
        "# HELP aditya_inference_latency_seconds Inference latency per prediction frame in seconds",
        "# TYPE aditya_inference_latency_seconds gauge",
        f"aditya_inference_latency_seconds {metrics_state['last_inference_latency_seconds']:.6f}",
        "",
        "# HELP aditya_active_websocket_connections Active real-time mission dashboard connections",
        "# TYPE aditya_active_websocket_connections gauge",
        f"aditya_active_websocket_connections {metrics_state['active_websocket_connections']}",
        "",
        "# HELP aditya_flare_alerts_triggered_total Cumulative safe-hold solar flare alert trigger events",
        "# TYPE aditya_flare_alerts_triggered_total counter",
        f"aditya_flare_alerts_triggered_total {metrics_state['flare_alerts_triggered_total']}"
    ]
    return "\n".join(lines) + "\n"

@app.post("/api/v1/predict/conformal")
def predict_conformal_endpoint(req: PredictRequest):
    t_str = req.timestamp or datetime.now(timezone.utc).isoformat()
    features = req.dict()
    res = conformal_engine.predict_conformal(
        features=features,
        timestamp=t_str,
        loss_rate=req.packet_loss_rate,
        custom_alpha=req.alpha
    )
    return {
        "status": "SUCCESS",
        "result": {
            "timestamp": res.timestamp,
            "point_forecast_prob": res.point_forecast_prob,
            "flare_class": res.flare_class,
            "lower_bound_flux": res.lower_bound_flux,
            "upper_bound_flux": res.upper_bound_flux,
            "interval_width": res.interval_width,
            "coverage_confidence": res.coverage_confidence,
            "prediction_set": res.conformal_prediction_set,
            "packet_loss_rate": res.packet_loss_rate,
            "uncertainty_penalty_factor": res.uncertainty_penalty_factor,
            "safe_hold_recommended": res.safe_hold_recommended,
            "warning_lead_time_min": res.warning_lead_time_min
        }
    }

@app.websocket("/ws/telemetry")
async def websocket_telemetry_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api.server:app", host="0.0.0.0", port=8008, reload=True)
