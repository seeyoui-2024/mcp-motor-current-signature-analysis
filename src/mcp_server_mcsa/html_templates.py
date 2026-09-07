"""Professional HTML report templates for MCSA diagnostics.

Self-contained, responsive HTML templates with inline CSS and Plotly.js
CDN for interactive spectrum charts.  All user-facing text is bilingual
(English/Chinese) with a client-side language toggle that switches the
entire report content (section titles, info labels, table headers, fault
analysis, assessment) via ``data-i18n`` attributes.
"""

from __future__ import annotations

import html as _html
import json
from typing import Any

from mcp_server_mcsa.i18n import (
    TRANSLATIONS,
    Language,
    get_fault_type_name,
    get_severity_label,
    get_text,
)

# ---------------------------------------------------------------------------
# Client-side translation dictionary (for the in-page language toggle)
# ---------------------------------------------------------------------------

# UI-only keys referenced by the page chrome / charts that are not part of
# the server-side i18n vocabulary.
_UI_TRANSLATIONS = {
    "report_title": {"en": "MCSA Diagnostic Report", "zh": "MCSA 诊断报告"},
    "subtitle": {"en": "Motor Current Signature Analysis", "zh": "电机电流特征分析"},
    "spectrum_chart": {"en": "Current Spectrum (Zoom to inspect)", "zh": "电流频谱（缩放查看）"},
    "tagline": {"en": "Professional motor current signature analysis", "zh": "专业电机电流特征分析"},
    "frequency_hz": {"en": "Frequency (Hz)", "zh": "频率 (Hz)"},
    "magnitude": {"en": "Amplitude", "zh": "幅值"},
}


def _build_js_translations() -> dict[str, dict[str, str]]:
    """Derive the client-side dictionary from the server TRANSLATIONS table.

    Keeping a single source of truth (``i18n.TRANSLATIONS``) guarantees the
    in-page language toggle can refresh every rendered label.
    """
    js = {"en": {}, "zh": {}}
    for key, pair in TRANSLATIONS.items():
        js["en"][key] = pair.get("en", key)
        js["zh"][key] = pair.get("zh", key)
    for key, pair in _UI_TRANSLATIONS.items():
        js["en"][key] = pair["en"]
        js["zh"][key] = pair["zh"]
    return js


_JS_TRANSLATIONS = _build_js_translations()
_JS_TRANSLATIONS_JSON = json.dumps(_JS_TRANSLATIONS).replace("</", "<\\/")


def _find_key(prefix: str, text: str) -> str | None:
    """Reverse-map a rendered label back to its i18n key, if unique.

    Matches against either language value so reports built from a pipeline
    that ran in English still resolve their keys when rendered in Chinese
    (and vice versa).
    """
    if not text:
        return None
    for key, pair in TRANSLATIONS.items():
        if key.startswith(prefix) and text in pair.values():
            return key
    return None


def get_severity_css_class(severity: str) -> str:
    """Map a severity label to a CSS badge class."""
    low = severity.lower()
    if low in ("healthy", "正常", "健康"):
        return "badge-success"
    if low in ("incipient", "初期"):
        return "badge-info"
    if low in ("moderate", "中度"):
        return "badge-warning"
    return "badge-danger"


def _severity_key(lang: Language) -> dict[str, str]:
    return {
        "healthy": get_severity_label("healthy", lang),
        "incipient": get_severity_label("incipient", lang),
        "moderate": get_severity_label("moderate", lang),
        "severe": get_severity_label("severe", lang),
    }


