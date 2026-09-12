"""
Aditya-L1 Real-Time Telemetry Stream Ingestion Engine
ISSDC Downlink Interface, Telemetry Ring Buffer, and Sliding-Window Physics Feature Extractor.
"""

import time
import json
import asyncio
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, AsyncGenerator, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timezone

@dataclass
class TelemetryPacket:
    timestamp: str
    packet_id: int
    station_id: str          # e.g., "ISTRAC-BLR", "DSN-GOLDSTONE", "SVALBARD"
    solexs_sdd2_counts: float
    hel1os_czt1_20_to_40: float
    hel1os_czt1_80_to_150: float
    hel1os_cdte1_5_to_20: float
    goes_flux_long: float
    voltage_bus_v: float
    payload_temp_c: float
    handover_in_progress: bool
    packet_loss_rate: float
    checksum_valid: bool

class StreamingFeatureBuffer:
    """
    Maintains a rolling ring-buffer of multi-instrument telemetry frames
    and computes real-time astrophysical precursor features on the fly.
    """
    def __init__(self, capacity: int = 120):
        self.capacity = capacity
        self.timestamps: List[datetime] = []
        self.solexs_counts: List[float] = []
        self.hel1os_hard: List[float] = []
        self.hel1os_soft: List[float] = []
        self.goes_flux: List[float] = []
        self.packet_loss_history: List[float] = []

    def append(self, packet: TelemetryPacket):
        dt = datetime.fromisoformat(packet.timestamp.replace("Z", "+00:00"))
        self.timestamps.append(dt)
        self.solexs_counts.append(float(packet.solexs_sdd2_counts))
        self.hel1os_hard.append(float(packet.hel1os_czt1_20_to_40))
        self.hel1os_soft.append(float(packet.hel1os_cdte1_5_to_20))
        self.goes_flux.append(float(packet.goes_flux_long))
        self.packet_loss_history.append(float(packet.packet_loss_rate))

        if len(self.timestamps) > self.capacity:
            self.timestamps.pop(0)
            self.solexs_counts.pop(0)
            self.hel1os_hard.pop(0)
            self.hel1os_soft.pop(0)
            self.goes_flux.pop(0)
            self.packet_loss_history.pop(0)

    def compute_features(self) -> Dict[str, float]:
        """
        Extracts 24-channel rolling physics & temporal features required by LSTM and ensemble.
        """
        n = len(self.solexs_counts)
        if n < 5:
            return {
                "flux_long_raw": self.goes_flux[-1] if n > 0 else 1e-7,
                "flux_long_baseline": 1e-7,
                "flux_long_zscore": 0.0,
                "solexs_flux_accel": 0.0,
                "solexs_brightening": 0.0,
                "spectral_hardening": 1.0,
                "microflare_score": 0.0,
                "neupert_phase_lag": 0.0,
                "solexs_fft_dom_freq": 0.0,
                "solexs_fft_entropy": 1.0,
                "effective_packet_loss": self.packet_loss_history[-1] if n > 0 else 0.0,
            }

        arr_flux = np.array(self.goes_flux)
        arr_solexs = np.array(self.solexs_counts)
        arr_hard = np.array(self.hel1os_hard)
        arr_soft = np.array(self.hel1os_soft)

        # Baseline & Z-score
        baseline = float(np.median(arr_flux[-min(n, 30):]))
        std = float(np.std(arr_flux[-min(n, 30):])) + 1e-12
        zscore = float((arr_flux[-1] - baseline) / std)

        # Flux derivative & acceleration
        d_flux = np.diff(arr_flux[-min(n, 10):])
        d2_flux = np.diff(d_flux) if len(d_flux) > 1 else np.array([0.0])
        flux_accel = float(d2_flux[-1]) if len(d2_flux) > 0 else 0.0

        # Thermal brightening (SoLEXS count rise over last 5 intervals)
        solexs_baseline = np.median(arr_solexs[-min(n, 15):]) + 1e-6
        solexs_brightening = float((arr_solexs[-1] - solexs_baseline) / solexs_baseline)

        # Spectral hardening: hard X-ray / soft X-ray ratio
        soft_val = arr_soft[-1] if arr_soft[-1] > 0 else 1.0
        spectral_hardening = float(arr_hard[-1] / soft_val)

        # Microflare high-frequency fluctuation power
        hf_power = float(np.var(np.diff(arr_solexs[-min(n, 10):])) if len(arr_solexs) >= 10 else 0.0)
        microflare_score = float(np.log1p(max(0.0, hf_power)))

        # FFT dominant frequency & entropy on SoLEXS
        fft_vals = np.abs(np.fft.rfft(arr_solexs[-min(n, 32):]))
        if len(fft_vals) > 1:
            fft_norm = fft_vals[1:] / (np.sum(fft_vals[1:]) + 1e-12)
            fft_entropy = float(-np.sum(fft_norm * np.log(fft_norm + 1e-12)))
            dom_freq_idx = int(np.argmax(fft_vals[1:])) + 1
            dom_freq = float(dom_freq_idx / (2.0 * len(fft_vals)))
        else:
            fft_entropy = 1.0
            dom_freq = 0.0

        # Neupert effect phase lag
        neupert_lag = 0.0
        if n >= 15:
            d_soft = np.gradient(arr_solexs[-15:])
            cross_corr = np.correlate(d_soft - np.mean(d_soft), arr_hard[-15:] - np.mean(arr_hard[-15:]), mode="full")
            neupert_lag = float(np.argmax(cross_corr) - 14)

        return {
            "flux_long_raw": float(arr_flux[-1]),
            "flux_long_baseline": baseline,
            "flux_long_zscore": zscore,
            "solexs_flux_accel": flux_accel,
            "solexs_brightening": solexs_brightening,
            "spectral_hardening": spectral_hardening,
            "microflare_score": microflare_score,
            "neupert_phase_lag": neupert_lag,
            "solexs_fft_dom_freq": dom_freq,
            "solexs_fft_entropy": fft_entropy,
            "effective_packet_loss": float(self.packet_loss_history[-1]),
        }

