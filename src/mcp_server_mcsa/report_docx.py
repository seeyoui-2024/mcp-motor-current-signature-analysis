"""DOCX report generation for MCSA diagnostic reports."""

from __future__ import annotations

import io
from datetime import datetime
from typing import Any

from mcp_server_mcsa.i18n import t
from mcp_server_mcsa.report import (
    _FAULT_KEYS,
    _fault_label,
    _get_recommendations,
    _severity_color,
    _severity_label,
    _translate_assessment,
)


def _generate_docx_report(data: dict[str, Any], lang: str) -> tuple[bytes | None, str]:
    try:
        from docx import Document
        from docx.shared import Pt, RGBColor
    except ImportError:
        return None, "python-docx is not installed. Install with: pip install python-docx"

    doc = Document()
    style = doc.styles["Normal"]
    style.font.size = Pt(11)

    doc.add_heading(t("report.title.mcsa_diagnostic", lang), level=0)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    doc.add_paragraph(f"{t('ui.generated', lang)}: {timestamp}")

    motor_params = data.get("motor_parameters", {})
    signal_info = data.get("signal_info", {})
    fault_analysis = data.get("fault_analysis", {})
    band_energy = data.get("band_energy_around_fundamental", {})
    envelope_stats = data.get("envelope_statistics", {})
    summary = data.get("summary", {})
    source_file = data.get("source_file", "")

    _add_motor_section(doc, motor_params, lang)
    _add_signal_section(doc, signal_info, source_file, lang)
    _add_fault_section(doc, fault_analysis, lang)
    _add_env_section(doc, envelope_stats, lang)
    _add_band_section(doc, band_energy, lang)

    overall = summary.get("overall_assessment", "")
    if lang == "zh-CN":
        overall = _translate_assessment(overall, lang)
    doc.add_heading(t("report.title.overall_assessment", lang), level=1)
    doc.add_paragraph(overall)

    doc.add_heading(t("report.title.recommendations", lang), level=1)
    for rec in _get_recommendations(summary, lang):
        doc.add_paragraph(rec, style="List Bullet")

    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf.read(), ""


def _add_motor_section(doc: Any, params: dict[str, Any], lang: str) -> None:
    doc.add_heading(t("report.title.motor_params", lang), level=1)
    table = doc.add_table(rows=1, cols=2)
    table.style = "Light Grid Accent 1"
    hdr = table.rows[0].cells
    hdr[0].text = t("doc.parameter", lang)
    hdr[1].text = t("doc.value", lang)
    fields = [
        (t("motor.supply_freq", lang), params.get("supply_freq_hz", "")),
        (t("motor.poles", lang), params.get("poles", "")),
        (t("motor.synchronous_speed", lang), params.get("sync_speed_rpm", "")),
        (t("motor.rotor_speed", lang), params.get("rotor_speed_rpm", "")),
        (t("motor.slip", lang), params.get("slip", "")),
        (t("motor.rotor_freq", lang), params.get("rotor_freq_hz", "")),
        (t("motor.slip_freq", lang), params.get("slip_freq_hz", "")),
    ]
    for label, val in fields:
        row = table.add_row().cells
        row[0].text = str(label)
        row[1].text = str(val)


def _add_signal_section(doc: Any, info: dict[str, Any], source_file: str, lang: str) -> None:
    doc.add_heading(t("report.title.signal_info", lang), level=1)
    table = doc.add_table(rows=1, cols=2)
    table.style = "Light Grid Accent 1"
    hdr = table.rows[0].cells
    hdr[0].text = t("doc.parameter", lang)
    hdr[1].text = t("doc.value", lang)
    fields = [
        (t("signal.n_samples", lang), info.get("n_samples", "")),
        (t("signal.sampling_freq", lang), info.get("sampling_freq_hz", "")),
        (t("signal.duration", lang), info.get("duration_s", "")),
        (t("signal.freq_resolution", lang), info.get("freq_resolution_hz", "")),
    ]
    if source_file:
        fields.append((t("signal.source_file", lang), source_file))
    for label, val in fields:
        row = table.add_row().cells
        row[0].text = str(label)
        row[1].text = str(val)