def _get_base_template(
    title: str,
    content: str,
    metadata: dict[str, Any] | None = None,
    language: Language = "en",
) -> str:
    """Base HTML document with professional styling and language toggle.

    Args:
        title: Report title (escaped into <title>).
        content: Main HTML content (trusted, already built).
        metadata: Optional metadata dict stored as JSON in a data block.
        language: Initial language ("en" or "zh").
    """
    safe_title = _html.escape(str(title))
    metadata_json = json.dumps(metadata or {}, indent=2, default=str).replace(
        "</", "<\\/"
    )
    t = get_text
    js_t = _JS_TRANSLATIONS[language]

    return f"""<!DOCTYPE html>
<html lang="{language}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="generator" content="MCSA MCP Server">
    <title>{safe_title}</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        :root {{
            --primary-color: #2c3e50;
            --secondary-color: #3498db;
            --success-color: #27ae60;
            --warning-color: #f39c12;
            --danger-color: #e74c3c;
            --background: #f8f9fa;
            --card-background: #ffffff;
            --text-primary: #2c3e50;
            --text-secondary: #7f8c8d;
            --border-color: #e0e0e0;
            --shadow: 0 2px 8px rgba(0,0,0,0.1);
            --shadow-hover: 0 4px 16px rgba(0,0,0,0.15);
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto,
                'Helvetica Neue', Arial, 'PingFang SC', 'Microsoft YaHei', sans-serif;
            background: var(--background);
            color: var(--text-primary);
            line-height: 1.6;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem 1rem;
            box-shadow: var(--shadow);
        }}
        .header-content {{ max-width: 1400px; margin: 0 auto; }}
        .header h1 {{ font-size: 2rem; font-weight: 600; margin-bottom: 0.5rem; }}
        .header .subtitle {{ opacity: 0.95; font-size: 1rem; }}
        .container {{ max-width: 1400px; margin: 2rem auto; padding: 0 1rem; }}
        .card {{
            background: var(--card-background);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: var(--shadow);
            transition: box-shadow 0.3s ease;
        }}
        .card:hover {{ box-shadow: var(--shadow-hover); }}
        .card-title {{
            font-size: 1.4rem;
            font-weight: 600;
            margin-bottom: 1rem;
            color: var(--text-primary);
            border-bottom: 2px solid var(--secondary-color);
            padding-bottom: 0.5rem;
        }}
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 1.5rem;
        }}
        .info-item {{
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 1rem;
            border-radius: 8px;
            border-left: 4px solid var(--secondary-color);
        }}
        .info-label {{
            font-size: 0.75rem;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 0.25rem;
            font-weight: 600;
        }}
        .info-value {{ font-size: 1.35rem; font-weight: 700; color: var(--text-primary); }}
        .chart-container {{
            background: var(--card-background);
            border-radius: 12px;
            padding: 1rem;
            margin-bottom: 1.5rem;
            box-shadow: var(--shadow);
        }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 0.5rem; }}
        th {{
            background: #f5f7fa;
            font-weight: 600;
            padding: 0.75rem;
            text-align: left;
            border-bottom: 2px solid var(--border-color);
        }}
        td {{
            padding: 0.75rem;
            border-bottom: 1px solid var(--border-color);
        }}
        td.numeric, th.numeric {{ font-family: 'SF Mono', Consolas, monospace; }}
        .badge {{
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 12px;
            font-size: 0.8125rem;
            font-weight: 600;
            text-transform: uppercase;
        }}
        .badge-success {{ background: var(--success-color); color: white; }}
        .badge-warning {{ background: var(--warning-color); color: white; }}
        .badge-danger {{ background: var(--danger-color); color: white; }}
        .badge-info {{ background: var(--secondary-color); color: white; }}
        .footer {{
            text-align: center;
            padding: 2rem 1rem;
            color: var(--text-secondary);
            border-top: 1px solid var(--border-color);
            margin-top: 3rem;
        }}
        .footer p {{ margin-bottom: 0.25rem; }}
        .language-toggle {{
            position: fixed;
            top: 1rem;
            right: 1rem;
            z-index: 1000;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 8px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.15);
            padding: 0.5rem;
            display: flex;
            gap: 0.25rem;
        }}
        .lang-btn {{
            padding: 0.5rem 1rem;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
            font-size: 0.875rem;
            transition: all 0.2s ease;
            background: transparent;
            color: var(--text-secondary);
        }}
        .lang-btn:hover {{ background: var(--background); }}
        .lang-btn.active {{ background: var(--secondary-color); color: white; }}
        .assessment-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: var(--shadow);
        }}
        .assessment-card .assessment-text {{ font-size: 1.15rem; font-weight: 500; }}
        @media (max-width: 768px) {{
            .header h1 {{ font-size: 1.5rem; }}
            .info-grid {{ grid-template-columns: 1fr; }}
        }}
        @media print {{
            .language-toggle {{ display: none; }}
            .card {{ page-break-inside: avoid; }}
        }}
    </style>
</head>
<body>
    <script type="application/json" id="report-metadata">
{metadata_json}
    </script>
    <div class="language-toggle">
        <button class="lang-btn {'active' if language == 'en' else ''}" onclick="switchLanguage('en', event)">English</button>
        <button class="lang-btn {'active' if language == 'zh' else ''}" onclick="switchLanguage('zh', event)">中文</button>
    </div>
    <div class="header">
        <div class="header-content">
            <h1 data-i18n="report_title">{js_t["report_title"]}</h1>
            <div class="subtitle" data-i18n="subtitle">{js_t["subtitle"]}</div>
        </div>
    </div>
    <div class="container">
        {content}
    </div>
    <div class="footer">
        <p><span data-i18n="report.generated_by">{t("report.generated_by", language)}</span> <strong data-i18n="report.server_name">{t("report.server_name", language)}</strong></p>
        <p style="font-size: 0.875rem; color: var(--text-secondary);" data-i18n="tagline">{js_t["tagline"]}</p>
    </div>
    <script>
        var translations = {_JS_TRANSLATIONS_JSON};
        var currentLang = {json.dumps(language)};

        function switchLanguage(lang, event) {{
            currentLang = lang;
            document.querySelectorAll('.lang-btn').forEach(function(btn) {{
                btn.classList.remove('active');
            }});
            if (event && event.target) event.target.classList.add('active');

            var t = translations[lang] || translations['en'];
            document.querySelectorAll('[data-i18n]').forEach(function(el) {{
                var key = el.getAttribute('data-i18n');
                if (t[key]) el.textContent = t[key];
            }});
            document.title = t['report_title'];

            // Rebuild badges that were rendered with data-severity-key
            document.querySelectorAll('.badge[data-severity-key]').forEach(function(el) {{
                var key = el.getAttribute('data-severity-key');
                if (t[key]) el.textContent = t[key];
            }});

            // Update Plotly figure text
            updatePlotlyCharts(lang);
        }}

        function updatePlotlyCharts(lang) {{
            var t = translations[lang] || translations['en'];
            var chart = document.getElementById('spectrum-chart');
            if (chart && chart.data) {{
                Plotly.relayout(chart, {{
                    'xaxis.title.text': t['frequency_hz'],
                    'yaxis.title.text': t['magnitude']
                }});
            }}
        }}
    </script>
</body>
</html>"""


