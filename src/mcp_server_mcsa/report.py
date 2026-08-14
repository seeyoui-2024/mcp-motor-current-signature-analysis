"""MCSA Report generation module.

Generates HTML and DOCX diagnostic reports from MCSA analysis results.
Supports English and Chinese (zh-CN) languages.
"""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Any

from mcp_server_mcsa.i18n import t


_SEVERITY_COLORS = {
    "healthy": "#28a745",
    "incipient": "#ffc107",
    "moderate": "#fd7e14",
    "severe": "#dc3545",
    "critical": "#721c24",
    "normal": "#28a745",
    "watch": "#ffc107",
    "warning": "#fd7e14",
}

_SEVERITY_LABELS = {
    "healthy": "severity.healthy",
    "incipient": "severity.incipient",
    "moderate": "severity.moderate",
    "severe": "severity.severe",
    "critical": "severity.critical",
    "normal": "severity.normal",
    "watch": "severity.watch",
    "warning": "severity.warning",
}

_FAULT_TYPE_LABELS = {
    "broken_rotor_bars": "fault.broken_rotor_bars",
    "eccentricity": "fault.eccentricity",
    "stator_inter_turn": "fault.stator_inter_turn",
    "bearing": "fault.bearing",
}

_FAULT_KEYS = [
    ("broken_rotor_bars", "fault.broken_rotor_bars"),
    ("eccentricity", "fault.eccentricity"),
    ("stator_inter_turn", "fault.stator_inter_turn"),
    ("bearing", "fault.bearing"),
]


def _severity_color(severity: str) -> str:
    return _SEVERITY_COLORS.get(severity, "#6c757d")


def _severity_label(severity: str, lang: str) -> str:
    key = _SEVERITY_LABELS.get(severity)
    return t(key, lang) if key else severity


def _fault_label(fault_type: str, lang: str) -> str:
    key = _FAULT_TYPE_LABELS.get(fault_type)
    return t(key, lang) if key else fault_type


def _overall_class(overall: str) -> str:
    if any(w in overall.lower() for w in ["critical", "severe", "危急"]):
        return "critical"
    if any(w in overall.lower() for w in ["warning", "moderate", "警告", "中等"]):
        return "warning"
    return ""


def _translate_assessment(text: str, lang: str) -> str:
    """Translate overall assessment text to the target language using i18n system."""
    if not text:
        return text
    # Try to map text to a translation key
    upper = text.upper()
    _KEY_MAP = {
        "CRITICAL": "assessment.critical",
        "WARNING": "assessment.warning",
        "WATCH": "assessment.watch_incipient",
        "NORMAL": "assessment.normal",
    }
    for prefix, key in _KEY_MAP.items():
        if upper.startswith(prefix):
            return t(key, lang)
    # Fallback: return original text
    return text


def _get_recommendations(summary: dict, lang: str) -> list[str]:
    recs: list[str] = []
    for sev_key, fault_key in [
        ("brb_severity", "broken_rotor_bars"),
        ("eccentricity_severity", "eccentricity"),
        ("stator_severity", "stator_inter_turn"),
    ]:
        sev = summary.get(sev_key, "")
        fault_name = _fault_label(fault_key, lang)
        if sev in ("severe", "critical"):
            recs.append(f"{fault_name}: {t('rec.immediate', lang)}")
        elif sev == "moderate":
            recs.append(f"{fault_name}: {t('rec.maintenance', lang)}")
        elif sev == "incipient":
            recs.append(f"{fault_name}: {t('rec.monitoring', lang)}")

    env_kurtosis = summary.get("envelope_kurtosis", 0)
    if env_kurtosis and env_kurtosis > 6.0:
        recs.append(f"{t('rec.review', lang)} ({t('env.kurtosis', lang)}: {env_kurtosis})")

    if not recs:
        recs.append(t("rec.review", lang))
    return recs


def generate_report_impl(
    data: dict[str, Any],
    formats: list[str] | None = None,
    lang: str = "en",
) -> dict[str, Any]:
    if formats is None:
        formats = ["html"]

    data_dir = Path(os.environ.get("MCSA_DATA_DIR", Path.home() / ".mcsa_data"))
    reports_dir = data_dir / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results: dict[str, Any] = {"report_id": f"mcsa_report_{timestamp}", "files": []}

    if "html" in formats:
        from mcp_server_mcsa.report_html import _generate_html_report
        html_content = _generate_html_report(data, lang)
        html_path = reports_dir / f"mcsa_report_{timestamp}.html"
        html_path.write_text(html_content, encoding="utf-8")
        results["files"].append({
            "format": "html",
            "path": str(html_path),
            "size_bytes": len(html_content.encode("utf-8")),
        })

    if "docx" in formats:
        from mcp_server_mcsa.report_docx import _generate_docx_report
        docx_bytes, error = _generate_docx_report(data, lang)
        if docx_bytes is not None:
            docx_path = reports_dir / f"mcsa_report_{timestamp}.docx"
            docx_path.write_bytes(docx_bytes)
            results["files"].append({
                "format": "docx",
                "path": str(docx_path),
                "size_bytes": len(docx_bytes),
            })
        else:
            results["files"].append({
                "format": "docx",
                "error": error,
            })

    results["lang"] = lang
    results["generated_at"] = datetime.now().isoformat()
    return results