def _add_fault_section(doc: Any, fault_analysis: dict[str, Any], lang: str) -> None:
    doc.add_heading(t("report.title.fault_analysis", lang), level=1)
    for fault_key, i18n_key in _FAULT_KEYS:
        fdata = fault_analysis.get(fault_key)
        if fdata is None:
            continue
        severity = fdata.get("severity", "")
        label = _fault_label(fault_key, lang)
        sev_text = _severity_label(severity, lang)

        h = doc.add_heading(f"{label} — {sev_text}", level=2)
        color = _severity_color(severity)
        for run in h.runs:
            run.font.color.rgb = RGBColor.from_string(color.lstrip("#"))

        if fault_key == "broken_rotor_bars":
            doc.add_paragraph(
                f"{t('fault.index', lang)}: {fdata.get('combined_index_db', 'N/A')} dB"
            )
            doc.add_paragraph(
                f"{t('fault.threshold_db', lang)}: "
                f"{fdata.get('thresholds_db', {}).get('severe', 'N/A')} dB"
            )
        elif fault_key in ("eccentricity", "stator_inter_turn"):
            doc.add_paragraph(
                f"{t('fault.index', lang)}: {fdata.get('worst_sideband_db', 'N/A')} dB"
            )
            sidebands = fdata.get("sidebands", [])
            if sidebands:
                table = doc.add_table(rows=1, cols=3)
                table.style = "Light Grid Accent 1"
                shdr = table.rows[0].cells
                shdr[0].text = t("fault.harmonic_order", lang)
                shdr[1].text = t("fault.lower", lang)
                shdr[2].text = t("fault.upper", lang)
                for sb in sidebands:
                    row = table.add_row().cells
                    row[0].text = str(sb.get("harmonic_order", ""))
                    lo = sb.get("lower", {})
                    hi = sb.get("upper", {})
                    row[1].text = f"{lo.get('expected_hz', '')} Hz"
                    row[2].text = f"{hi.get('expected_hz', '')} Hz"
        elif fault_key == "bearing":
            doc.add_paragraph(
                f"{t('fault.frequency', lang)}: {fdata.get('defect_frequency_hz', 'N/A')} Hz"
            )


def _add_env_section(doc: Any, stats: dict[str, Any], lang: str) -> None:
    if not stats:
        return
    doc.add_heading(t("report.title.envelope_stats", lang), level=1)
    table = doc.add_table(rows=1, cols=2)
    table.style = "Light Grid Accent 1"
    hdr = table.rows[0].cells
    hdr[0].text = t("doc.parameter", lang)
    hdr[1].text = t("doc.value", lang)
    fields = [
        (t("env.rms", lang), stats.get("rms", "")),
        (t("env.kurtosis", lang), stats.get("kurtosis", "")),
        (t("env.skewness", lang), stats.get("skewness", "")),
        (t("env.crest_factor", lang), stats.get("crest_factor", "")),
    ]
    for label, val in fields:
        row = table.add_row().cells
        row[0].text = str(label)
        row[1].text = str(val)


def _add_band_section(doc: Any, band: dict[str, Any], lang: str) -> None:
    if not band:
        return
    doc.add_heading(t("report.title.band_energy", lang), level=1)
    table = doc.add_table(rows=1, cols=2)
    table.style = "Light Grid Accent 1"
    hdr = table.rows[0].cells
    hdr[0].text = t("doc.parameter", lang)
    hdr[1].text = t("doc.value", lang)
    fields = [
        (t("band.centre_freq", lang), band.get("centre_freq_hz", "")),
        (t("band.bandwidth", lang), band.get("bandwidth_hz", "")),
        (t("band.energy", lang), band.get("band_energy", "")),
    ]
    for label, val in fields:
        row = table.add_row().cells
        row[0].text = str(label)
        row[1].text = str(val)