"""Internationalization (i18n) module for MCSA diagnostic reports.

Provides bilingual (English/Chinese) text translations for all user-facing
strings in diagnostic reports, fault detection results, and resources.
"""

from __future__ import annotations

from typing import Literal

Language = Literal["en", "zh"]

# ---------------------------------------------------------------------------
# Translation dictionaries
# ---------------------------------------------------------------------------

TRANSLATIONS: dict[str, dict[Language, str]] = {
    # Severity levels
    "severity.healthy": {"en": "healthy", "zh": "健康"},
    "severity.incipient": {"en": "incipient", "zh": "初期"},
    "severity.moderate": {"en": "moderate", "zh": "中度"},
    "severity.severe": {"en": "severe", "zh": "严重"},

    # Fault types
    "fault_type.broken_rotor_bars": {"en": "broken_rotor_bars", "zh": "转子断条"},
    "fault_type.eccentricity": {"en": "eccentricity", "zh": "偏心"},
    "fault_type.stator_inter_turn": {"en": "stator_inter_turn", "zh": "定子匝间短路"},
    "fault_type.bearing_bpfo": {"en": "bearing_bpfo", "zh": "轴承外圈故障 (BPFO)"},
    "fault_type.bearing_bpfi": {"en": "bearing_bpfi", "zh": "轴承内圈故障 (BPFI)"},
    "fault_type.bearing_bsf": {"en": "bearing_bsf", "zh": "轴承滚动体故障 (BSF)"},
    "fault_type.bearing_ftf": {"en": "bearing_ftf", "zh": "轴承保持架故障 (FTF)"},
    "fault_type.bearing": {"en": "bearing", "zh": "轴承"},

    # Detection status reasons
    "detection_status.detected": {"en": "detected", "zh": "已检出"},
    "detection_status.no_sideband_present": {"en": "no_sideband_present", "zh": "无侧边带"},
    "detection_status.frequency_out_of_range": {"en": "frequency_out_of_range", "zh": "频率超出范围"},
    "detection_status.frequency_resolution_insufficient": {"en": "frequency_resolution_insufficient", "zh": "频率分辨率不足"},
    "detection_status.sideband_inside_supply_main_lobe": {"en": "sideband_inside_supply_main_lobe", "zh": "侧边带落入供电基波主瓣内"},

    # Overall assessment
    "assessment.critical": {"en": "CRITICAL — One or more fault indicators at severe level. Immediate inspection recommended.", "zh": "严重 — 一项或多项故障指标达到严重级别，建议立即停机检查。"},
    "assessment.warning": {"en": "WARNING — Moderate fault indication detected. Schedule inspection.", "zh": "警告 — 检测到中度故障特征，请安排检查。"},
    "assessment.watch": {"en": "WATCH — Incipient fault signatures detected. Increase monitoring frequency.", "zh": "关注 — 检测到初期故障特征，建议增加监测频次。"},
    "assessment.normal": {"en": "NORMAL — No significant fault indicators detected.", "zh": "正常 — 未检测到显著故障指标。"},

    # Notes and descriptions
    "note.bearing_weak": {"en": "Bearing signatures in stator current are typically weak. Confirm with envelope analysis or vibration measurements.", "zh": "定子电流中的轴承特征通常较弱，建议结合包络谱或振动测量确认。"},
    "note.bearing_detection": {"en": "Bearing defect detection from current spectrum.", "zh": "基于电流频谱的轴承缺陷检测。"},
    "note.spectrum_stored": {"en": "Spectrum stored as '{id}'. Pass this spectrum_id to downstream tools.", "zh": "频谱已存储为 '{id}'，请将此 spectrum_id 传递给下游工具。"},
    "note.signal_stored": {"en": "Signal stored server-side as '{id}'. Pass this signal_id to analysis tools.", "zh": "信号已服务端存储为 '{id}'，请将此 signal_id 传递给分析工具。"},

    # Motor parameters
    "motor_param.sync_speed": {"en": "Synchronous speed", "zh": "同步转速"},
    "motor_param.rotor_speed": {"en": "Rotor speed", "zh": "转子转速"},
    "motor_param.slip": {"en": "Slip", "zh": "转差率"},
    "motor_param.rotor_freq": {"en": "Rotor frequency", "zh": "转子频率"},
    "motor_param.slip_freq": {"en": "Slip frequency", "zh": "转差频率"},

    # Report sections
    "report.motor_parameters": {"en": "Motor Parameters", "zh": "电机参数"},
    "report.signal_info": {"en": "Signal Information", "zh": "信号信息"},
    "report.top_spectral_peaks": {"en": "Top Spectral Peaks", "zh": "主要频谱峰值"},
    "report.fault_analysis": {"en": "Fault Analysis", "zh": "故障分析"},
    "report.band_energy": {"en": "Band Energy Around Fundamental", "zh": "基波周围带内能量"},
    "report.envelope_statistics": {"en": "Envelope Statistics", "zh": "包络统计指标"},
    "report.summary": {"en": "Summary", "zh": "综合评估"},

    # Fault analysis detail keys
    "detail.fault_type": {"en": "Fault Type", "zh": "故障类型"},
    "detail.fundamental": {"en": "Fundamental", "zh": "基波"},
    "detail.lower_sideband": {"en": "Lower Sideband", "zh": "下侧边带"},
    "detail.upper_sideband": {"en": "Upper Sideband", "zh": "上侧边带"},
    "detail.sidebands": {"en": "Sidebands", "zh": "侧边带组"},
    "detail.harmonic_order": {"en": "Harmonic Order", "zh": "谐波阶数"},
    "detail.combined_index_db": {"en": "Combined Index (dB)", "zh": "综合指数 (dB)"},
    "detail.worst_sideband_db": {"en": "Worst Sideband (dB)", "zh": "最差侧边带 (dB)"},
    "detail.severity": {"en": "Severity", "zh": "严重度"},
    "detail.thresholds_db": {"en": "Thresholds (dB)", "zh": "阈值 (dB)"},
    "detail.detection_status": {"en": "Detection Status", "zh": "检测状态"},
    "detail.detected": {"en": "Detected", "zh": "是否检出"},
    "detail.reason": {"en": "Reason", "zh": "原因"},
    "detail.fft_bin_width_hz": {"en": "FFT Bin Width (Hz)", "zh": "FFT 分辨率 (Hz)"},
    "detail.tolerance_hz": {"en": "Tolerance (Hz)", "zh": "容差 (Hz)"},
    "detail.min_bin_width_for_tolerance_hz": {"en": "Min Bin Width for Tolerance (Hz)", "zh": "容差所需最小分辨率 (Hz)"},
    "detail.defect_frequency_hz": {"en": "Defect Frequency (Hz)", "zh": "缺陷频率 (Hz)"},
    "detail.expected_hz": {"en": "Expected (Hz)", "zh": "理论值 (Hz)"},
    "detail.frequency_hz": {"en": "Frequency (Hz)", "zh": "频率 (Hz)"},
    "detail.amplitude": {"en": "Amplitude", "zh": "幅值"},
    "detail.db_relative": {"en": "dB Relative to Fundamental", "zh": "相对基波 (dB)"},
    "detail.found": {"en": "Found", "zh": "是否找到"},

    # Band energy
    "band.centre_freq_hz": {"en": "Centre Frequency (Hz)", "zh": "中心频率 (Hz)"},
    "band.bandwidth_hz": {"en": "Bandwidth (Hz)", "zh": "带宽 (Hz)"},
    "band.band_low_hz": {"en": "Band Low (Hz)", "zh": "带低限 (Hz)"},
    "band.band_high_hz": {"en": "Band High (Hz)", "zh": "带高限 (Hz)"},
    "band.band_energy": {"en": "Band Energy", "zh": "带内能量"},

    # Envelope statistics
    "env.rms": {"en": "RMS", "zh": "有效值"},
    "env.peak": {"en": "Peak", "zh": "峰值"},
    "env.crest_factor": {"en": "Crest Factor", "zh": "峰值因子"},
    "env.kurtosis": {"en": "Kurtosis", "zh": "峰度"},
    "env.skewness": {"en": "Skewness", "zh": "偏度"},

    # Signal info
    "signal.n_samples": {"en": "Number of Samples", "zh": "采样点数"},
    "signal.duration_s": {"en": "Duration (s)", "zh": "时长 (s)"},
    "signal.sampling_freq_hz": {"en": "Sampling Frequency (Hz)", "zh": "采样频率 (Hz)"},
    "signal.freq_resolution_hz": {"en": "Frequency Resolution (Hz)", "zh": "频率分辨率 (Hz)"},

    # Resource: fault signatures reference
    "resource.title": {"en": "MCSA Fault Signature Reference", "zh": "MCSA 故障特征参考表"},
    "resource.brb.title": {"en": "Broken Rotor Bars (BRB)", "zh": "转子断条 (BRB)"},
    "resource.brb.signature": {"en": "Sidebands at (1 ± 2s)·f_s around the supply fundamental", "zh": "在供电基波周围出现 (1 ± 2s)·f_s 侧边带"},
    "resource.brb.index": {"en": "Index: dB ratio of sideband amplitude to fundamental", "zh": "指数：侧边带幅值与基波的 dB 比值"},
    "resource.brb.thresholds": {"en": "Thresholds (dB below fundamental):", "zh": "阈值 (相对基波 dB)："},
    "resource.brb.healthy": {"en": "Healthy: ≤ -50 dB", "zh": "健康：≤ -50 dB"},
    "resource.brb.incipient": {"en": "Incipient: -50 to -45 dB", "zh": "初期：-50 至 -45 dB"},
    "resource.brb.moderate": {"en": "Moderate: -45 to -40 dB", "zh": "中度：-45 至 -40 dB"},
    "resource.brb.severe": {"en": "Severe: > -35 dB", "zh": "严重：> -35 dB"},
    "resource.brb.notes": {"en": "More visible at medium–high load; higher harmonics at (1 ± 2ks)·f_s", "zh": "中高负载下更明显；高次谐波出现在 (1 ± 2ks)·f_s"},

    "resource.ecc.title": {"en": "Eccentricity (Static / Dynamic)", "zh": "偏心 (静偏心 / 动偏心)"},
    "resource.ecc.signature": {"en": "Sidebands at f_s ± k·f_r (rotor frequency multiples)", "zh": "在 f_s ± k·f_r 处出现侧边带 (转子频率倍数)"},
    "resource.ecc.static": {"en": "Static eccentricity: produces components at f_s ± f_r", "zh": "静偏心：在 f_s ± f_r 产生分量"},
    "resource.ecc.dynamic": {"en": "Dynamic eccentricity: produces components at f_s ± k·f_r, varying with load", "zh": "动偏心：在 f_s ± k·f_r 产生分量，随负载变化"},
    "resource.ecc.mixed": {"en": "Mixed eccentricity: components at n·f_r (pure rotational harmonics)", "zh": "混合偏心：在 n·f_r 产生纯转动谐波分量"},

    "resource.stator.title": {"en": "Stator Inter-Turn Short Circuit", "zh": "定子匝间短路"},
    "resource.stator.signature": {"en": "Sidebands at f_s ± 2k·f_r", "zh": "在 f_s ± 2k·f_r 出现侧边带"},
    "resource.stator.notes": {"en": "May also increase negative-sequence current component; distinguish from supply unbalance by checking load dependency", "zh": "亦可能增加负序电流分量；通过负载依赖性与供电不平衡区分"},

    "resource.bearing.title": {"en": "Bearing Defects", "zh": "轴承缺陷"},
    "resource.bearing.signature": {"en": "Sidebands at f_s ± k·f_defect where f_defect is BPFO/BPFI/BSF/FTF", "zh": "在 f_s ± k·f_defect 出现侧边带，f_defect 为 BPFO/BPFI/BSF/FTF"},
    "resource.bearing.bpfo": {"en": "BPFO = (n/2)·(1 - d/D·cos α)", "zh": "BPFO = (n/2)·(1 - d/D·cos α)"},
    "resource.bearing.bpfi": {"en": "BPFI = (n/2)·(1 + d/D·cos α)", "zh": "BPFI = (n/2)·(1 + d/D·cos α)"},
    "resource.bearing.bsf": {"en": "BSF = (D/2d)·(1 - (d/D·cos α)²)", "zh": "BSF = (D/2d)·(1 - (d/D·cos α)²)"},
    "resource.bearing.ftf": {"en": "FTF = (1/2)·(1 - d/D·cos α)", "zh": "FTF = (1/2)·(1 - d/D·cos α)"},
    "resource.bearing.notes": {"en": "Weak in stator current; confirm with envelope analysis or vibration data", "zh": "定子电流中较弱；建议结合包络分析或振动数据确认"},

    "resource.load.title": {"en": "Load Faults (Cavitation, Misalignment)", "zh": "负载故障 (汽蚀、不对中)"},
    "resource.load.signature": {"en": "Broadband energy increase around f_s (\"foot\" pattern in PSD)", "zh": "基波周围宽带能量增加 (PSD 中呈 \"足\" 字形)"},
    "resource.load.index": {"en": "Index: Band energy integration around the supply frequency", "zh": "指数：供电频率周围带内能量积分"},

    # Units
    "unit.hz": {"en": "Hz", "zh": "Hz"},
    "unit.rpm": {"en": "RPM", "zh": "转/分"},
    "unit.db": {"en": "dB", "zh": "dB"},
    "unit.s": {"en": "s", "zh": "秒"},

    # HTML report labels (server-side)
    "report.generated_by": {"en": "Generated by", "zh": "生成者"},
    "report.server_name": {"en": "MCSA MCP Server", "zh": "MCSA MCP 服务器"},
    "report.not_computed": {"en": "Not computed for this run.", "zh": "本次运行未计算。"},
    "report.yes": {"en": "Yes", "zh": "是"},
    "report.no": {"en": "No", "zh": "否"},
    "report.rank": {"en": "Rank", "zh": "排名"},
    "report.prominence": {"en": "Prominence", "zh": "突出度"},
    "detail.na": {"en": "n/a", "zh": "无"},
    "detail.yes": {"en": "Found", "zh": "找到"},
    "detail.no": {"en": "Not found", "zh": "未找到"},
    "report.html_saved": {"en": "HTML diagnostic report saved", "zh": "HTML 诊断报告已保存"},
    "report.docx_saved": {"en": "DOCX diagnostic report saved", "zh": "DOCX 诊断报告已保存"},

    # DOCX report labels
    "report.title.mcsa_diagnostic": {"en": "MCSA Diagnostic Report", "zh": "MCSA 诊断报告"},
    "ui.generated": {"en": "Generated", "zh": "生成时间"},
    "doc.parameter": {"en": "Parameter", "zh": "参数"},
    "doc.value": {"en": "Value", "zh": "值"},
    "signal.source_file": {"en": "Source File", "zh": "数据源"},
    "motor_param.supply_freq": {"en": "Supply Frequency", "zh": "供电频率"},
    "motor_param.poles": {"en": "Number of Poles", "zh": "极数"},
    "report.overall_assessment": {"en": "Overall Assessment", "zh": "综合评估"},
    "report.recommendations": {"en": "Recommendations", "zh": "建议"},
    "rec.immediate": {"en": "Immediate inspection recommended", "zh": "建议立即检查"},
    "rec.maintenance": {"en": "Schedule maintenance", "zh": "建议安排维护"},
    "rec.monitoring": {"en": "Increase monitoring frequency", "zh": "增加监测频次"},
    "rec.review": {"en": "Review recommended", "zh": "建议审查"},
}


