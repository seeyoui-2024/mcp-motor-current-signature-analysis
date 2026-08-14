"""HTML report generation for MCSA diagnostic reports."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from mcp_server_mcsa.i18n import t
from mcp_server_mcsa.report import (
    _FAULT_KEYS,
    _fault_label,
    _get_recommendations,
    _overall_class,
    _severity_color,
    _severity_label,
    _translate_assessment,
)


def _generate_html_report(data: dict[str, Any], lang: str) -> str:
    report_id = f"mcsa_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    motor_params = data.get("motor_parameters", {})
    signal_info = data.get("signal_info", {})
    peaks = data.get("top_spectral_peaks", [])
    fault_analysis = data.get("fault_analysis", {})
    band_energy = data.get("band_energy_around_fundamental", {})
    envelope_stats = data.get("envelope_statistics", {})
    summary = data.get("summary", {})
    source_file = data.get("source_file", "")

    motor_rows = _build_motor_rows(motor_params, lang)
    signal_rows = _build_signal_rows(signal_info, source_file, lang)
    peaks_svg = _build_peaks_svg(peaks)
    fault_cards = _build_fault_cards(fault_analysis, lang)
    env_rows = _build_env_rows(envelope_stats, lang)
    band_rows = _build_band_rows(band_energy, lang)

    overall = summary.get("overall_assessment", "")
    if lang == "zh-CN":
        overall = _translate_assessment(overall, lang)

    recs = _get_recommendations(summary, lang)
    recs_html = "\n".join(f'        <li>{r}</li>' for r in recs)

    return f'''<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{t("report.title.mcsa_diagnostic", lang)} — {report_id}</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f5f5f5; color: #333; line-height: 1.6; }}
    .container {{ max-width: 1000px; margin: 0 auto; padding: 20px; }}
    .header {{ background: linear-gradient(135deg, #1a237e, #0d47a1); color: white; padding: 30px; border-radius: 12px; margin-bottom: 24px; position: relative; }}
    .header h1 {{ font-size: 24px; margin-bottom: 8px; }}
    .header .meta {{ font-size: 13px; opacity: 0.9; }}
    .lang-switch {{ position: absolute; top: 20px; right: 20px; display: flex; gap: 8px; }}
    .lang-switch button {{ background: rgba(255,255,255,0.2); border: 1px solid rgba(255,255,255,0.4); color: white; padding: 6px 14px; border-radius: 6px; cursor: pointer; font-size: 12px; transition: all 0.2s; }}
    .lang-switch button:hover {{ background: rgba(255,255,255,0.35); }}
    .lang-switch button.active {{ background: white; color: #1a237e; }}
    .section {{ background: white; border-radius: 10px; padding: 24px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }}
    .section h2 {{ font-size: 18px; color: #1a237e; margin-bottom: 16px; padding-bottom: 10px; border-bottom: 2px solid #e3f2fd; }}
    table {{ width: 100%; border-collapse: collapse; }}
    th, td {{ padding: 10px 14px; text-align: left; border-bottom: 1px solid #eee; }}
    th {{ background: #f8f9fa; font-weight: 600; color: #555; font-size: 13px; }}
    td {{ font-size: 14px; }}
    .fault-card {{ background: #f8f9fa; border-radius: 8px; padding: 16px; margin-bottom: 14px; }}
    .fault-card h3 {{ font-size: 16px; color: #333; margin-bottom: 10px; }}
    .severity-badge {{ display: inline-block; padding: 4px 14px; border-radius: 20px; color: white; font-weight: 600; font-size: 13px; margin-bottom: 10px; }}
    .fault-card p {{ margin: 6px 0; font-size: 14px; }}
    .fault-card .note {{ font-style: italic; color: #888; }}
    .overall {{ background: linear-gradient(135deg, #28a745, #20c997); color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
    .overall.warning {{ background: linear-gradient(135deg, #fd7e14, #ffc107); }}
    .overall.critical {{ background: linear-gradient(135deg, #dc3545, #c82333); }}
    .overall h2 {{ color: white; border: none; margin-bottom: 10px; }}
    .rec-list {{ list-style: none; padding: 0; }}
    .rec-list li {{ padding: 12px 16px; background: #f0f4ff; margin-bottom: 8px; border-radius: 6px; border-left: 3px solid #1a237e; }}
    svg {{ display: block; margin: 10px 0; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <div class="lang-switch">
        <button onclick="switchLang('en')" id="btn-en" class="active">EN</button>
        <button onclick="switchLang('zh-CN')" id="btn-zh">中文</button>
      </div>
      <h1 data-i18n="report.title.mcsa_diagnostic">{t("report.title.mcsa_diagnostic", lang)}</h1>
      <div class="meta">
        <span data-i18n="ui.report_id">{t("ui.report_id", lang)}</span>: {report_id} |
        <span data-i18n="ui.generated">{t("ui.generated", lang)}</span>: {generated_at}
      </div>
    </div>

    <div class="section">
      <h2 data-i18n="report.title.motor_params">{t("report.title.motor_params", lang)}</h2>
      <table>
        <thead><tr><th data-i18n="doc.parameter">{t("doc.parameter", lang)}</th><th data-i18n="doc.value">{t("doc.value", lang)}</th></tr></thead>
        <tbody>
{motor_rows}
        </tbody>
      </table>
    </div>

    <div class="section">
      <h2 data-i18n="report.title.signal_info">{t("report.title.signal_info", lang)}</h2>
      <table>
        <thead><tr><th data-i18n="doc.parameter">{t("doc.parameter", lang)}</th><th data-i18n="doc.value">{t("doc.value", lang)}</th></tr></thead>
        <tbody>
{signal_rows}
        </tbody>
      </table>
    </div>

    <div class="section">
      <h2 data-i18n="report.title.spectral_peaks">{t("report.title.spectral_peaks", lang)}</h2>
{peaks_svg}
    </div>

    <div class="section">
      <h2 data-i18n="report.title.fault_analysis">{t("report.title.fault_analysis", lang)}</h2>
{fault_cards}
    </div>

    <div class="section">
      <h2 data-i18n="report.title.envelope_stats">{t("report.title.envelope_stats", lang)}</h2>
      <table>
        <thead><tr><th data-i18n="doc.parameter">{t("doc.parameter", lang)}</th><th data-i18n="doc.value">{t("doc.value", lang)}</th></tr></thead>
        <tbody>
{env_rows}
        </tbody>
      </table>
    </div>

    <div class="section">
      <h2 data-i18n="report.title.band_energy">{t("report.title.band_energy", lang)}</h2>
      <table>
        <thead><tr><th data-i18n="doc.parameter">{t("doc.parameter", lang)}</th><th data-i18n="doc.value">{t("doc.value", lang)}</th></tr></thead>
        <tbody>
{band_rows}
        </tbody>
      </table>
    </div>

    <div class="overall {_overall_class(overall)}">
      <h2 data-i18n="report.title.overall_assessment">{t("report.title.overall_assessment", lang)}</h2>
      <p>{overall}</p>
    </div>

    <div class="section">
      <h2 data-i18n="report.title.recommendations">{t("report.title.recommendations", lang)}</h2>
      <ul class="rec-list">
{recs_html}
      </ul>
    </div>
  </div>

  <script>
    function switchLang(lang) {{
      document.documentElement.lang = lang;
      document.querySelectorAll('[data-i18n]').forEach(el => {{
        const key = el.getAttribute('data-i18n');
        if (window._i18n && window._i18n[key] && window._i18n[key][lang]) {{
          el.textContent = window._i18n[key][lang];
        }}
      }});
      document.getElementById('btn-en').classList.toggle('active', lang === 'en');
      document.getElementById('btn-zh').classList.toggle('active', lang === 'zh-CN');
    }}
    window.switchLang = switchLang;
  </script>
</body>
</html>'''


def _build_motor_rows(params: dict[str, Any], lang: str) -> str:
    rows = ""
    fields = [
        ("motor.supply_freq", params.get("supply_freq_hz", "")),
        ("motor.poles", params.get("poles", "")),
        ("motor.synchronous_speed", params.get("sync_speed_rpm", "")),
        ("motor.rotor_speed", params.get("rotor_speed_rpm", "")),
        ("motor.slip", params.get("slip", "")),
        ("motor.rotor_freq", params.get("rotor_freq_hz", "")),
        ("motor.slip_freq", params.get("slip_freq_hz", "")),
    ]
    for i18n_key, value in fields:
        rows += f'      <tr><td data-i18n="{i18n_key}">{t(i18n_key, lang)}</td><td>{value}</td></tr>\n'
    return rows


def _build_signal_rows(info: dict[str, Any], source_file: str, lang: str) -> str:
    rows = ""
    fields = [
        ("signal.n_samples", info.get("n_samples", "")),
        ("signal.sampling_freq", info.get("sampling_freq_hz", "")),
        ("signal.duration", info.get("duration_s", "")),
        ("signal.freq_resolution", info.get("freq_resolution_hz", "")),
    ]
    if source_file:
        fields.append(("signal.source_file", source_file))
    for i18n_key, value in fields:
        rows += f'      <tr><td data-i18n="{i18n_key}">{t(i18n_key, lang)}</td><td>{value}</td></tr>\n'
    return rows


def _build_peaks_svg(peaks: list[dict]) -> str:
    if not peaks:
        return ""
    max_amp = max((p.get("amplitude", p.get("prominence", 0)) for p in peaks), default=1.0)
    bar_width = max(30, min(60, 600 // max(len(peaks), 1)))
    chart_width = len(peaks) * (bar_width + 10) + 40
    chart_height = 200
    svg = f'    <svg viewBox="0 0 {chart_width} {chart_height}" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:{chart_width}px;height:auto;">\n'
    svg += f'      <rect width="{chart_width}" height="{chart_height}" fill="#1e1e2e"/>\n'
    for i, peak in enumerate(peaks[:10]):
        freq = peak.get("frequency_hz", peak.get("freq_hz", 0))
        amp = peak.get("amplitude", peak.get("prominence", 0))
        bar_h = (amp / max_amp) * (chart_height - 50) if max_amp > 0 else 0
        x = 20 + i * (bar_width + 10)
        y = chart_height - 30 - bar_h
        color = "#00bcd4" if i == 0 else "#7c4dff"
        svg += f'      <rect x="{x}" y="{y}" width="{bar_width}" height="{bar_h}" fill="{color}" rx="3"/>\n'
        svg += f'      <text x="{x + bar_width / 2}" y="{chart_height - 10}" text-anchor="middle" fill="#a0a0a0" font-size="10">{freq:.1f}Hz</text>\n'
        svg += f'      <text x="{x + bar_width / 2}" y="{y - 4}" text-anchor="middle" fill="#ffffff" font-size="10">{amp:.4f}</text>\n'
    svg += '    </svg>\n'
    return svg


def _build_fault_cards(fault_analysis: dict[str, Any], lang: str) -> str:
    cards = ""
    for fault_key, i18n_key in _FAULT_KEYS:
        fdata = fault_analysis.get(fault_key)
        if fdata is None:
            continue
        severity = fdata.get("severity", "")
        color = _severity_color(severity)
        label = _fault_label(fault_key, lang)
        sev_text = _severity_label(severity, lang)

        cards += f'    <div class="fault-card" style="border-left: 4px solid {color};">\n'
        cards += f'      <h3 data-i18n="{i18n_key}">{label}</h3>\n'
        cards += f'      <div class="severity-badge" style="background:{color};">{sev_text}</div>\n'

        if fault_key == "broken_rotor_bars":
            idx = fdata.get("combined_index_db", "N/A")
            thresh = fdata.get("thresholds_db", {}).get("severe", "N/A")
            detected = fdata.get("detection_status", {}).get("detected", False)
            cards += f'      <p><strong data-i18n="fault.index">{t("fault.index", lang)}</strong>: {idx} dB</p>\n'
            cards += f'      <p><strong data-i18n="fault.threshold_db">{t("fault.threshold_db", lang)}</strong>: {thresh} dB</p>\n'
            match_text = t("ui.match", lang) if detected else t("ui.no_match", lang)
            cards += f'      <p><strong>{match_text}</strong></p>\n'
        elif fault_key in ("eccentricity", "stator_inter_turn"):
            worst_db = fdata.get("worst_sideband_db", "N/A")
            cards += f'      <p><strong data-i18n="fault.index">{t("fault.index", lang)}</strong>: {worst_db} dB</p>\n'
            sidebands = fdata.get("sidebands", [])
            if sidebands:
                cards += '      <table><thead><tr>\n'
                cards += f'<th data-i18n="fault.harmonic_order">{t("fault.harmonic_order", lang)}</th>\n'
                cards += f'<th data-i18n="fault.lower">{t("fault.lower", lang)}</th>\n'
                cards += f'<th data-i18n="fault.upper">{t("fault.upper", lang)}</th>\n'
                cards += '</tr></thead><tbody>\n'
                for sb in sidebands:
                    order = sb.get("harmonic_order", "")
                    lo = sb.get("lower", {})
                    hi = sb.get("upper", {})
                    lo_f = lo.get("expected_hz", lo.get("frequency_hz", ""))
                    lo_db = lo.get("db_relative", "")
                    hi_f = hi.get("expected_hz", hi.get("frequency_hz", ""))
                    hi_db = hi.get("db_relative", "")
                    cards += f'        <tr><td>{order}</td><td>{lo_f} Hz ({lo_db} dB)</td><td>{hi_f} Hz ({hi_db} dB)</td></tr>\n'
                cards += '      </tbody></table>\n'
        elif fault_key == "bearing":
            defect_freq = fdata.get("defect_frequency_hz", "N/A")
            note = fdata.get("note", "")
            cards += f'      <p><strong data-i18n="fault.frequency">{t("fault.frequency", lang)}</strong>: {defect_freq} Hz</p>\n'
            if note:
                cards += f'      <p class="note">{note}</p>\n'
        cards += '    </div>\n'
    return cards


def _build_env_rows(stats: dict[str, Any], lang: str) -> str:
    if not stats:
        return ""
    rows = ""
    fields = [
        ("env.rms", stats.get("rms", "")),
        ("env.kurtosis", stats.get("kurtosis", "")),
        ("env.skewness", stats.get("skewness", "")),
        ("env.crest_factor", stats.get("crest_factor", "")),
        ("fault.amplitude", stats.get("peak", "")),
    ]
    for i18n_key, val in fields:
        if val:
            rows += f'      <tr><td data-i18n="{i18n_key}">{t(i18n_key, lang)}</td><td>{val}</td></tr>\n'
    return rows


def _build_band_rows(band: dict[str, Any], lang: str) -> str:
    if not band:
        return ""
    rows = ""
    fields = [
        ("band.centre_freq", band.get("centre_freq_hz", "")),
        ("band.bandwidth", band.get("bandwidth_hz", "")),
        ("band.energy", band.get("band_energy", "")),
    ]
    for i18n_key, val in fields:
        if val:
            rows += f'      <tr><td data-i18n="{i18n_key}">{t(i18n_key, lang)}</td><td>{val}</td></tr>\n'
    return rows