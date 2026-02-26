"""
metrics.py — Full metric computation engine, risk classification, executive summary
Navedas Intelligence — AI Validation Confidence Monitor
"""

from __future__ import annotations
import pandas as pd
import numpy as np
from typing import Any

REQUIRED_ENVIRONMENTS = {"Desktop", "Mobile", "AMP", "AdBlock", "SlowNetwork"}


# ═══════════════════════════════════════════════════════════════════════════════
# CORE METRIC COMPUTATIONS
# ═══════════════════════════════════════════════════════════════════════════════

def compute_ai_confidence_index(df: pd.DataFrame) -> float:
    """Mean AI confidence score across all rows."""
    return float(df["ai_confidence_score"].mean())


def compute_ecs(df: pd.DataFrame) -> float:
    """
    Environmental Coverage Score.
    = (distinct environments tested / 5) × 100
    Penalizes any missing environment from the required set of 5.
    """
    found_envs = set(df["environment"].dropna().unique())
    covered = len(found_envs & REQUIRED_ENVIRONMENTS)
    return round((covered / len(REQUIRED_ENVIRONMENTS)) * 100, 2)


def compute_false_negative_rate(df: pd.DataFrame) -> float:
    """
    False Negative Rate (as percentage).
    = sum(false_negative) / sum(actual_failure) × 100
    Returns 0.0 if there are no actual failures.
    """
    total_actual = df["actual_failure"].sum()
    if total_actual == 0:
        return 0.0
    return round((df["false_negative"].sum() / total_actual) * 100, 2)


def compute_precision(df: pd.DataFrame) -> float:
    """
    Precision = true_positive_detections / total_detected_failures (by AI).
    true_positive: AI detected a failure AND it was an actual failure.
    total_detected: all rows where failure_detected_by_ai == True.
    Returns 0.0 if AI detected nothing.
    """
    total_detected = df["failure_detected_by_ai"].sum()
    if total_detected == 0:
        return 0.0
    true_positives = (df["failure_detected_by_ai"] & df["actual_failure"]).sum()
    return round(float(true_positives / total_detected), 6)


def compute_confidence_gap(ai_confidence_index: float, precision: float) -> float:
    """
    Confidence Gap = AI Confidence Index − (Precision × 100)
    Measures how overconfident the AI is relative to its actual precision.
    """
    return round(ai_confidence_index - (precision * 100), 2)


def compute_rai(precision: float, ecs: float) -> float:
    """
    Reality Alignment Index = (Precision × ECS) / 100
    Composite metric tying precision to environmental coverage.
    """
    return round((precision * ecs) / 100, 2)


def compute_uncertainty_rate(df: pd.DataFrame) -> float:
    """Proportion of rows with uncertainty_flag set (as percentage)."""
    return round((df["uncertainty_flag"].sum() / len(df)) * 100, 2)


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE-LEVEL METRICS
# ═══════════════════════════════════════════════════════════════════════════════

