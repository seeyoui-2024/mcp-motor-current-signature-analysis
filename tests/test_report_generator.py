"""Tests for the HTML report generation system."""

from __future__ import annotations

import json
import re

import numpy as np
import pytest

from mcp_server_mcsa.analysis.test_signal import generate_test_signal
from mcp_server_mcsa.html_templates import (
    create_diagnostic_report,
    create_envelope_report,
    create_spectrum_report,
)
from mcp_server_mcsa.report_generator import (
    REPORTS_DIR,
    list_reports,
    save_diagnostic_report,
    save_envelope_report,
    save_spectrum_report,
)
from mcp_server_mcsa.server import _run_diagnosis_pipeline


@pytest.fixture
def brb_report():
    """Full diagnostic pipeline result on a signal with injected BRB fault."""
    r = generate_test_signal(
        duration_s=4.0,
        fs_sample=5000.0,
        supply_freq_hz=50.0,
        poles=4,
        rotor_speed_rpm=1470.0,
        noise_std=0.01,
        faults=["brb", "eccentricity", "bearing"],
        fault_severity=0.03,
    )
    x = np.asarray(r["signal"], dtype=np.float64)
    fs = r["sampling_freq_hz"]
    return _run_diagnosis_pipeline(
        x, fs,
        supply_freq_hz=50.0,
        poles=4,
        rotor_speed_rpm=1470.0,
        bearing_defect_freq_hz=6.0,
        tolerance_hz=0.5,
        language="en",
        include_spectrum=True,
        signal_id="sig_test",
    )


def _extract_metadata(html: str) -> dict:
    m = re.search(
        r'<script type="application/json" id="report-metadata">(.*?)</script>',
        html,
        re.S,
    )
    assert m is not None, "report-metadata block missing"
    return json.loads(m.group(1).replace("<\\/", "</"))


class TestCreateDiagnosticReport:
    def test_pages_render_in_both_languages(self, brb_report):
        for lang in ("en", "zh"):
            html = create_diagnostic_report(brb_report, language=lang)  # type: ignore[arg-type]
            assert f'<html lang="{lang}">' in html
            assert 'switchLanguage' in html
            assert 'spectrum-chart' in html
            assert '<div class="language-toggle">' in html

    def test_initial_language_active_button(self, brb_report):
        en = create_diagnostic_report(brb_report, language="en")  # type: ignore[arg-type]
        zh = create_diagnostic_report(brb_report, language="zh")  # type: ignore[arg-type]
        assert 'lang-btn active" onclick="switchLanguage(\'en\'' in en
        assert 'lang-btn active" onclick="switchLanguage(\'zh\'' in zh

    def test_translations_embed_as_valid_json(self, brb_report):
        html = create_diagnostic_report(brb_report, language="en")  # type: ignore[arg-type]
        m = re.search(r"var translations = (\{.*?\});", html, re.S)
        assert m is not None, "translations dict missing"
        data = json.loads(m.group(1).replace("<\\/", "</"))
        assert "en" in data and "zh" in data
        assert data["en"]["report_title"] == "MCSA Diagnostic Report"
        assert data["zh"]["report_title"] == "MCSA 诊断报告"

    def test_metadata_block_accepts_custom_metadata(self, brb_report):
        html = create_diagnostic_report(
            brb_report, metadata={"signal_id": "sig_abc", "report_type": "x"}  # type: ignore[arg-type]
        )
        meta = _extract_metadata(html)
        assert meta["signal_id"] == "sig_abc"
        assert meta["report_type"] == "x"

    def test_bearing_missing_severity_renders_na(self, brb_report):
        html = create_diagnostic_report(brb_report, language="en")  # type: ignore[arg-type]
        assert "badge-info" in html  # neutral badge for the bearing card

    def test_no_spectrum_omits_chart(self, brb_report):
        report = {k: v for k, v in brb_report.items() if k != "spectrum"}
        html = create_diagnostic_report(report, language="en")  # type: ignore[arg-type]
        assert 'id="spectrum-chart"' not in html

    def test_full_content_is_toggleable(self, brb_report):
        """Every data-i18n key (incl. fault sections & assessment) resolves."""
        html = create_diagnostic_report(brb_report, language="zh")  # type: ignore[arg-type]
        m = re.search(r"var translations = (\{.*?\});", html, re.S)
        assert m is not None
        data = json.loads(m.group(1).replace("<\\/", "</"))
        keys = set(re.findall(r'data-i18n="([^"]+)"', html))
        assert any(k.startswith("fault_type.") for k in keys)
        assert any(k.startswith("detection_status.") for k in keys)
        assert any(k.startswith("assessment.") for k in keys)
        missing = sorted(k for k in keys if k not in data["en"] or k not in data["zh"])
        assert missing == [], f"data-i18n keys missing from translations: {missing}"


@pytest.fixture
def spectrum_arrays():
    freqs = [float(i) for i in range(100)]
    amps = [1.0 / (1 + i) for i in range(100)]
    peaks = [{"frequency_hz": 2.0, "amplitude": 0.5, "prominence": 0.3}]
    signal_info = {"n_samples": 1000, "sampling_freq_hz": 500, "duration_s": 2.0}
    return freqs, amps, peaks, signal_info


