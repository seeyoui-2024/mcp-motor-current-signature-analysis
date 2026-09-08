"""Report generation for MCSA diagnostics.

Saves professional, standalone HTML reports (interactive Plotly charts,
bilingual en/zh with client-side toggle) to a reports directory, mirroring
the workflow of the predictive-maintenance-mcp-main project.
"""

from __future__ import annotations

import itertools
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from mcp_server_mcsa.html_templates import (
    create_diagnostic_report,
    create_envelope_report,
    create_spectrum_report,
)
from mcp_server_mcsa.i18n import Language, get_text
from mcp_server_mcsa.report_docx import generate_docx_report as _generate_docx_report

logger = logging.getLogger(__name__)

#: Default output directory (configurable via MCSA_REPORTS_DIR env var).
REPORTS_DIR = Path(__import__("os").environ.get("MCSA_REPORTS_DIR", Path.home() / ".mcsa_reports"))
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

#: Process-local sequence so consecutive runs never collide on Windows,
#: where two calls in the same microsecond can produce identical timestamps.
_report_sequence = itertools.count()


def timestamped_report_name(label: str, ext: str = "html") -> str:
    """Build a unique, timestamped report filename."""
    safe_label = Path(label).stem.replace("/", "_").replace("\\", "_")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    seq = next(_report_sequence)
    return f"mcsa_diagnostic_{safe_label}_{stamp}-{seq:06d}.{ext}"


