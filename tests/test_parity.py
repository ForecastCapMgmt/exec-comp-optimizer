#!/usr/bin/env python3
"""Compare the Streamlit formulas, calc.py, and the browser page.

The legacy function below is a direct transcription of the math that used to
live inline in app.py. calc.py is what app.py calls now. The JavaScript
inside web/exec-comp-optimizer.html must match both, including display
rounding (Python's round-half-even format).
"""

from __future__ import annotations

import json
import math
import random
import re
import shutil
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from calc import compute_exec_comp  # noqa: E402

HTML_PATH = ROOT / "web" / "exec-comp-optimizer.html"
RESULTS_PATH = ROOT / "tests" / "PARITY_RESULTS.md"

NUMERIC_KEYS = (
    "price",
    "gross_value",
    "intrinsic_value",
    "vesting_gross",
    "vesting_intrinsic",
    "vesting_tax",
    "net_value",
    "days_to_vesting",
    "months_to_vesting",
    "position_value",
    "concentration_pct",
    "vesting_concentration",
    "sell_after_tax",
    "hold_value",
    "post_vesting_conc",
)
STRING_KEYS = (
    "tax_note",
    "base_rec",
    "timing_advice",
    "recommendation",
    "risk_color",
    "risk_text",
    "warning_text",
    "price_display",
    "gross_display",
    "net_display",
    "vesting_tax_display",
    "concentration_display",
    "vesting_concentration_display",
    "sell_display",
    "hold_display",
    "post_vesting_display",
)


