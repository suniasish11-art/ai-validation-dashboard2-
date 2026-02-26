"""
utils.py — Data loading, schema validation, and preprocessing
Navedas Intelligence — AI Validation Confidence Monitor
"""

import os
import sys
import pandas as pd
from pathlib import Path


REQUIRED_COLUMNS = {
    "validation_id": "object",
    "phase": "object",
    "environment": "object",
    "ai_confidence_score": "float64",
    "actual_failure": "bool",
    "failure_detected_by_ai": "bool",
    "false_negative": "bool",
    "uncertainty_flag": "bool",
    "latency_ms": "int64",
    "timestamp": "datetime64[ns]",
}

REQUIRED_ENVIRONMENTS = {"Desktop", "Mobile", "AMP", "AdBlock", "SlowNetwork"}
REQUIRED_PHASES = {"Before", "After"}
EXPECTED_ROW_COUNT = 1200


def locate_csv(filename: str = "ai_validation_telemetry_1200_rows.csv") -> Path:
    """
    Locate the CSV file by searching common locations relative to the
    dashboard directory and common user paths. No hardcoded absolute paths.
    """
    search_roots = [
        Path(__file__).parent,                  # same folder as this script
        Path(__file__).parent.parent,           # one level up
        Path.home(),                            # user home
        Path.home() / "Downloads",
        Path.home() / "Desktop",
        Path.home() / "Documents",
    ]

    for root in search_roots:
        candidate = root / filename
        if candidate.exists():
            return candidate

    raise FileNotFoundError(
        f"\n[DATA ERROR] Cannot locate '{filename}'.\n"
        f"Searched in: {[str(r) for r in search_roots]}\n"
        f"Place the CSV file in the same folder as dashboard.py and retry.\n"
        f"Run: streamlit run dashboard.py"
    )


def load_and_validate(filepath: Path) -> pd.DataFrame:
    """
    Load CSV, enforce schema, parse timestamps, cast booleans, validate row count.
    Returns a clean, typed DataFrame.
    """
    try:
        df = pd.read_csv(filepath)
    except Exception as exc:
        raise RuntimeError(f"[LOAD ERROR] Failed to read CSV at '{filepath}': {exc}")

    # ── Column presence check ────────────────────────────────────────────────
    missing_cols = set(REQUIRED_COLUMNS.keys()) - set(df.columns)
    if missing_cols:
        raise ValueError(f"[SCHEMA ERROR] Missing columns: {missing_cols}")

    # ── Boolean coercion ─────────────────────────────────────────────────────
    bool_cols = ["actual_failure", "failure_detected_by_ai", "false_negative", "uncertainty_flag"]
    for col in bool_cols:
        if df[col].dtype == object:
            df[col] = df[col].str.strip().str.lower().map({"true": True, "false": False})
        df[col] = df[col].astype(bool)

    # ── Numeric coercion ─────────────────────────────────────────────────────
    df["ai_confidence_score"] = pd.to_numeric(df["ai_confidence_score"], errors="coerce")
    df["latency_ms"] = pd.to_numeric(df["latency_ms"], errors="coerce").fillna(0).astype(int)

    # ── Timestamp parsing ────────────────────────────────────────────────────
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    null_ts = df["timestamp"].isna().sum()
    if null_ts > 0:
        print(f"[WARNING] {null_ts} rows have unparseable timestamps — these rows will be excluded from trend charts.")

    # ── Phase / environment validation ───────────────────────────────────────
    found_phases = set(df["phase"].dropna().unique())
    found_envs = set(df["environment"].dropna().unique())

    missing_phases = REQUIRED_PHASES - found_phases
    missing_envs = REQUIRED_ENVIRONMENTS - found_envs

    if missing_phases:
        print(f"[WARNING] Missing phases: {missing_phases}")
    if missing_envs:
        print(f"[WARNING] Missing environments: {missing_envs} — ECS will be penalized.")

    # ── Row count check ──────────────────────────────────────────────────────
    actual_rows = len(df)
    if actual_rows != EXPECTED_ROW_COUNT:
        print(f"[WARNING] Expected {EXPECTED_ROW_COUNT} rows, found {actual_rows}.")

    # ── Drop rows with null confidence (critical metric) ────────────────────
    null_conf = df["ai_confidence_score"].isna().sum()
    if null_conf > 0:
        print(f"[WARNING] {null_conf} rows with null ai_confidence_score dropped.")
        df = df.dropna(subset=["ai_confidence_score"])

    return df.reset_index(drop=True)


def print_summary(df: pd.DataFrame) -> None:
    """Print a concise summary of the loaded dataset."""
    print("\n" + "=" * 60)
    print("  DATASET SUMMARY")
    print("=" * 60)
    print(f"  Total rows loaded      : {len(df)}")
    print(f"  Phases present         : {sorted(df['phase'].unique())}")
    print(f"  Environments present   : {sorted(df['environment'].unique())}")
    print(f"  Date range             : {df['timestamp'].min()} to {df['timestamp'].max()}")
    print(f"  Actual failures        : {df['actual_failure'].sum()}")
    print(f"  AI-detected failures   : {df['failure_detected_by_ai'].sum()}")
    print(f"  False negatives        : {df['false_negative'].sum()}")
    print(f"  Uncertainty flags      : {df['uncertainty_flag'].sum()}")
    print(f"  Avg confidence score   : {df['ai_confidence_score'].mean():.2f}")
    print(f"  Avg latency (ms)       : {df['latency_ms'].mean():.1f}")
    print("=" * 60 + "\n")
