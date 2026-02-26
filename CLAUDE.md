# AI Validation Confidence Dashboard — CLAUDE.md

## Project Overview
A production-grade AI Validation Confidence Monitor built with Python + Streamlit.
Loads a 1200-row telemetry CSV and computes 7 governance metrics displayed across 11 dashboard sections.

## Project Location
`C:\Users\sunit\navedas_dashboard\`

## GitHub Repository
`https://github.com/suniasish11-art/ai-validation-dashboard2-`

## Tech Stack
- Python 3.14
- Streamlit 1.54.0
- Plotly 6.5.2
- pandas 2.3.3
- NumPy 1.x
- No matplotlib (removed — replaced with pure CSS color scale)

## File Structure
```
navedas_dashboard/
├── dashboard.py     — main Streamlit app, all UI, charts, CSS
├── metrics.py       — all metric computations, risk classification, executive summary
├── utils.py         — CSV loader, schema validator, data cleaner
├── requirements.txt — streamlit, pandas, numpy, plotly
└── ai_validation_telemetry_1200_rows.csv  — 1200 rows, 10 columns
```

## CSV Schema (10 columns)
| Column | Type | Description |
|---|---|---|
| validation_id | string | Unique row identifier |
| phase | string | "Before" or "After" |
| environment | string | Desktop / Mobile / AMP / AdBlock / SlowNetwork |
| ai_confidence_score | float | AI self-reported confidence (0–100) |
| actual_failure | bool | Was there a real failure? |
| failure_detected_by_ai | bool | Did AI detect the failure? |
| false_negative | bool | Real failure missed by AI |
| uncertainty_flag | bool | AI flagged itself as uncertain |
| latency_ms | int | Response latency in milliseconds |
| timestamp | datetime | When the validation occurred |

## 7 Core Metrics
| Metric | Formula | Critical Threshold |
|---|---|---|
| AI Confidence Index (ACI) | mean(ai_confidence_score) | < 85% = warning |
| ECS | (distinct envs / 5) × 100 | < 60% = High Risk |
| False Negative Rate (FNR) | (false_negatives / actual_failures) × 100 | > 10% = Critical |
| Precision | true_positives / AI_detected | < 60% = poor |
| Confidence Gap | ACI − (Precision × 100) | > 20 = Critical |
| RAI | (Precision × ECS) / 100 | < 50 = Governance Failure |
| Uncertainty Rate | (uncertainty_flag rows / total) × 100 | > 20% = poor |

## Risk Classification Rules
- Confidence Gap > 20 → Critical
- ECS < 60 → High Risk
- FNR > 10% → Critical
- RAI < 50 → Governance Failure
- Overall severity = worst signal across all four

## Key Architecture Decisions

### _hex_to_rgba() helper (dashboard.py)
Plotly does NOT accept 8-digit hex colors like `#ff4b4bcc`.
Always use `_hex_to_rgba(hex, alpha)` to convert colors for Plotly.
```python
def _hex_to_rgba(hex_color: str, alpha: float) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"
```

### Plotly Gauge — gridcolor is INVALID
The gauge axis only accepts `tickcolor`, NOT `gridcolor`.
Removing `gridcolor` is mandatory or Plotly throws ValueError.

### Streamlit Deprecated APIs
- Use `width='stretch'` NOT `use_container_width=True` (deprecated in 1.54)
- Use `width='content'` NOT `use_container_width=False`
- Use `.map()` NOT `.applymap()` (deprecated in pandas 2.x)

### Widget Label Visibility
Streamlit 1.54.0 widget labels (selectbox, checkbox) may be invisible on dark backgrounds.
Fix pattern used:
- Selectboxes: use `label_visibility="collapsed"` + manual `st.markdown("<span class='filter-lbl'>Label</span>")`
- Checkboxes: target with `div[data-testid="stCheckbox"] label span` CSS

### CSS Color Scale (no matplotlib)
`background_gradient()` requires matplotlib. We use a custom pure-CSS `_color_scale()` function instead.
Red → Yellow → Green scale applied to FNR and Precision columns in the environment table.

### CSV Location
`utils.py` searches these paths in order:
1. Same folder as script (works for both local and Streamlit Cloud)
2. One level up
3. User home, Downloads, Desktop, Documents

## Design System
- Background: `#050b18` (deep navy)
- Card background: `#080f1e` / `#0a1628`
- Primary accent: `#6389ff` (blue)
- Text primary: `#c8d8ff`
- Text secondary: `#8892b0` / `#7a90b8`
- Success: `#00d97e`
- Warning: `#ffd600`
- Danger: `#ff4b4b`
- Critical: `#ff0055`
- Orange: `#ff8800`
- Font: Inter (Google Fonts)

## Running Locally
```bash
cd C:\Users\sunit\navedas_dashboard
streamlit run dashboard.py --server.port 8503
```
Visit: http://localhost:8503

## Deploying to Streamlit Cloud
1. Push all files to GitHub repo `suniasish11-art/ai-validation-dashboard2-`
2. Go to https://share.streamlit.io
3. Select repo, branch = main, main file = dashboard.py
4. Click Deploy

## Common Errors and Fixes
| Error | Fix |
|---|---|
| `ValueError: Invalid color '#ff4b4bcc'` | Use `_hex_to_rgba()` — never append hex alpha like `+ "cc"` |
| `ValueError: Invalid property 'gridcolor' for gauge.Axis` | Remove gridcolor — only `tickcolor` is valid |
| `ImportError: background_gradient requires matplotlib` | Use custom `_color_scale()` + `.apply(axis=1)` |
| `UnicodeEncodeError on →` | Windows CP1252 rejects Unicode arrows — use "to" instead |
| Port already in use | Use `--server.port 8504` or kill existing process |
| Widget labels invisible | Use `label_visibility="collapsed"` + manual markdown labels |

## User Preferences
- Step-by-step guidance preferred
- Windows 11 machine
- Using VS Code
- GitHub username: suniasish11-art
- Email: suniasish11@gmail.com