def legacy(case: dict) -> dict:
    """Original app.py formulas, plus the same display strings the page prints."""
    price = case["price"]
    total_shares = case["total_shares"]
    option_type = case["option_type"]
    strike = case["strike"]
    federal_tax_rate = case["federal_tax_rate"]
    amt_rate = case["amt_rate"]
    shares_vesting = case["shares_vesting"]
    next_vesting_date = date.fromisoformat(case["next_vesting_date"])
    net_worth = case["net_worth"]
    today = date.fromisoformat(case["today"])

    if not price:
        price = 150.0
    gross_value = price * total_shares
    intrinsic_value = max(0, price - strike) * total_shares
    vesting_gross = price * shares_vesting
    vesting_intrinsic = max(0, price - strike) * shares_vesting

    if option_type == "RSU":
        vesting_tax = vesting_gross * (federal_tax_rate / 100)
        net_value = gross_value * (1 - federal_tax_rate / 100)
        tax_note = f"RSU: Est. tax on next vesting ≈ ${vesting_tax:,.0f}"
        base_rec = "RSUs are taxed as ordinary income upon vesting."
    else:
        vesting_tax = (
            vesting_intrinsic * (federal_tax_rate / 100)
            if option_type == "NSO"
            else vesting_intrinsic * (amt_rate / 100)
        )
        net_value = (
            (intrinsic_value * (1 - federal_tax_rate / 100)) + (total_shares * strike)
            if option_type != "ISO"
            else (vesting_intrinsic - vesting_tax) + (total_shares * strike)
        )
        tax_note = (
            f"ISO: Est. AMT on next vesting spread ≈ ${vesting_tax:,.0f}"
            if option_type == "ISO"
            else f"NSO: Est. tax on next vesting spread ≈ ${vesting_tax:,.0f}"
        )
        base_rec = (
            "ISOs offer long-term capital gains potential if held properly."
            if option_type == "ISO"
            else "NSOs trigger ordinary income tax on the bargain element when exercised."
        )

    days_to_vesting = (next_vesting_date - today).days
    months_to_vesting = max(0, days_to_vesting // 30)
    if months_to_vesting <= 3:
        timing_advice = (
            f"With {shares_vesting:,} shares vesting in the next {months_to_vesting} months, "
            "plan for the immediate tax impact."
        )
    elif months_to_vesting <= 12:
        timing_advice = (
            f"{shares_vesting:,} shares vesting in about {months_to_vesting} months "
            "gives you planning time."
        )
    else:
        timing_advice = "Vesting is further out — good opportunity to model scenarios."

    recommendation = f"{base_rec} {timing_advice}"
    position_value = gross_value if option_type == "RSU" else (intrinsic_value + total_shares * strike)
    concentration_pct = (position_value / net_worth * 100) if net_worth > 0 else 0
    vesting_concentration = (vesting_gross / net_worth * 100) if net_worth > 0 else 0

    if concentration_pct < 10:
        risk_color = "#4caf7d"
        risk_text = "Low"
    elif concentration_pct < 20:
        risk_color = "#f0b429"
        risk_text = "Moderate"
    else:
        risk_color = "#e05c5c"
        risk_text = "High — consider diversifying"

    show_vesting_warning = vesting_concentration > 5
    warning_text = (
        f"Next vesting could add ~{vesting_concentration:.1f}% concentration."
        if show_vesting_warning
        else ""
    )

    growth_rates = [0.0, 0.05, 0.10, 0.15, 0.20]
    future_net = []
    for rate in growth_rates:
        fp = price * (1 + rate)
        if option_type == "RSU":
            future_net.append(fp * total_shares * (1 - federal_tax_rate / 100))
        else:
            fi = max(0, fp - strike) * total_shares
            future_net.append(fi * (1 - federal_tax_rate / 100) + total_shares * strike)

    sell_after_tax = (
        vesting_gross * (1 - federal_tax_rate / 100)
        if option_type == "RSU"
        else (vesting_intrinsic * (1 - federal_tax_rate / 100))
    )
    hold_value = (
        vesting_gross if option_type == "RSU" else vesting_intrinsic + shares_vesting * strike
    )
    post_vesting_conc = ((position_value + vesting_gross) / net_worth * 100) if net_worth > 0 else 0

    return {
        "price": price,
        "gross_value": gross_value,
        "intrinsic_value": intrinsic_value,
        "vesting_gross": vesting_gross,
        "vesting_intrinsic": vesting_intrinsic,
        "vesting_tax": vesting_tax,
        "net_value": net_value,
        "tax_note": tax_note,
        "base_rec": base_rec,
        "days_to_vesting": days_to_vesting,
        "months_to_vesting": months_to_vesting,
        "timing_advice": timing_advice,
        "recommendation": recommendation,
        "position_value": position_value,
        "concentration_pct": concentration_pct,
        "vesting_concentration": vesting_concentration,
        "risk_color": risk_color,
        "risk_text": risk_text,
        "show_vesting_warning": show_vesting_warning,
        "warning_text": warning_text,
        "growth_rates": growth_rates,
        "growth_labels": [f"{int(r * 100)}%" for r in growth_rates],
        "future_net": future_net,
        "future_net_display": [f"${v:,.0f}" for v in future_net],
        "sell_after_tax": sell_after_tax,
        "hold_value": hold_value,
        "post_vesting_conc": post_vesting_conc,
        "price_display": f"${price:,.2f}",
        "gross_display": f"${gross_value:,.0f}",
        "net_display": f"${net_value:,.0f}",
        "vesting_tax_display": f"${vesting_tax:,.0f}",
        "concentration_display": f"{concentration_pct:.1f}%",
        "vesting_concentration_display": f"{vesting_concentration:.1f}%",
        "sell_display": f"${sell_after_tax:,.0f}",
        "hold_display": f"${hold_value:,.0f}",
        "post_vesting_display": f"{post_vesting_conc:.1f}%",
    }


def build_cases() -> list[dict]:
    today = date(2026, 10, 19)

    def case(name, **kwargs):
        days = kwargs.pop("days", 0)
        base = {
            "name": name,
            "price": 150.0,
            "total_shares": 5000,
            "option_type": "RSU",
            "strike": 45.0,
            "federal_tax_rate": 32,
            "amt_rate": 26,
            "shares_vesting": 1250,
            "net_worth": 2_000_000,
            "today": today.isoformat(),
            "next_vesting_date": (today + timedelta(days=days)).isoformat(),
        }
        base.update(kwargs)
        return base

    cases = [
        case("default_rsu_vests_today"),
        case("rsu_three_months", days=90),
        case("rsu_just_under_four_months", days=119),
        case("rsu_four_months", days=120),
        case("rsu_twelve_months", days=360),
        case("rsu_just_over_twelve_months_calendar", days=361),
        case("rsu_further_out", days=390),
        case("rsu_past_date", days=-10),
        case("rsu_tax_22", federal_tax_rate=22),
        case("rsu_tax_37", federal_tax_rate=37, days=200),
        case("rsu_zero_vesting_shares", shares_vesting=0, days=10),
        case("rsu_min_grant", total_shares=100, shares_vesting=25, price=10, strike=0, net_worth=100_000),
        case("price_zero_falls_back_to_150", price=0),
        case("price_null_falls_back_to_150", price=None),
        case("fractional_price", price=123.45, strike=45.67, total_shares=2500, shares_vesting=625, days=45),
        case(
            "concentration_exact_10",
            price=100,
            total_shares=1000,
            shares_vesting=100,
            net_worth=1_000_000,
            strike=0,
        ),
        case(
            "concentration_just_under_10_displays_10",
            price=100,
            total_shares=1000,
            shares_vesting=100,
            net_worth=1_000_001,
            strike=0,
        ),
        case(
            "concentration_exact_20",
            price=100,
            total_shares=1000,
            shares_vesting=100,
            net_worth=500_000,
            strike=0,
        ),
        case(
            "concentration_just_under_20",
            price=100,
            total_shares=1000,
            shares_vesting=100,
            net_worth=500_001,
            strike=0,
        ),
        case(
            "concentration_over_100",
            price=100,
            total_shares=10_000,
            shares_vesting=1000,
            net_worth=100_000,
            strike=0,
        ),
        case(
            "vesting_concentration_exact_5",
            price=50,
            total_shares=2000,
            shares_vesting=1000,
            net_worth=1_000_000,
        ),
        case(
            "vesting_concentration_just_over_5",
            price=50,
            total_shares=2000,
            shares_vesting=1001,
            net_worth=1_000_000,
        ),
        case(
            "vesting_warning_rounds_to_5_display",
            price=100,
            total_shares=2000,
            shares_vesting=504,
            net_worth=1_000_000,
        ),
        case("net_worth_zero", net_worth=0, price=100, total_shares=1000),
        case(
            "nso_in_the_money",
            option_type="NSO",
            price=100,
            strike=40,
            total_shares=1000,
            shares_vesting=100,
            federal_tax_rate=32,
            net_worth=1_500_000,
            days=200,
        ),
        case(
            "nso_out_of_the_money_until_growth",
            option_type="NSO",
            price=40,
            strike=42,
            total_shares=1000,
            shares_vesting=250,
            federal_tax_rate=32,
            net_worth=800_000,
            days=60,
        ),
        case(
            "nso_price_equals_strike",
            option_type="NSO",
            price=45,
            strike=45,
            total_shares=5000,
            shares_vesting=1250,
        ),
        case(
            "nso_strike_zero",
            option_type="NSO",
            price=80,
            strike=0,
            total_shares=1500,
            shares_vesting=300,
            federal_tax_rate=24,
        ),
        case(
            "iso_amt_26",
            option_type="ISO",
            price=100,
            strike=40,
            total_shares=1000,
            shares_vesting=100,
            federal_tax_rate=32,
            amt_rate=26,
            net_worth=1_500_000,
            days=30,
        ),
        case(
            "iso_amt_zero",
            option_type="ISO",
            price=100,
            strike=40,
            total_shares=1000,
            shares_vesting=100,
            amt_rate=0,
            federal_tax_rate=37,
        ),
        case(
            "iso_amt_28",
            option_type="ISO",
            price=250.5,
            strike=15.25,
            total_shares=8000,
            shares_vesting=2000,
            amt_rate=28,
            federal_tax_rate=35,
            net_worth=5_000_000,
            days=400,
        ),
        case(
            "large_grant",
            option_type="RSU",
            price=350.25,
            total_shares=2_000_000,
            shares_vesting=125_000,
            federal_tax_rate=37,
            net_worth=50_000_000,
            strike=1,
            days=500,
        ),
        case(
            "negative_price_kept",
            price=-5,
            option_type="NSO",
            strike=10,
            total_shares=1000,
            shares_vesting=100,
        ),
    ]
    return cases


def load_js() -> str:
    html = HTML_PATH.read_text(encoding="utf-8")
    match = re.search(r'<script id="fcm-logic">([\s\S]*?)</script>', html)
    if not match:
        raise SystemExit("Could not find #fcm-logic in the HTML file")
    return match.group(1)


def run_js_clean(cases: list[dict], formats: list[dict]) -> dict:
    payload = {
        "cases": [{k: v for k, v in case.items() if k != "name"} for case in cases],
        "formats": formats,
    }
    runner = r"""
const fs = require("fs");
const script = fs.readFileSync(process.argv[1], "utf8");
const payload = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
eval(script);
const cases = payload.cases.map((c) => globalThis.fcmComputeExecComp(c));
const formats = payload.formats.map((c) => globalThis.fcmFormatNumber(c.n, c.d, c.g));
process.stdout.write(JSON.stringify({ cases, formats }));
"""
    tmp = ROOT / "tests" / ".parity-tmp"
    tmp.mkdir(exist_ok=True)
    script_path = tmp / "logic.js"
    payload_path = tmp / "payload.json"
    script_path.write_text(load_js(), encoding="utf-8")
    payload_path.write_text(json.dumps(payload), encoding="utf-8")
    proc = subprocess.run(
        ["node", "-e", runner, str(script_path), str(payload_path)],
        text=True,
        capture_output=True,
        check=False,
    )
    try:
        if proc.returncode != 0:
            raise SystemExit(f"node failed\n{proc.stderr}\n{proc.stdout}")
        return json.loads(proc.stdout)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def close(a, b) -> bool:
    if isinstance(a, bool) or isinstance(b, bool):
        return a is b or a == b
    return math.isclose(float(a), float(b), rel_tol=1e-12, abs_tol=1e-6)


def compare(name: str, expected: dict, actual: dict, label: str) -> list[str]:
    errors = []
    for key in NUMERIC_KEYS:
        if not close(expected[key], actual[key]):
            errors.append(f"{name} {label} {key}: expected {expected[key]!r} got {actual[key]!r}")
    for key in STRING_KEYS:
        if expected[key] != actual[key]:
            errors.append(f"{name} {label} {key}: expected {expected[key]!r} got {actual[key]!r}")
    if expected["show_vesting_warning"] != actual["show_vesting_warning"]:
        errors.append(
            f"{name} {label} show_vesting_warning: expected {expected['show_vesting_warning']!r} "
            f"got {actual['show_vesting_warning']!r}"
        )
    if expected["growth_labels"] != actual["growth_labels"]:
        errors.append(f"{name} {label} growth_labels differ")
    if len(expected["future_net"]) != len(actual["future_net"]):
        errors.append(f"{name} {label} future_net length")
    else:
        for i, (exp, got) in enumerate(zip(expected["future_net"], actual["future_net"])):
            if not close(exp, got):
                errors.append(f"{name} {label} future_net[{i}]: expected {exp!r} got {got!r}")
    if expected["future_net_display"] != actual["future_net_display"]:
        errors.append(
            f"{name} {label} future_net_display: expected {expected['future_net_display']!r} "
            f"got {actual['future_net_display']!r}"
        )
    for i, (exp, got) in enumerate(zip(expected["growth_rates"], actual["growth_rates"])):
        if not close(exp, got):
            errors.append(f"{name} {label} growth_rates[{i}]")
    return errors


def formatter_samples() -> list[dict]:
    rng = random.Random(7)
    samples = [
        0, -0.0, 0.5, 1.5, 2.5, -1.5, -2.5, 10.25, 10.35, 10.05, 1.25,
        100.5, 101.5, 1234.5, 999.5, 1920.5, 509999.99999999994, 68000,
        0.1 + 0.2, 150 * 5000 * (1 - 32 / 100), 1e12, 5.04,
    ]
    samples.extend(rng.uniform(-1e8, 1e8) for _ in range(80))
    samples.extend(rng.randrange(-50_000, 50_000) + 0.5 for _ in range(40))
    formats = []
    for n in samples:
        for d in (0, 1, 2):
            for g in (True, False):
                formats.append({"n": n, "d": d, "g": g})
    return formats


def secrets_errors() -> list[str]:
    errors = []
    html = HTML_PATH.read_text(encoding="utf-8").lower()
    for needle in ("smtp.gmail.com", "sender_password", "sender_email", "app password"):
        if needle in html:
            errors.append(f"HTML contains {needle!r}")
    if (ROOT / "secrets.toml").exists():
        errors.append("secrets.toml is still in the working tree")
    tracked = subprocess.run(
        ["git", "ls-files", "secrets.toml"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if tracked.stdout.strip():
        errors.append("secrets.toml is still tracked by git")
    app = (ROOT / "app.py").read_text(encoding="utf-8")
    if "compute_exec_comp(" not in app:
        errors.append("app.py no longer calls compute_exec_comp")
    return errors


def quirk_errors(cases: list[dict], expected: list[dict]) -> list[str]:
    errors = []
    by_name = {case["name"]: result for case, result in zip(cases, expected)}
    iso = by_name["iso_amt_26"]
    if math.isclose(iso["net_value"], iso["future_net"][0], rel_tol=0, abs_tol=1e-6):
        errors.append("ISO headline net value unexpectedly matches the 0% chart bar")
    rsu = by_name["default_rsu_vests_today"]
    if not math.isclose(rsu["net_value"], rsu["future_net"][0], rel_tol=0, abs_tol=1e-6):
        errors.append("RSU 0% growth bar should equal headline net value")
    nso = by_name["nso_in_the_money"]
    if not math.isclose(nso["net_value"], nso["future_net"][0], rel_tol=0, abs_tol=1e-6):
        errors.append("NSO 0% growth bar should equal headline net value")
    under = by_name["concentration_just_under_10_displays_10"]
    if under["risk_text"] != "Low":
        errors.append("just-under-10 concentration should stay Low")
    if under["concentration_display"] != "10.0%":
        errors.append(
            f"just-under-10 display expected 10.0% got {under['concentration_display']}"
        )
    return errors


def write_report(cases, expected, errors, format_total, format_bad) -> None:
    lines = [
        "# Parity results",
        "",
        "Python source of truth: the original Streamlit formulas (transcribed in `tests/test_parity.py`) and `calc.py`, which `app.py` calls.",
        "JavaScript: `fcmComputeExecComp` in `web/exec-comp-optimizer.html`.",
        "",
        f"- Cases: {len(cases)}",
        f"- Mismatches: {len(errors)}",
        f"- Formatter samples checked against Python `format`: {format_total}",
        f"- Formatter mismatches: {format_bad}",
        "- Numeric tolerance: absolute 1e-6 (display strings must match exactly, including half-even rounding)",
        "",
        "## Worked example (default RSU, price $150, 5,000 shares, 32% federal, vest today)",
        "",
    ]
    sample = expected[0]
    for key in (
        "price_display",
        "gross_display",
        "net_display",
        "vesting_tax_display",
        "tax_note",
        "recommendation",
        "concentration_display",
        "risk_text",
        "sell_display",
        "hold_display",
        "post_vesting_display",
        "future_net_display",
    ):
        lines.append(f"- `{key}`: {sample[key]}")
    lines.extend(["", "## Cases", ""])
    for case, result in zip(cases, expected):
        lines.append(
            f"- `{case['name']}` ({case['option_type']}): net {result['net_display']}, "
            f"vesting tax {result['vesting_tax_display']}, concentration {result['concentration_display']} "
            f"{result['risk_text']}, chart {', '.join(result['future_net_display'])}"
        )
    if errors:
        lines.extend(["", "## Failures", ""])
        lines.extend(f"- {err}" for err in errors)
    else:
        lines.extend(["", "All cases matched.", ""])
    RESULTS_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    cases = build_cases()
    expected = [legacy(case) for case in cases]
    formats = formatter_samples()
    js = run_js_clean(cases, formats)
    errors: list[str] = []
    max_abs = 0.0
    for case, exp, got_js in zip(cases, expected, js["cases"]):
        py = compute_exec_comp(
            price=case["price"],
            total_shares=case["total_shares"],
            option_type=case["option_type"],
            strike=case["strike"],
            federal_tax_rate=case["federal_tax_rate"],
            amt_rate=case["amt_rate"],
            shares_vesting=case["shares_vesting"],
            next_vesting_date=case["next_vesting_date"],
            net_worth=case["net_worth"],
            today=case["today"],
        )
        errors.extend(compare(case["name"], exp, py, "calc.py"))
        errors.extend(compare(case["name"], exp, got_js, "js"))
        for key in NUMERIC_KEYS:
            max_abs = max(max_abs, abs(float(exp[key]) - float(got_js[key])))
        for exp_v, got_v in zip(exp["future_net"], got_js["future_net"]):
            max_abs = max(max_abs, abs(float(exp_v) - float(got_v)))

    format_bad = 0
    for spec, got in zip(formats, js["formats"]):
        n, d, g = spec["n"], spec["d"], spec["g"]
        want = f"{n:,.{d}f}" if g else f"{n:.{d}f}"
        if want != got:
            format_bad += 1
            if format_bad <= 8:
                errors.append(f"format {n!r} d={d} g={g}: python {want!r} js {got!r}")
    if format_bad > 8:
        errors.append(f"... {format_bad} formatter mismatches total")

    errors.extend(quirk_errors(cases, expected))
    errors.extend(secrets_errors())
    write_report(cases, expected, errors, len(formats), format_bad)

    print(f"Cases: {len(cases)}")
    print(f"Formatter samples: {len(formats)} (mismatches {format_bad})")
    print(f"Max absolute numeric delta (JS vs Python formulas): {max_abs:.3g}")
    print(f"Mismatches: {len(errors)}")
    for err in errors[:30]:
        print(" -", err)
    print(f"Wrote {RESULTS_PATH.relative_to(ROOT)}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