def get_text(key: str, lang: Language = "en") -> str:
    """Get translated text for a key in the specified language.

    Args:
        key: Translation key (e.g., "severity.healthy", "fault_type.broken_rotor_bars")
        lang: Target language ("en" or "zh")

    Returns:
        Translated string. Falls back to English if key not found.
    """
    entry = TRANSLATIONS.get(key)
    if entry is None:
        # Fallback: return key itself for missing translations
        return key
    return entry.get(lang, entry["en"])


def get_fault_type_name(fault_type: str, lang: Language = "en") -> str:
    """Get translated fault type name.

    Args:
        fault_type: Internal fault type key (e.g., "broken_rotor_bars", "bearing_bpfo")
        lang: Target language

    Returns:
        Translated display name.
    """
    key = f"fault_type.{fault_type}"
    return get_text(key, lang)


def get_severity_label(severity: str, lang: Language = "en") -> str:
    """Get translated severity label.

    Args:
        severity: Internal severity key (healthy/incipient/moderate/severe)
        lang: Target language

    Returns:
        Translated severity label.
    """
    key = f"severity.{severity}"
    return get_text(key, lang)


def get_detection_reason(reason: str, lang: Language = "en") -> str:
    """Get translated detection status reason.

    Args:
        reason: Internal reason key (detected/no_sideband_present/...)
        lang: Target language

    Returns:
        Translated reason.
    """
    key = f"detection_status.{reason}"
    return get_text(key, lang)


def get_assessment_text(assessment_key: str, lang: Language = "en") -> str:
    """Get translated overall assessment text.

    Args:
        assessment_key: One of "critical", "warning", "watch", "normal"
        lang: Target language

    Returns:
        Translated assessment text.
    """
    key = f"assessment.{assessment_key}"
    return get_text(key, lang)


def get_resource_text(key: str, lang: Language = "en") -> str:
    """Get translated resource text for fault signatures reference.

    Args:
        key: Resource key (e.g., "resource.brb.title", "resource.ecc.signature")
        lang: Target language

    Returns:
        Translated text.
    """
    return get_text(key, lang)