class TelemetryStreamSimulator:
    """
    High-fidelity streaming telemetry simulator capable of replaying authentic
    Aditya-L1 datasets or synthesizing real-time operational feeds with
    ground station handovers and packet loss events.
    """
    def __init__(self, dataset_path: str = "data/processed/dashboard_data.csv"):
        self.dataset_path = dataset_path
        self.df: Optional[pd.DataFrame] = None
        self.current_idx = 0
        self.packet_counter = 1000
        self.stations = ["ISTRAC-BLR", "DSN-GOLDSTONE", "SVALBARD", "SAN-MARTIN"]
        self.current_station_idx = 0
        self.handover_countdown = 120
        self.simulated_loss_rate = 0.02
        self._load_dataset()

    def _load_dataset(self):
        try:
            self.df = pd.read_csv(self.dataset_path, nrows=5000)
            print(f"Loaded {len(self.df)} telemetry baseline rows for stream simulation.")
        except Exception as e:
            print(f"Dataset load warning: {e}. Falling back to dynamic synthesis.")
            self.df = None

    def get_next_packet(self, force_packet_loss: Optional[float] = None) -> TelemetryPacket:
        self.packet_counter += 1
        self.handover_countdown -= 1

        # Simulate periodic ground station handovers
        handover_in_progress = False
        if self.handover_countdown <= 0:
            handover_in_progress = True
            if self.handover_countdown <= -5:
                self.current_station_idx = (self.current_station_idx + 1) % len(self.stations)
                self.handover_countdown = np.random.randint(100, 200)

        # Compute dynamic packet loss
        if force_packet_loss is not None:
            loss_rate = float(force_packet_loss)
        elif handover_in_progress:
            loss_rate = float(np.random.uniform(0.18, 0.45))
        else:
            loss_rate = float(np.random.beta(1.5, 40.0) * 0.08)

        now_str = datetime.now(timezone.utc).isoformat()

        if self.df is not None and len(self.df) > 0:
            row = self.df.iloc[self.current_idx]
            self.current_idx = (self.current_idx + 1) % len(self.df)

            solexs = float(row.get("solexs_sdd2_counts", 120.0))
            czt = float(row.get("hel1os_czt1_20_to_40_ctr", 45.0))
            czt_hi = float(row.get("hel1os_czt1_80_to_150_ctr", 12.0))
            cdte = float(row.get("hel1os_cdte1_5_to_20_ctr", 80.0))
            flux = float(row.get("flux_long_raw", 1.5e-6))
        else:
            # Dynamic synthesis
            t = self.packet_counter * 0.1
            solexs = 100.0 + 30.0 * np.sin(t * 0.5) + np.random.normal(0, 5)
            czt = 40.0 + 15.0 * np.cos(t * 0.3) + np.random.normal(0, 3)
            czt_hi = 10.0 + 4.0 * np.sin(t * 0.2) + np.random.normal(0, 1)
            cdte = 75.0 + 20.0 * np.sin(t * 0.4) + np.random.normal(0, 4)
            flux = 1.0e-6 * (1.0 + 0.5 * np.sin(t * 0.1))

        # Apply packet loss noise / attenuation if dropout occurs
        if np.random.rand() < loss_rate:
            checksum_valid = False
        else:
            checksum_valid = True

        return TelemetryPacket(
            timestamp=now_str,
            packet_id=self.packet_counter,
            station_id=self.stations[self.current_station_idx],
            solexs_sdd2_counts=max(0.0, solexs),
            hel1os_czt1_20_to_40=max(0.0, czt),
            hel1os_czt1_80_to_150=max(0.0, czt_hi),
            hel1os_cdte1_5_to_20=max(0.0, cdte),
            goes_flux_long=max(1e-9, flux),
            voltage_bus_v=float(28.0 + np.random.normal(0, 0.15)),
            payload_temp_c=float(-18.5 + np.random.normal(0, 0.3)),
            handover_in_progress=handover_in_progress,
            packet_loss_rate=round(loss_rate, 4),
            checksum_valid=checksum_valid
        )