class TestSpectrumAndEnvelopeReports:
    def test_spectrum_report_bilingual(self, spectrum_arrays):
        freqs, amps, peaks, info = spectrum_arrays
        for lang in ("en", "zh"):
            html = create_spectrum_report(freqs, amps, peaks, info, language=lang)  # type: ignore[arg-type]
            assert f'<html lang="{lang}">' in html
            assert 'spectrum-chart' in html
            assert "Plotly.newPlot('spectrum-chart'" in html
            assert 'switchLanguage' in html

    def test_envelope_report_bilingual(self, spectrum_arrays):
        freqs, amps, _, info = spectrum_arrays
        stats = {"kurtosis": 3.5, "skewness": 0.1, "crest_factor": 4.2, "rms": 0.01, "peak": 0.05}
        for lang in ("en", "zh"):
            html = create_envelope_report(freqs, amps, stats, info, language=lang)  # type: ignore[arg-type]
            assert f'<html lang="{lang}">' in html
            assert 'spectrum-chart' in html
            assert 'Kurtosis' in html or '峰度' in html

    def test_save_spectrum_report(self, spectrum_arrays, tmp_path):
        freqs, amps, peaks, info = spectrum_arrays
        saved = save_spectrum_report(
            freqs, amps, peaks, info, label="case", language="en", directory=tmp_path
        )
        assert saved["report_type"] == "mcsa_spectrum"
        assert (tmp_path / saved["file_name"]).exists()

    def test_save_envelope_report(self, spectrum_arrays, tmp_path):
        freqs, amps, _, info = spectrum_arrays
        stats = {"kurtosis": 3.5, "skewness": 0.1}
        saved = save_envelope_report(
            freqs, amps, stats, info, label="case", language="zh", directory=tmp_path
        )
        assert saved["report_type"] == "mcsa_envelope"
        assert (tmp_path / saved["file_name"]).exists()

    def test_spectrum_report_missing_peaks(self, spectrum_arrays):
        freqs, amps, _, info = spectrum_arrays
        html = create_spectrum_report(freqs, amps, [], info, language="en")  # type: ignore[arg-type]
        assert '</table>' not in html  # no peaks → no table
        assert 'spectrum-chart' in html

    def test_reports_share_base_template_footer(self, spectrum_arrays, tmp_path):
        freqs, amps, peaks, info = spectrum_arrays
        html = create_spectrum_report(freqs, amps, peaks, info, language="zh")  # type: ignore[arg-type]
        assert 'MCSA 诊断报告' in html
        assert 'data-i18n="report.generated_by"' in html
        assert 'data-i18n="report.server_name"' in html

    def test_content_labels_are_toggleable(self, spectrum_arrays):
        """Every data-i18n key must resolve in the embedded translations dict."""
        freqs, amps, peaks, info = spectrum_arrays
        html = create_spectrum_report(freqs, amps, peaks, info, language="en")  # type: ignore[arg-type]
        m = re.search(r"var translations = (\{.*?\});", html, re.S)
        assert m is not None
        data = json.loads(m.group(1).replace("<\\/", "</"))
        keys = set(re.findall(r'data-i18n="([^"]+)"', html))
        assert len(keys) >= 10
        missing = sorted(k for k in keys if k not in data["en"] or k not in data["zh"])
        assert missing == [], f"data-i18n keys missing from translations: {missing}"


class TestSaveDiagnosticReport:
    def test_saves_file_and_returns_metadata(self, brb_report, tmp_path):
        saved = save_diagnostic_report(
            brb_report,
            label="case_1",
            metadata={"motor_id": "M1"},
            language="en",
            directory=tmp_path,
        )
        assert saved["file_path"].endswith(".html")
        assert (tmp_path / saved["file_name"]).exists()
        assert saved["report_type"] == "mcsa_full_diagnostic"
        assert saved["file_size_kb"] > 0
        assert saved["metadata"]["motor_id"] == "M1"
        # Unique names: a second run never overwrites
        saved2 = save_diagnostic_report(
            brb_report, label="case_1", language="en", directory=tmp_path
        )
        assert saved2["file_name"] != saved["file_name"]

    def test_saved_file_is_utf8_and_self_contained(self, brb_report, tmp_path):
        save_diagnostic_report(brb_report, label="case_2", language="zh", directory=tmp_path)
        (html_file,) = tmp_path.glob("mcsa_diagnostic_case_2_*.html")
        content = html_file.read_text(encoding="utf-8")
        assert "\ufffd" not in content
        assert "MCSA 诊断报告" in content
        assert 'src="https://cdn.plot.ly/' in content
        _extract_metadata(content)


class TestListReports:
    def test_lists_saved_reports(self, brb_report, tmp_path):
        save_diagnostic_report(brb_report, label="monitor", language="en", directory=tmp_path)
        reports = list_reports(tmp_path)
        assert any(r["file_name"].startswith("mcsa_diagnostic_monitor_") for r in reports)
        assert all(r["file_size_kb"] > 0 for r in reports)

    def test_defaults_to_reports_dir(self):
        # REPORTS_DIR constant exists and is a valid path.
        assert REPORTS_DIR.is_dir()