def save_diagnostic_report(
    report_data: dict[str, Any],
    label: str = "signal",
    metadata: dict[str, Any] | None = None,
    language: Language = "en",
    directory: Path | None = None,
) -> dict[str, Any]:
    """Render and save a bilingual MCSA diagnostic HTML report.

    Args:
        report_data: Diagnostic dict from ``run_full_diagnosis`` /
            ``diagnose_from_file`` (must include a ``spectrum`` key if a
            chart is desired).
        label: Short label embedded in the filename (signal id optimal).
        metadata: Extra provenance metadata stored in the report.
        language: Initial page language ("en" or "zh").
        directory: Output directory (defaults to REPORTS_DIR).

    Returns:
        Dict with file path, name, size, report type, and a message.
    """
    out_dir = Path(directory) if directory is not None else REPORTS_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    meta = dict(metadata or {})
    meta.setdefault("report_type", "mcsa_full_diagnostic")
    meta.setdefault("generated_utc", datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    meta.setdefault("language", language)
    if "signal_id" in report_data:
        meta.setdefault("signal_id", report_data["signal_id"])

    html = create_diagnostic_report(
        report_data, metadata=meta, language=language
    )

    output_file = out_dir / timestamped_report_name(label)
    output_file.write_text(html, encoding="utf-8")

    logger.info("HTML diagnostic report saved: %s", output_file.name)

    return {
        "file_path": str(output_file.absolute()),
        "file_name": output_file.name,
        "file_size_kb": round(output_file.stat().st_size / 1024, 2),
        "report_type": "mcsa_full_diagnostic",
        "language": language,
        "metadata": meta,
        "message": f"{get_text('report.html_saved', language)}: {output_file.name} ({output_file.stat().st_size / 1024:.2f} KB)",
    }


def save_spectrum_report(
    frequencies_hz: list[float],
    amplitudes: list[float],
    peaks: list[dict[str, Any]],
    signal_info: dict[str, Any],
    label: str = "spectrum",
    metadata: dict[str, Any] | None = None,
    language: Language = "en",
    directory: Path | None = None,
) -> dict[str, Any]:
    """Render and save a bilingual frequency-spectrum HTML report.

    Args:
        frequencies_hz: Spectrum frequency axis (Hz).
        amplitudes: Spectrum amplitude values.
        peaks: Detected peaks for the peaks table.
        signal_info: Signal metadata (n_samples/sampling_freq_hz/duration_s).
        label: Short label embedded in the filename.
        metadata: Extra provenance metadata.
        language: Initial page language ("en" or "zh").
        directory: Output directory (defaults to REPORTS_DIR).

    Returns:
        Dict with file path, name, size, report type, and a message.
    """
    out_dir = Path(directory) if directory is not None else REPORTS_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    meta = dict(metadata or {})
    meta.setdefault("report_type", "mcsa_spectrum")
    meta.setdefault("generated_utc", datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    meta.setdefault("language", language)

    html = create_spectrum_report(
        frequencies_hz, amplitudes, peaks, signal_info,
        metadata=meta, language=language,
    )
    output_file = out_dir / timestamped_report_name(f"spectrum_{label}")
    output_file.write_text(html, encoding="utf-8")
    logger.info("HTML spectrum report saved: %s", output_file.name)

    return {
        "file_path": str(output_file.absolute()),
        "file_name": output_file.name,
        "file_size_kb": round(output_file.stat().st_size / 1024, 2),
        "report_type": "mcsa_spectrum",
        "language": language,
        "metadata": meta,
        "message": f"{get_text('report.html_saved', language)}: {output_file.name} ({output_file.stat().st_size / 1024:.2f} KB)",
    }


def save_envelope_report(
    frequencies_hz: list[float],
    amplitudes: list[float],
    env_stats: dict[str, Any],
    signal_info: dict[str, Any],
    label: str = "envelope",
    metadata: dict[str, Any] | None = None,
    language: Language = "en",
    directory: Path | None = None,
) -> dict[str, Any]:
    """Render and save a bilingual envelope-analysis HTML report.

    Args:
        frequencies_hz: Envelope spectrum frequency axis (Hz).
        amplitudes: Envelope spectrum amplitude values.
        env_stats: Envelope statistical indices.
        signal_info: Signal metadata (n_samples/sampling_freq_hz/duration_s).
        label: Short label embedded in the filename.
        metadata: Extra provenance metadata.
        language: Initial page language ("en" or "zh").
        directory: Output directory (defaults to REPORTS_DIR).

    Returns:
        Dict with file path, name, size, report type, and a message.
    """
    out_dir = Path(directory) if directory is not None else REPORTS_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    meta = dict(metadata or {})
    meta.setdefault("report_type", "mcsa_envelope")
    meta.setdefault("generated_utc", datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    meta.setdefault("language", language)

    html = create_envelope_report(
        frequencies_hz, amplitudes, env_stats, signal_info,
        metadata=meta, language=language,
    )
    output_file = out_dir / timestamped_report_name(f"envelope_{label}")
    output_file.write_text(html, encoding="utf-8")
    logger.info("HTML envelope report saved: %s", output_file.name)

    return {
        "file_path": str(output_file.absolute()),
        "file_name": output_file.name,
        "file_size_kb": round(output_file.stat().st_size / 1024, 2),
        "report_type": "mcsa_envelope",
        "language": language,
        "metadata": meta,
        "message": f"{get_text('report.html_saved', language)}: {output_file.name} ({output_file.stat().st_size / 1024:.2f} KB)",
    }


def save_docx_report(
    report_data: dict[str, Any],
    label: str = "signal",
    metadata: dict[str, Any] | None = None,
    language: Language = "en",
    directory: Path | None = None,
) -> dict[str, Any]:
    """Render and save a bilingual MCSA diagnostic DOCX report.

    Args:
        report_data: Diagnostic dict from ``run_full_diagnosis`` /
            ``diagnose_from_file``.
        label: Short label embedded in the filename.
        metadata: Extra provenance metadata stored in the report.
        language: Report language ("en" or "zh").
        directory: Output directory (defaults to REPORTS_DIR).

    Returns:
        Dict with file path, name, size, report type, and a message.
    """
    out_dir = Path(directory) if directory is not None else REPORTS_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    meta = dict(metadata or {})
    meta.setdefault("report_type", "mcsa_docx")
    meta.setdefault("generated_utc", datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    meta.setdefault("language", language)
    if "signal_id" in report_data:
        meta.setdefault("signal_id", report_data["signal_id"])

    docx_bytes, error = _generate_docx_report(report_data, lang=language)
    if docx_bytes is None:
        return {"error": error}

    output_file = out_dir / timestamped_report_name(label, ext="docx")
    output_file.write_bytes(docx_bytes)

    logger.info("DOCX report saved: %s", output_file.name)

    return {
        "file_path": str(output_file.absolute()),
        "file_name": output_file.name,
        "file_size_kb": round(output_file.stat().st_size / 1024, 2),
        "report_type": "mcsa_docx",
        "language": language,
        "metadata": meta,
        "message": f"{get_text('report.docx_saved', language)}: {output_file.name} ({output_file.stat().st_size / 1024:.2f} KB)",
    }


def list_reports(directory: Path | None = None) -> list[dict[str, Any]]:
    """List saved reports (HTML and DOCX), newest first."""
    out_dir = Path(directory) if directory is not None else REPORTS_DIR
    reports = []
    for f in sorted(out_dir.glob("mcsa_diagnostic_*"), key=lambda p: p.stat().st_mtime, reverse=True):
        reports.append({
            "file_name": f.name,
            "file_path": str(f.absolute()),
            "file_size_kb": round(f.stat().st_size / 1024, 2),
            "created": f.stat().st_mtime,
        })
    return reports
