"""Generate the complete bilingual (EN/ZH) HTML report suite from test data.

Report types produced (matching predictive-maintenance-mcp-main scope):
  1. spectrum  — frequency-spectrum analysis report
  2. envelope  — envelope-analysis report
  3. diagnostic — full MCSA diagnostic report

Each type is generated in English and Chinese for every fault scenario:
  healthy, broken rotor bars (brb), eccentricity, bearing, and the
  combined case.

Run: python scripts/generate_all_reports.py [--out DIR]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np

from mcp_server_mcsa.analysis.envelope import envelope_spectrum, hilbert_envelope
from mcp_server_mcsa.analysis.fault_detection import envelope_statistical_indices
from mcp_server_mcsa.analysis.preprocessing import preprocess_pipeline
from mcp_server_mcsa.analysis.spectral import compute_fft_spectrum, detect_peaks
from mcp_server_mcsa.analysis.test_signal import generate_test_signal
from mcp_server_mcsa.report_generator import (
    REPORTS_DIR,
    save_diagnostic_report,
    save_envelope_report,
    save_spectrum_report,
)

MOTOR = {
    "supply_freq_hz": 50.0,
    "poles": 4,
    "rotor_speed_rpm": 1470.0,
}

SCENARIOS = [
    ("healthy", None),
    ("brb", ["brb"]),
    ("eccentricity", ["eccentricity"]),
    ("bearing", ["bearing"]),
    ("combined", ["brb", "eccentricity", "bearing"]),
]


def build_signal(faults: list[str] | None) -> tuple[np.ndarray, float]:
    """Generate a synthetic motor-current test signal."""
    result = generate_test_signal(
        duration_s=4.0,
        fs_sample=5000.0,
        supply_freq_hz=MOTOR["supply_freq_hz"],
        poles=MOTOR["poles"],
        rotor_speed_rpm=MOTOR["rotor_speed_rpm"],
        noise_std=0.01,
        faults=faults,
        fault_severity=0.04 if faults else 0.0,
    )
    return np.asarray(result["signal"], dtype=np.float64), result["sampling_freq_hz"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=REPORTS_DIR,
                        help="Output directory (default: %(default)s)")
    args = parser.parse_args()

    out_dir = args.out
    out_dir.mkdir(parents=True, exist_ok=True)

    produced: list[str] = []
    for scenario, faults in SCENARIOS:
        x, fs = build_signal(faults)
        x_proc = preprocess_pipeline(x, fs, window="hann")
        freqs, amps = compute_fft_spectrum(x_proc, fs, sided="one")

        # Peaks for the spectrum report
        peaks = detect_peaks(freqs, amps, prominence=0.001, max_peaks=10)

        # Envelope data
        env_freqs, env_amps = envelope_spectrum(x, fs, bandpass=(400, 1200))
        env = hilbert_envelope(x)
        env_stats = envelope_statistical_indices(env - np.mean(env))

        signal_info = {
            "n_samples": len(x),
            "sampling_freq_hz": fs,
            "duration_s": round(len(x) / fs, 3),
            "freq_resolution_hz": round(float(freqs[1] - freqs[0]), 6) if len(freqs) > 1 else 0,
        }

        for lang in ("en", "zh"):
            # 1. Spectrum report
            saved = save_spectrum_report(
                freqs.tolist(), amps.tolist(), peaks, signal_info,
                label=f"{scenario}",
                metadata={"signal_id": f"sig_{scenario}", "faults_injected": faults},
                language=lang,
                directory=out_dir,
            )
            produced.append(saved["file_name"])

            # 2. Envelope report
            saved = save_envelope_report(
                env_freqs.tolist(), env_amps.tolist(), env_stats, signal_info,
                label=f"{scenario}",
                metadata={"signal_id": f"sig_{scenario}", "faults_injected": faults},
                language=lang,
                directory=out_dir,
            )
            produced.append(saved["file_name"])

        # 3. Diagnostic report (one per language, reusing full pipeline result)
        from mcp_server_mcsa.server import _run_diagnosis_pipeline

        for lang in ("en", "zh"):
            report = _run_diagnosis_pipeline(
                x, fs,
                supply_freq_hz=MOTOR["supply_freq_hz"],
                poles=MOTOR["poles"],
                rotor_speed_rpm=MOTOR["rotor_speed_rpm"],
                bearing_defect_freq_hz=6.0,
                tolerance_hz=0.5,
                language=lang,
                signal_id=f"sig_{scenario}",
                include_spectrum=True,
            )
            saved = save_diagnostic_report(
                report, label=f"{scenario}",
                metadata={"signal_id": f"sig_{scenario}", "faults_injected": faults},
                language=lang,
                directory=out_dir,
            )
            produced.append(saved["file_name"])

        print(f"[+] {scenario:12s} complete (en+zh × spectrum/envelope/diagnostic)")

    print(f"\nGenerated {len(produced)} report files in {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