def _build_info_grid(items: list[tuple[str, str, str]]) -> str:
    """Build the label/value info card grid.

    Each item is ``(i18n_key, label, value)`` — the i18n key drives the
    client-side language toggle while ``value`` may contain numeric/unit
    text that should not be re-translated.
    """
    cards = "\n".join(
        f"""        <div class="info-item">
            <div class="info-label" data-i18n="{_html.escape(key)}">{_html.escape(label)}</div>
            <div class="info-value">{value}</div>
        </div>"""
        for key, label, value in items
    )
    return f'<div class="info-grid">\n{cards}\n    </div>'


def _sideband_rows(sidebands: list[dict[str, Any]], lang: Language) -> str:
    """Render a sideband table body for a fault analysis section."""
    rows = []
    for sb in sidebands:
        for side, entry in (("↓", sb.get("lower", {})), ("↑", sb.get("upper", {}))):
            expected = entry.get("expected_hz")
            freq = entry.get("frequency_hz")
            found = entry.get("found", False)
            amp = entry.get("amplitude", 0.0)
            db = entry.get("db_relative")
            exp = (
                f"{expected:.3f}"
                if isinstance(expected, (int, float))
                else get_text("detail.na", lang)
            )
            fq = f"{freq:.3f}" if isinstance(freq, (int, float)) else "—"
            found_key = "detail.yes" if found else "detail.no"
            found_text = get_text(found_key, lang)
            rows.append(
                f"""            <tr>
            <td>{_html.escape(str(side))}</td>
            <td class="numeric">{exp}</td>
            <td class="numeric">{fq if found else '—'}</td>
            <td class="numeric">{amp:.6g}</td>
            <td class="numeric">{db:+.1f} dB</td>
            <td data-i18n="{found_key}">{found_text}</td>
            </tr>"""
            )
    return "\n".join(rows)