def compute_phase_metrics(df: pd.DataFrame, phase: str) -> dict[str, Any]:
    """Compute the full metric set for a single phase slice."""
    subset = df[df["phase"] == phase].copy()
    if subset.empty:
        return {
            "phase": phase, "row_count": 0,
            "ai_confidence_index": None, "ecs": None,
            "false_negative_rate": None, "precision": None,
            "confidence_gap": None, "rai": None,
            "uncertainty_rate": None,
        }

    aci = compute_ai_confidence_index(subset)
    ecs = compute_ecs(subset)
    fnr = compute_false_negative_rate(subset)
    prec = compute_precision(subset)
    gap = compute_confidence_gap(aci, prec)
    rai = compute_rai(prec, ecs)
    unc = compute_uncertainty_rate(subset)

    return {
        "phase": phase,
        "row_count": len(subset),
        "ai_confidence_index": round(aci, 2),
        "ecs": ecs,
        "false_negative_rate": fnr,
        "precision": round(prec * 100, 2),
        "confidence_gap": gap,
        "rai": rai,
        "uncertainty_rate": unc,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# ENVIRONMENT-LEVEL METRICS
# ═══════════════════════════════════════════════════════════════════════════════

def compute_environment_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Per-environment breakdown of key performance indicators."""
    records = []
    for env in sorted(df["environment"].dropna().unique()):
        sub = df[df["environment"] == env]
        prec = compute_precision(sub)
        records.append({
            "Environment": env,
            "Rows": len(sub),
            "Avg Confidence": round(sub["ai_confidence_score"].mean(), 2),
            "False Negative Rate (%)": compute_false_negative_rate(sub),
            "Precision (%)": round(prec * 100, 2),
            "Uncertainty Rate (%)": compute_uncertainty_rate(sub),
            "Avg Latency (ms)": round(sub["latency_ms"].mean(), 1),
        })
    return pd.DataFrame(records)


# ═══════════════════════════════════════════════════════════════════════════════
# FULL METRIC BUNDLE
# ═══════════════════════════════════════════════════════════════════════════════

def compute_all_metrics(df: pd.DataFrame) -> dict[str, Any]:
    """
    Compute the complete metric dictionary for the full dataset and
    per-phase slices. This is the single source of truth for the dashboard.
    """
    aci = compute_ai_confidence_index(df)
    ecs = compute_ecs(df)
    fnr = compute_false_negative_rate(df)
    prec = compute_precision(df)
    gap = compute_confidence_gap(aci, prec)
    rai = compute_rai(prec, ecs)
    unc = compute_uncertainty_rate(df)

    phase_before = compute_phase_metrics(df, "Before")
    phase_after = compute_phase_metrics(df, "After")
    env_metrics = compute_environment_metrics(df)

    return {
        # ── Global ──────────────────────────────────────────────────────────
        "ai_confidence_index": round(aci, 2),
        "ecs": ecs,
        "false_negative_rate": fnr,
        "precision": round(prec * 100, 2),
        "confidence_gap": gap,
        "rai": rai,
        "uncertainty_rate": unc,
        # ── Phase comparison ─────────────────────────────────────────────────
        "phase_before": phase_before,
        "phase_after": phase_after,
        # ── Environment detail ───────────────────────────────────────────────
        "env_metrics": env_metrics,
        # ── Risk classification ──────────────────────────────────────────────
        "risk": classify_risk(gap, ecs, fnr, rai),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# RISK CLASSIFICATION
# ═══════════════════════════════════════════════════════════════════════════════

def classify_risk(
    confidence_gap: float,
    ecs: float,
    false_negative_rate: float,
    rai: float,
) -> dict[str, Any]:
    """
    Governance risk classification based on four threshold rules.
    Returns structured risk report with individual signals and overall severity.
    """
    signals: list[dict[str, str]] = []
    severity_order = {"Critical": 3, "High Risk": 2, "Elevated": 1, "Acceptable": 0}
    max_severity = "Acceptable"

    def _register(name: str, value: float, threshold: str, severity: str, detail: str):
        nonlocal max_severity
        signals.append({
            "Signal": name,
            "Value": value,
            "Threshold": threshold,
            "Severity": severity,
            "Detail": detail,
        })
        if severity_order.get(severity, 0) > severity_order.get(max_severity, 0):
            max_severity = severity

    # Rule 1 — Confidence Gap
    if confidence_gap > 20:
        _register(
            "Confidence Gap", confidence_gap, "> 20", "Critical",
            "AI confidence significantly exceeds validated precision. Leadership signals are unreliable.",
        )
    elif confidence_gap > 10:
        _register(
            "Confidence Gap", confidence_gap, "> 10", "Elevated",
            "Moderate overconfidence detected. Monitor but not yet governance-critical.",
        )
    else:
        _register(
            "Confidence Gap", confidence_gap, "≤ 10", "Acceptable",
            "AI confidence is aligned with precision.",
        )

    # Rule 2 — Environmental Coverage Score
    if ecs < 60:
        _register(
            "ECS", ecs, "< 60", "High Risk",
            "Critical environment gaps present. Blind spots will produce systematic false negatives.",
        )
    elif ecs < 80:
        _register(
            "ECS", ecs, "60–80", "Elevated",
            "Some environments under-tested. Coverage should be expanded before production sign-off.",
        )
    else:
        _register(
            "ECS", ecs, "≥ 80", "Acceptable",
            "Environmental coverage is adequate.",
        )

    # Rule 3 — False Negative Rate
    if false_negative_rate > 10:
        _register(
            "False Negative Rate", false_negative_rate, "> 10%", "Critical",
            "More than 1-in-10 real failures go undetected. Production risk is unacceptably high.",
        )
    elif false_negative_rate > 5:
        _register(
            "False Negative Rate", false_negative_rate, "5–10%", "Elevated",
            "Elevated miss rate. Investigate environment-specific failure patterns.",
        )
    else:
        _register(
            "False Negative Rate", false_negative_rate, "≤ 5%", "Acceptable",
            "False negative exposure is within governance tolerance.",
        )

    # Rule 4 — Reality Alignment Index
    if rai < 50:
        _register(
            "RAI", rai, "< 50", "Governance Failure",
            "AI validation system cannot be trusted for production governance decisions.",
        )
    elif rai < 70:
        _register(
            "RAI", rai, "50–70", "Elevated",
            "RAI indicates partial alignment. Proceed with manual oversight for critical paths.",
        )
    else:
        _register(
            "RAI", rai, "≥ 70", "Acceptable",
            "Reality Alignment is sufficient for governance use.",
        )

    return {
        "signals": signals,
        "overall_severity": max_severity,
        "signal_count": len(signals),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# EXECUTIVE SUMMARY
# ═══════════════════════════════════════════════════════════════════════════════

def generate_executive_summary(metrics: dict[str, Any]) -> str:
    """
    Generate a concise executive summary paragraph from the computed metrics.
    Tone: analytical, neutral, executive-grade.
    """
    aci = metrics["ai_confidence_index"]
    ecs = metrics["ecs"]
    fnr = metrics["false_negative_rate"]
    prec = metrics["precision"]
    gap = metrics["confidence_gap"]
    rai = metrics["rai"]
    unc = metrics["uncertainty_rate"]
    severity = metrics["risk"]["overall_severity"]

    before = metrics["phase_before"]
    after = metrics["phase_after"]

    # Delta calculations (handle None for missing phases)
    def delta(key: str) -> str:
        b = before.get(key)
        a = after.get(key)
        if b is None or a is None:
            return "N/A"
        d = a - b
        sign = "+" if d >= 0 else ""
        return f"{sign}{d:.1f}"

    fnr_delta = delta("false_negative_rate")
    gap_delta = delta("confidence_gap")
    rai_delta = delta("rai")
    ecs_delta = delta("ecs")

    blind_spots = REQUIRED_ENVIRONMENTS - set(
        metrics["env_metrics"]["Environment"].tolist()
        if isinstance(metrics["env_metrics"], pd.DataFrame)
        else []
    )
    blind_spot_str = (
        f"No environment blind spots remain in the current dataset."
        if not blind_spots
        else f"The following environments were not represented: {', '.join(sorted(blind_spots))}."
    )

    trust_statement = (
        "Based on current metrics, AI validation signals are NOT sufficiently trustworthy "
        "for unreviewed governance decisions."
        if severity in ("Critical", "Governance Failure", "High Risk")
        else (
            "AI validation signals are conditionally trustworthy with human oversight recommended "
            "for high-stakes decisions."
            if severity == "Elevated"
            else "AI validation signals are trustworthy for governance purposes at current metric levels."
        )
    )

    summary = f"""
The AI validation system operates at a mean confidence score of {aci:.1f}%,
yet validated precision stands at {prec:.1f}%, producing a Confidence Gap of {gap:.1f} points.
This gap indicates the system overstates its detection reliability relative to empirical outcomes.

Environmental coverage spans {ecs:.0f}% of required test environments. {blind_spot_str}
The False Negative Rate is {fnr:.1f}%, meaning approximately {fnr:.0f} in every 100 actual failures
are missed by the AI validation layer. The Reality Alignment Index (RAI) — a composite measure
of precision and environmental breadth — stands at {rai:.1f}, and {unc:.1f}% of validations
carry active uncertainty flags.

Following the agentic re-engineering intervention, phase comparison shows:
ECS shift of {ecs_delta} points, False Negative Rate change of {fnr_delta}%,
Confidence Gap movement of {gap_delta} points, and RAI movement of {rai_delta} points.
These deltas reflect the impact of mobile-first inspection loops, real-world browser simulation,
and full environment coverage introduced in the After phase.

Overall governance risk is classified as: {severity}.

{trust_statement}
""".strip()

    return summary