def _fault_section(
    key: str,
    result: dict[str, Any] | None,
    lang: Language,
) -> str:
    """Render a single fault-analysis card (or a muted "not computed" card)."""
    if result is None:
        return f"""    <div class="card">
        <h3 class="card-title"><span data-i18n="fault_type.{key}">{_html.escape(get_fault_type_name(key, lang))}</span></h3>
        <p style="color: var(--text-secondary);" data-i18n="report.not_computed">{get_text("report.not_computed", lang)}</p>
    </div>"""

    severity = str(result.get("severity", "") or "")
    display_severity = severity if severity else get_text("detail.na", lang)
    badge_class = get_severity_css_class(severity) if severity else "badge-info"
    ds = result.get("detection_status", {})
    detected = ds.get("detected", False)
    reason = str(ds.get("reason", ""))
    # Map rendered severity label back to its canonical key across both
    # languages so the badge/value re-translate on toggle regardless of the
    # language the pipeline ran in.
    sev_lookup = {}
    for _lang in ("en", "zh"):
        for canonical, label in _severity_key(_lang).items():
            sev_lookup[label] = canonical

    # Map rendered severity label back to its i18n key for the JS toggle.
    canonical = sev_lookup.get(severity) if severity else None
    severity_key = f"severity.{canonical}" if canonical else None

    rows = _sideband_rows(result.get("sidebands", []), lang)

    fault_type = str(result.get("fault_type", key))
    fault_key = _find_key("fault_type.", fault_type) or f"fault_type.{key}"
    fault_attr = f'data-i18n="{fault_key}"' if fault_key else ""

    reason_key = _find_key("detection_status.", reason)
    reason_attr = f'data-i18n="{reason_key}"' if reason_key else ""

    badge_attr = (
        f'data-severity-key="{severity_key}"' if severity_key else ""
    )

    severity_value_attr = (
        f'data-i18n="severity.{canonical}"' if canonical else ""
    )
    detected_key = "report.yes" if detected else "report.no"

    html = f"""    <div class="card">
        <h3 class="card-title"><span {fault_attr}>{_html.escape(fault_type)}</span>
            <span class="badge {badge_class}" {badge_attr}>{_html.escape(display_severity)}</span>
        </h3>
        <div class="info-grid">
            <div class="info-item">
                <div class="info-label" data-i18n="detail.severity">{_html.escape(get_text("detail.severity", lang))}</div>
                <div class="info-value" {severity_value_attr}>{_html.escape(display_severity)}</div>
            </div>
            <div class="info-item">
                <div class="info-label" data-i18n="detail.detected">{_html.escape(get_text("detail.detected", lang))}</div>
                <div class="info-value" data-i18n="{detected_key}">{get_text(detected_key, lang)}</div>
            </div>
            <div class="info-item">
                <div class="info-label" data-i18n="detail.reason">{_html.escape(get_text("detail.reason", lang))}</div>
                <div class="info-value" style="font-size: 1rem;" {reason_attr}>{_html.escape(reason)}</div>
            </div>
        </div>"""

    if rows:
        html += f"""        <table>
            <tr>
                <th data-i18n="detail.sidebands">{_html.escape(get_text("detail.sidebands", lang))}</th>
                <th data-i18n="detail.expected_hz">{_html.escape(get_text("detail.expected_hz", lang))}</th>
                <th data-i18n="detail.frequency_hz">{_html.escape(get_text("detail.frequency_hz", lang))}</th>
                <th data-i18n="detail.amplitude">{_html.escape(get_text("detail.amplitude", lang))}</th>
                <th data-i18n="detail.db_relative">{_html.escape(get_text("detail.db_relative", lang))}</th>
                <th data-i18n="detail.found">{_html.escape(get_text("detail.found", lang))}</th>
            </tr>
{rows}
        </table>"""

    html += "\n    </div>"
    return html


def _peaks_table(peaks: list[dict[str, Any]], lang: Language) -> str:
    """Render the top spectral peaks table."""
    rows = []
    for i, p in enumerate(peaks[:10], 1):
        freq = p.get("frequency_hz", 0.0)
        amp = p.get("amplitude", 0.0)
        prom = p.get("prominence", 0.0)
        rows.append(
            f"""        <tr>
            <td><strong>#{i}</strong></td>
            <td class="numeric">{freq:.3f}</td>
            <td class="numeric">{amp:.6g}</td>
            <td class="numeric">{prom:.6g}</td>
        </tr>"""
        )
    header = (
        "<tr>"
        f"<th data-i18n=\"report.rank\">{get_text('report.rank', lang)}</th>"
        f"<th data-i18n=\"detail.frequency_hz\">{get_text('detail.frequency_hz', lang)}</th>"
        f"<th data-i18n=\"detail.amplitude\">{get_text('detail.amplitude', lang)}</th>"
        f"<th data-i18n=\"report.prominence\">{get_text('report.prominence', lang)}</th>"
        "</tr>"
    )
    body = "\n".join(rows)
    return "<table>\n" + header + "\n" + body + "\n</table>"


def create_diagnostic_report(
    report_data: dict[str, Any],
    metadata: dict[str, Any] | None = None,
    language: Language = "en",
) -> str:
    """Create a complete bilingual MCSA diagnostic report as HTML.

    Args:
        report_data: The diagnostic report dict produced by
            ``run_full_diagnosis`` / ``diagnose_from_file``.
        metadata: Extra display metadata (signal id, file, generation time).
        language: Initial language ("en" or "zh").

    Returns:
        Complete standalone HTML document.
    """
    t = get_text
    js_t = _JS_TRANSLATIONS[language]

    # --- Title -----------------------------------------------------------------
    signal_id = str(report_data.get("signal_id") or (metadata or {}).get("signal_id") or "signal")
    title = f"{js_t['report_title']} — {_html.escape(signal_id)}"

    # --- Signal info cards ------------------------------------------------------
    sig = report_data.get("signal_info", {})
    info_items = [
        ("signal.n_samples", t("signal.n_samples", language), f'{int(sig.get("n_samples", 0)):,}'),
        ("signal.duration_s", t("signal.duration_s", language), f'{float(sig.get("duration_s", 0)):.3f} {t("unit.s", language)}'),
        ("signal.sampling_freq_hz", t("signal.sampling_freq_hz", language), f'{float(sig.get("sampling_freq_hz", 0)):,.0f} {t("unit.hz", language)}'),
        ("signal.freq_resolution_hz", t("signal.freq_resolution_hz", language), f'{float(sig.get("freq_resolution_hz", 0)):.6g} {t("unit.hz", language)}'),
    ]
    content = _build_info_grid(info_items)

    # --- Motor parameters --------------------------------------------------------
    mp = report_data.get("motor_parameters", {})
    if mp:
        mp_items = [
            ("motor_param.sync_speed", t("motor_param.sync_speed", language), f'{mp.get("sync_speed_rpm", "—")} {t("unit.rpm", language)}'),
            ("motor_param.rotor_speed", t("motor_param.rotor_speed", language), f'{mp.get("rotor_speed_rpm", "—")} {t("unit.rpm", language)}'),
            ("motor_param.slip", t("motor_param.slip", language), f'{mp.get("slip", "—"):.4%}' if isinstance(mp.get("slip"), (int, float)) else str(mp.get("slip", "—"))),
            ("motor_param.rotor_freq", t("motor_param.rotor_freq", language), f'{mp.get("rotor_freq_hz", "—")} {t("unit.hz", language)}'),
            ("motor_param.slip_freq", t("motor_param.slip_freq", language), f'{mp.get("slip_freq_hz", "—")} {t("unit.hz", language)}'),
        ]
        content += f"""    <div class="card">
        <h3 class="card-title"><span data-i18n="report.motor_parameters">{_html.escape(t("report.motor_parameters", language))}</span></h3>
        {_build_info_grid(mp_items)}
    </div>"""

    # --- Spectrum chart -----------------------------------------------------------
    spectrum = report_data.get("spectrum")
    if spectrum:
        freqs = [float(x) for x in spectrum["frequencies_hz"]]
        amps = [float(x) for x in spectrum["amplitudes"]]
        # Downsample to keep file size sensible (max ~5000 points)
        step = max(1, len(freqs) // 5000)
        freqs_d = freqs[::step]
        amps_d = amps[::step]
        content += f"""    <div class="chart-container">
        <div id="spectrum-chart"></div>
    </div>
    <script>
        var spectrumData = {{
            x: {json.dumps(freqs_d)},
            y: {json.dumps(amps_d)},
            type: 'scatter',
            mode: 'lines',
            name: translations[currentLang]['magnitude'],
            line: {{ color: '#667eea', width: 1.5 }},
            hovertemplate: '%{{x:.1f}} Hz<br>%{{y:.6g}}<extra></extra>'
        }};
        var spectrumLayout = {{
            title: {{
                text: translations[currentLang]['spectrum_chart'],
                font: {{ size: 18, color: '#2c3e50' }}
            }},
            xaxis: {{
                title: translations[currentLang]['frequency_hz'],
                gridcolor: '#eee'
            }},
            yaxis: {{
                title: translations[currentLang]['magnitude'],
                gridcolor: '#eee'
            }},
            showlegend: false,
            margin: {{ t: 60, b: 55, l: 60, r: 20 }},
            paper_bgcolor: '#ffffff',
            plot_bgcolor: '#ffffff'
        }};
        Plotly.newPlot('spectrum-chart', [spectrumData], spectrumLayout, {{ responsive: true }});
    </script>"""

    # --- Fault analysis -----------------------------------------------------------
    fa = report_data.get("fault_analysis", {})
    if fa:
        content += f"""    <div class="card">
        <h3 class="card-title"><span data-i18n="report.fault_analysis">{_html.escape(t("report.fault_analysis", language))}</span></h3>
    </div>"""
        for key in ("broken_rotor_bars", "eccentricity", "stator_inter_turn", "bearing"):
            content += _fault_section(key, fa.get(key), language) + "\n"

    # --- Top spectral peaks ---------------------------------------------------------
    peaks = report_data.get("top_spectral_peaks", [])
    if peaks:
        content += f"""    <div class="card">
        <h3 class="card-title"><span data-i18n="report.top_spectral_peaks">{_html.escape(t("report.top_spectral_peaks", language))}</span></h3>
        {_peaks_table(peaks, language)}
    </div>"""

    # --- Band energy ---------------------------------------------------------------
    be = report_data.get("band_energy_around_fundamental")
    if be:
        be_items = [
            ("band.centre_freq_hz", t("band.centre_freq_hz", language), f'{be.get("centre_freq_hz", "—")} {t("unit.hz", language)}'),
            ("band.band_energy", t("band.band_energy", language), f'{be.get("band_energy", "—"):.6g}'),
            ("band.band_low_hz", t("band.band_low_hz", language), f'{be.get("band_low_hz", "—")} {t("unit.hz", language)}'),
            ("band.band_high_hz", t("band.band_high_hz", language), f'{be.get("band_high_hz", "—")} {t("unit.hz", language)}'),
        ]
        content += f"""    <div class="card">
        <h3 class="card-title"><span data-i18n="report.band_energy">{_html.escape(t("report.band_energy", language))}</span></h3>
        {_build_info_grid(be_items)}
    </div>"""

    # --- Envelope statistics ---------------------------------------------------------
    env = report_data.get("envelope_statistics", {})
    if env:
        env_items = [
            ("env.kurtosis", t("env.kurtosis", language), f'{env.get("kurtosis", "—"):.4f}'),
            ("env.skewness", t("env.skewness", language), f'{env.get("skewness", "—"):.4f}'),
            ("env.crest_factor", t("env.crest_factor", language), f'{env.get("crest_factor", "—"):.4f}'),
            ("env.rms", t("env.rms", language), f'{env.get("rms", "—"):.6g}'),
        ]
        content += f"""    <div class="card">
        <h3 class="card-title"><span data-i18n="report.envelope_statistics">{_html.escape(t("report.envelope_statistics", language))}</span></h3>
        {_build_info_grid(env_items)}
    </div>"""

    # --- Summary / assessment ---------------------------------------------------------
    summary = report_data.get("summary", {})
    assessment = str(summary.get("overall_assessment", "") or "")
    if assessment:
        assessment_key = _find_key("assessment.", assessment)
        assessment_attr = f'data-i18n="{assessment_key}"' if assessment_key else ""
        content += f"""    <div class="assessment-card">
        <div class="info-label" data-i18n="report.summary" style="color: rgba(255,255,255,0.85); text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600; font-size: 0.8125rem; margin-bottom: 0.5rem;">{_html.escape(t("report.summary", language))}</div>
        <div class="assessment-text" {assessment_attr}>{_html.escape(assessment)}</div>
    </div>"""

    return _get_base_template(title, content, metadata=metadata, language=language)


def create_spectrum_report(
    frequencies_hz: list[float],
    amplitudes: list[float],
    peaks: list[dict[str, Any]],
    signal_info: dict[str, Any],
    metadata: dict[str, Any] | None = None,
    language: Language = "en",
) -> str:
    """Create a bilingual frequency-spectrum analysis report.

    Shows the amplitude spectrum on an interactive Plotly chart plus the
    top detected peaks.

    Args:
        frequencies_hz: Spectrum frequency axis (Hz).
        amplitudes: Spectrum amplitude values.
        peaks: Detected peaks (dicts with frequency_hz/amplitude/prominence).
        signal_info: Dict with n_samples / sampling_freq_hz / duration_s.
        metadata: Report provenance metadata.
        language: Initial language ("en" or "zh").
    """
    t = get_text
    js_t = _JS_TRANSLATIONS[language]

    label = str((metadata or {}).get("signal_id") or "spectrum")
    title = f"{js_t['report_title']} — Spectrum {_html.escape(label)}"

    sig = signal_info or {}
    info_items = [
        ("signal.n_samples", t("signal.n_samples", language), f'{int(sig.get("n_samples", 0)):,}'),
        ("signal.duration_s", t("signal.duration_s", language), f'{float(sig.get("duration_s", 0)):.3f} {t("unit.s", language)}'),
        ("signal.sampling_freq_hz", t("signal.sampling_freq_hz", language), f'{float(sig.get("sampling_freq_hz", 0)):,.0f} {t("unit.hz", language)}'),
        ("signal.freq_resolution_hz", t("signal.freq_resolution_hz", language), f'{float(sig.get("freq_resolution_hz", 0)):.6g} {t("unit.hz", language)}'),
    ]
    content = _build_info_grid(info_items)

    # Downsample for a reasonable file size (~4000 points max).
    n = len(frequencies_hz)
    step = max(1, n // 4000)
    freqs_d = frequencies_hz[::step]
    amps_d = amplitudes[::step]

    content += f"""    <div class="chart-container">
        <div id="spectrum-chart"></div>
    </div>
    <script>
        var spectrumData = {{
            x: {json.dumps(freqs_d)},
            y: {json.dumps(amps_d)},
            type: 'scatter',
            mode: 'lines',
            name: translations[currentLang]['magnitude'],
            line: {{ color: '#667eea', width: 1.5 }},
            hovertemplate: '%{{x:.1f}} Hz<br>%{{y:.6g}}<extra></extra>'
        }};
        var spectrumLayout = {{
            title: {{
                text: translations[currentLang]['spectrum_chart'],
                font: {{ size: 18, color: '#2c3e50' }}
            }},
            xaxis: {{ title: translations[currentLang]['frequency_hz'], gridcolor: '#eee' }},
            yaxis: {{ title: translations[currentLang]['magnitude'], gridcolor: '#eee' }},
            showlegend: false,
            margin: {{ t: 60, b: 55, l: 60, r: 20 }},
            paper_bgcolor: '#ffffff',
            plot_bgcolor: '#ffffff'
        }};
        Plotly.newPlot('spectrum-chart', [spectrumData], spectrumLayout, {{ responsive: true }});
    </script>
"""

    if peaks:
        content += f"""    <div class="card">
        <h3 class="card-title"><span data-i18n="report.top_spectral_peaks">{_html.escape(t("report.top_spectral_peaks", language))}</span></h3>
        {_peaks_table(peaks, language)}
    </div>"""

    return _get_base_template(title, content, metadata=metadata, language=language)


def create_envelope_report(
    frequencies_hz: list[float],
    amplitudes: list[float],
    env_stats: dict[str, Any],
    signal_info: dict[str, Any],
    metadata: dict[str, Any] | None = None,
    language: Language = "en",
) -> str:
    """Create a bilingual envelope-analysis report.

    Shows the envelope spectrum on an interactive Plotly chart plus the
    envelope statistical indicators (kurtosis, crest factor, …).

    Args:
        frequencies_hz: Envelope spectrum frequency axis (Hz).
        amplitudes: Envelope spectrum amplitude values.
        env_stats: Dict with rms/peak/crest_factor/kurtosis/skewness.
        signal_info: Dict with n_samples / sampling_freq_hz / duration_s.
        metadata: Report provenance metadata.
        language: Initial language ("en" or "zh").
    """
    t = get_text
    js_t = _JS_TRANSLATIONS[language]

    label = str((metadata or {}).get("signal_id") or "envelope")
    title = f"{js_t['report_title']} — Envelope {_html.escape(label)}"

    sig = signal_info or {}
    info_items = [
        ("signal.n_samples", t("signal.n_samples", language), f'{int(sig.get("n_samples", 0)):,}'),
        ("signal.duration_s", t("signal.duration_s", language), f'{float(sig.get("duration_s", 0)):.3f} {t("unit.s", language)}'),
        ("signal.sampling_freq_hz", t("signal.sampling_freq_hz", language), f'{float(sig.get("sampling_freq_hz", 0)):,.0f} {t("unit.hz", language)}'),
    ]
    content = _build_info_grid(info_items)

    n = len(frequencies_hz)
    step = max(1, n // 4000)
    freqs_d = frequencies_hz[::step]
    amps_d = amplitudes[::step]

    content += f"""    <div class="chart-container">
        <div id="spectrum-chart"></div>
    </div>
    <script>
        var spectrumData = {{
            x: {json.dumps(freqs_d)},
            y: {json.dumps(amps_d)},
            type: 'scatter',
            mode: 'lines',
            name: translations[currentLang]['magnitude'],
            line: {{ color: '#667eea', width: 1.5 }},
            hovertemplate: '%{{x:.1f}} Hz<br>%{{y:.6g}}<extra></extra>'
        }};
        var spectrumLayout = {{
            title: {{
                text: translations[currentLang]['spectrum_chart'],
                font: {{ size: 18, color: '#2c3e50' }}
            }},
            xaxis: {{ title: translations[currentLang]['frequency_hz'], gridcolor: '#eee' }},
            yaxis: {{ title: translations[currentLang]['magnitude'], gridcolor: '#eee' }},
            showlegend: false,
            margin: {{ t: 60, b: 55, l: 60, r: 20 }},
            paper_bgcolor: '#ffffff',
            plot_bgcolor: '#ffffff'
        }};
        Plotly.newPlot('spectrum-chart', [spectrumData], spectrumLayout, {{ responsive: true }});
    </script>
"""

    if env_stats:
        env_items = []
        for key, fmt in (
            ("kurtosis", ".4f"),
            ("skewness", ".4f"),
            ("crest_factor", ".4f"),
            ("rms", ".6g"),
            ("peak", ".6g"),
        ):
            val = env_stats.get(key)
            if isinstance(val, (int, float)):
                env_items.append((f"env.{key}", t(f"env.{key}", language), format(float(val), fmt)))
        if env_items:
            content += f"""    <div class="card">
        <h3 class="card-title"><span data-i18n="report.envelope_statistics">{_html.escape(t("report.envelope_statistics", language))}</span></h3>
        {_build_info_grid(env_items)}
    </div>"""

    return _get_base_template(title, content, metadata=metadata, language=language)
