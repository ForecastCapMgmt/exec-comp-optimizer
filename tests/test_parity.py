#!/usr/bin/env python3
"""Compare app.py's formulas (via tests/reference_model.py) with the JavaScript
embedded in web/exec-comp-optimizer.html.

Run from the repository root:

    python3 tests/test_parity.py
"""

from __future__ import annotations

import json
import random
import re
import subprocess
import sys
import tempfile
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))

from reference_model import calculate  # noqa: E402

HTML_PATH = ROOT / "web" / "exec-comp-optimizer.html"
ABS_TOL = 1e-6

NUMERIC_KEYS = (
    "price",
    "grossValue",
    "intrinsicValue",
    "vestingGross",
    "vestingIntrinsic",
    "vestingTax",
    "netValue",
    "daysToVesting",
    "monthsToVesting",
    "positionValue",
    "concentrationPct",
    "vestingConcentration",
    "sellAfterTax",
    "holdValue",
    "postVestingConc",
    "strikeTimesShares",
)

LIST_KEYS = ("futurePrices", "futureNet", "futurePricesWide", "futureNetWide")
EXACT_KEYS = ("taxNote", "timingBand", "riskBand", "growthLabels", "wideLabels", "showVestingWarning")

FORBIDDEN_PHRASES = (
    "you should",
    "consider diversif",
    "we recommend",
    "recommended",
    "plan for",
    "you must",
    "you need to",
    "unlock",
)

# Hand-computed from the formulas in app.py. Both engines must hit these,
# so a bug copied into Python and JavaScript still fails.
HAND_EXPECTATIONS = {
    "rsu-default": {
        "grossValue": 750_000,
        "netValue": 510_000,
        "vestingGross": 187_500,
        "vestingTax": 60_000,
        "intrinsicValue": 525_000,
        "concentrationPct": 37.5,
        "vestingConcentration": 9.375,
        "daysToVesting": 0,
        "monthsToVesting": 0,
        "timingBand": "near",
        "riskBand": "high",
        "showVestingWarning": True,
        "futureNet": [510_000, 535_500, 561_000, 586_500, 612_000],
        "sellAfterTax": 127_500,
        "holdValue": 187_500,
        "postVestingConc": 46.875,
        "taxNote": "RSU: Est. tax on next vesting ≈ $60,000",
    },
    "nso-itm": {
        "intrinsicValue": 525_000,
        "vestingIntrinsic": 131_250,
        "vestingTax": 42_000,
        "netValue": 582_000,
        "positionValue": 750_000,
        "sellAfterTax": 89_250,
        "holdValue": 187_500,
        "futureNet": [582_000, 607_500, 633_000, 658_500, 684_000],
        "taxNote": "NSO: Est. tax on next vesting spread ≈ $42,000",
        "riskBand": "high",
    },
    "iso-itm": {
        "vestingTax": 34_125,
        "netValue": 322_125,
        # Chart uses the federal rate and the full grant, so 0% is not the headline net.
        "futureNet": [582_000, 607_500, 633_000, 658_500, 684_000],
        "taxNote": "ISO: Est. AMT on next vesting spread ≈ $34,125",
        "sellAfterTax": 89_250,
    },
    "nso-otm": {
        "intrinsicValue": 0,
        "vestingTax": 0,
        "netValue": 225_000,
        "positionValue": 225_000,
        "concentrationPct": 11.25,
        "riskBand": "moderate",
        "futureNet": [225_000, 225_000, 225_000, 225_000, 225_000],
        "sellAfterTax": 0,
        "holdValue": 56_250,
    },
    "rsu-conc-10": {
        "concentrationPct": 10,
        "riskBand": "moderate",
    },
    "rsu-conc-just-under-10": {
        "riskBand": "low",
    },
    "rsu-conc-20": {
        "concentrationPct": 20,
        "riskBand": "high",
    },
    "months-119": {"daysToVesting": 119, "monthsToVesting": 3, "timingBand": "near"},
    "months-120": {"daysToVesting": 120, "monthsToVesting": 4, "timingBand": "mid"},
    "months-389": {"daysToVesting": 389, "monthsToVesting": 12, "timingBand": "mid"},
    "months-390": {"daysToVesting": 390, "monthsToVesting": 13, "timingBand": "far"},
    "vesting-warning-at-5": {"vestingConcentration": 5, "showVestingWarning": False},
    "leap-day": {"daysToVesting": 2},
    "non-leap": {"daysToVesting": 1},
    "past-date": {"daysToVesting": -10, "monthsToVesting": 0, "timingBand": "near"},
    "zero-vesting-shares": {"vestingTax": 0, "vestingConcentration": 0, "showVestingWarning": False},
    "zero-net-worth": {"concentrationPct": 0, "vestingConcentration": 0, "postVestingConc": 0},
    "amt-zero": {"vestingTax": 0},
    "amt-28": {"vestingTax": 36_750},
    "rate-22": {"netValue": 585_000, "vestingTax": 41_250},
    "rate-37": {"netValue": 472_500, "vestingTax": 69_375},
    "price-equals-strike": {"intrinsicValue": 0, "netValue": 225_000},
}


def base_input(**overrides):
    data = {
        "ticker": "AAPL",
        "totalShares": 5000,
        "optionType": "RSU",
        "strike": 45.0,
        "federalTaxRate": 32,
        "amtRate": 26,
        "nextVestingDate": "2026-10-19",
        "sharesVesting": 1250,
        "netWorth": 2_000_000,
        "price": 150.0,
        "asOf": "2026-10-19",
    }
    data.update(overrides)
    return data


def shift(as_of, days):
    year, month, day = (int(part) for part in as_of.split("-"))
    return (date(year, month, day) + timedelta(days=days)).isoformat()


def cases():
    as_of = "2026-10-19"
    named = {
        "rsu-default": base_input(),
        "nso-itm": base_input(optionType="NSO"),
        "iso-itm": base_input(optionType="ISO", amtRate=26),
        "nso-otm": base_input(optionType="NSO", price=20.0, strike=45.0),
        "rsu-conc-10": base_input(price=100.0, totalShares=5000, netWorth=5_000_000),
        "rsu-conc-just-under-10": base_input(price=100.0, totalShares=5000, netWorth=5_000_001),
        "rsu-conc-20": base_input(price=100.0, totalShares=5000, netWorth=2_500_000),
        "months-119": base_input(nextVestingDate=shift(as_of, 119)),
        "months-120": base_input(nextVestingDate=shift(as_of, 120)),
        "months-389": base_input(nextVestingDate=shift(as_of, 389)),
        "months-390": base_input(nextVestingDate=shift(as_of, 390)),
        "vesting-warning-at-5": base_input(price=100.0, sharesVesting=1000, netWorth=2_000_000),
        "leap-day": base_input(asOf="2028-02-28", nextVestingDate="2028-03-01"),
        "non-leap": base_input(asOf="2027-02-28", nextVestingDate="2027-03-01"),
        "past-date": base_input(asOf="2026-10-19", nextVestingDate="2026-10-09"),
        "zero-vesting-shares": base_input(sharesVesting=0),
        "zero-net-worth": base_input(netWorth=0),
        "amt-zero": base_input(optionType="ISO", amtRate=0),
        "amt-28": base_input(optionType="ISO", amtRate=28),
        "rate-22": base_input(federalTaxRate=22),
        "rate-37": base_input(federalTaxRate=37),
        "price-equals-strike": base_input(optionType="NSO", price=45.0, strike=45.0),
        "fractional-price": base_input(price=150.01, strike=45.55, federalTaxRate=35, sharesVesting=100),
        "min-shares": base_input(totalShares=100, sharesVesting=100, price=0.01, strike=0),
        "vest-exceeds-grant": base_input(totalShares=100, sharesVesting=5000),
        "large-grant": base_input(totalShares=250_000, sharesVesting=50_000, price=999.99, netWorth=100_000),
        "cross-strike-on-growth": base_input(optionType="NSO", price=50.0, strike=55.0),
    }
    rng = random.Random(6382)
    generated = []
    for index in range(48):
        as_of_date = date(2026, 10, 19)
        delta = rng.choice([0, 1, 29, 30, 89, 90, 119, 120, 360, 361, 389, 390, -5, 800, -40])
        generated.append(
            (
                f"random-{index}",
                base_input(
                    ticker="T",
                    optionType=rng.choice(["RSU", "NSO", "ISO"]),
                    price=rng.choice([0.01, 1, 20, 45, 45.01, 150, 150.5, 999.99, 5000]),
                    strike=rng.choice([0, 0.01, 10, 45, 150, 200, 1000]),
                    totalShares=rng.choice([100, 101, 1250, 5000, 10_000, 250_000]),
                    sharesVesting=rng.choice([0, 1, 100, 1250, 5000, 9000]),
                    federalTaxRate=rng.randint(22, 37),
                    amtRate=rng.randint(0, 28),
                    netWorth=rng.choice([0, 100_000, 2_000_000, 5_000_000, 5_000_001, 10_000_000]),
                    asOf=as_of_date.isoformat(),
                    nextVestingDate=(as_of_date + timedelta(days=delta)).isoformat(),
                ),
            )
        )
    return list(named.items()) + generated


def extract_library():
    html = HTML_PATH.read_text(encoding="utf-8")
    match = re.search(
        r"/\* FCM_ECO_LIB_START \*/(.*)/\* FCM_ECO_LIB_END \*/",
        html,
        re.S,
    )
    if not match:
        raise SystemExit("Could not find FCM_ECO_LIB markers in the HTML file.")
    return match.group(1)


def run_js(library, payload):
    harness = r"""
const fs = require("fs");
const payload = JSON.parse(fs.readFileSync(0, "utf8"));
const calculated = payload.cases.map((item) => globalThis.fcmEcoCalculate(item.input));
const narratives = calculated.map((calc, index) => globalThis.fcmEcoNarrative(calc, payload.cases[index].input));
const validations = payload.validations.map((item) => globalThis.fcmEcoValidate(item));
const formatted = payload.formatSamples.map((sample) => ({
  n: sample.n,
  d: sample.d,
  js: globalThis.fcmEcoFormatFixed(sample.n, sample.d),
}));
process.stdout.write(JSON.stringify({ calculated, narratives, validations, formatted }));
"""
    with tempfile.TemporaryDirectory() as tmp:
        script = Path(tmp) / "run.js"
        script.write_text(library + "\n" + harness, encoding="utf-8")
        proc = subprocess.run(
            ["node", str(script)],
            input=json.dumps(payload),
            text=True,
            capture_output=True,
            check=False,
        )
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr)
        raise SystemExit(f"node exited {proc.returncode}")
    return json.loads(proc.stdout)


def close(left, right):
    return abs(float(left) - float(right)) <= ABS_TOL


def same_value(actual, expected):
    if isinstance(expected, bool):
        return actual is expected or actual == expected
    if isinstance(expected, str):
        return actual == expected
    if isinstance(expected, list):
        return (
            isinstance(actual, list)
            and len(actual) == len(expected)
            and all(same_value(item, want) for item, want in zip(actual, expected))
        )
    if isinstance(expected, (int, float)):
        return close(actual, expected)
    return actual == expected


def walk_strings(value, found):
    if isinstance(value, str):
        found.append(value)
    elif isinstance(value, dict):
        for item in value.values():
            walk_strings(item, found)
    elif isinstance(value, list):
        for item in value:
            walk_strings(item, found)


def static_html_checks(failures):
    html = HTML_PATH.read_text(encoding="utf-8")
    required = [
        "For educational purposes only; not investment, tax, or legal advice. Forecast Capital Management is a registered investment adviser. Results are hypothetical estimates based on your inputs.",
        "FCM_ECO_CONFIG",
        "subscribeUrl",
        "https://go.forecastcapitalmanagement.com/api/subscribe",
        'mode: "no-cors"',
        "text/plain;charset=UTF-8",
        "You're on the list. Check your inbox for the Forecast Report.",
        "calculation_completed",
        "dataLayer",
        "https://www.forecastcapitalmanagement.com/contact",
        "Want a second set of eyes?",
        "Cormorant Garamond",
        "Lora",
        'id="fcm-eco"',
        "Get The Friday 5",
        "Send me The Friday 5",
        "One short email every Friday: what moved markets in plain English, plus a podcast, a read, a live-well tip, and a quote worth thinking about. Five minutes. As a bonus, we'll send you the most recent Forecast Report.",
        "By joining, you agree to receive occasional emails from Forecast Capital Management. Unsubscribe anytime.",
        "Want a copy? Print or save this illustration as a PDF.",
    ]
    for snippet in required:
        if snippet not in html:
            failures.append(f"HTML is missing {snippet!r}")
    lowered = html.lower()
    for banned in (
        "smtp.gmail.com",
        "sender_password",
        "sender_email",
        "smtplib",
        "calendly",
        "replace-with-your-form-endpoint",
        "email me my results",
        "thanks — check your inbox.",
    ):
        if banned in lowered:
            failures.append(f"HTML contains {banned}")
    app = (ROOT / "app.py").read_text(encoding="utf-8")
    for snippet in (
        "gross_value = price * total_shares",
        "net_value = gross_value * (1 - federal_tax_rate / 100)",
        "st.secrets",
    ):
        if snippet not in app:
            failures.append(f"app.py no longer contains {snippet!r}")
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    if "secrets.toml" not in gitignore:
        failures.append(".gitignore does not mention secrets.toml")
    tracked = subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True).splitlines()
    if "secrets.toml" in tracked or ".streamlit/secrets.toml" in tracked:
        failures.append("secrets.toml is still tracked by git")
    if "app.py" not in tracked:
        failures.append("app.py is missing from git")


def validation_cases():
    good = base_input()
    return [
        good,
        dict(good, price=0),
        dict(good, price=-5),
        dict(good, totalShares=50),
        dict(good, totalShares=100.5),
        dict(good, sharesVesting=9000),
        dict(good, nextVestingDate="2020-01-01"),
        dict(good, federalTaxRate=21),
        dict(good, federalTaxRate=38),
        dict(good, optionType="ISO", amtRate=29),
        dict(good, netWorth=1000),
        dict(good, strike=-1),
        dict(good, ticker="not a ticker"),
        dict(good, optionType="ISO"),
    ]


def format_samples():
    samples = []
    fixed = [
        0, 0.5, 1.5, 2.5, 3.5, 10.5, -1.5, -0.5, -2.5, 34125.5, 100.25, 9.375,
        37.5, 46.875, 11.25, 1.25, 2.25, 1.005, 2.675, 1234567.5, 999.5, 150,
        510000, 9.95, 99.995, 8.5, 9.5, -0.4, 187500, 89250, 322125,
    ]
    for number in fixed:
        for digits in (0, 1, 2):
            samples.append({"n": number, "d": digits})
    rng = random.Random(19)
    for _ in range(300):
        number = (rng.random() - 0.25) * (10 ** rng.randint(0, 7))
        samples.append({"n": number, "d": rng.choice([0, 1, 2])})
    return samples


def main():
    failures = []
    static_html_checks(failures)
    library = extract_library()
    named_cases = cases()
    payload = {
        "cases": [{"name": name, "input": data} for name, data in named_cases],
        "validations": validation_cases(),
        "formatSamples": format_samples(),
    }
    js = run_js(library, payload)
    max_diff = 0.0
    comparisons = 0

    if len(js["calculated"]) != len(named_cases):
        failures.append("JS returned the wrong number of cases")

    for (name, data), calc_js, narrative in zip(named_cases, js["calculated"], js["narratives"]):
        calc_py = calculate(data)
        for key in NUMERIC_KEYS:
            comparisons += 1
            diff = abs(float(calc_py[key]) - float(calc_js[key]))
            max_diff = max(max_diff, diff)
            if diff > ABS_TOL:
                failures.append(f"{name} {key}: python={calc_py[key]!r} js={calc_js[key]!r}")
        for key in LIST_KEYS:
            left = calc_py[key]
            right = calc_js[key]
            if len(left) != len(right):
                failures.append(f"{name} {key} length {len(left)} != {len(right)}")
                continue
            for index, (py_value, js_value) in enumerate(zip(left, right)):
                comparisons += 1
                diff = abs(float(py_value) - float(js_value))
                max_diff = max(max_diff, diff)
                if diff > ABS_TOL:
                    failures.append(
                        f"{name} {key}[{index}]: python={py_value!r} js={js_value!r}"
                    )
        for key in EXACT_KEYS:
            comparisons += 1
            if calc_py[key] != calc_js[key]:
                failures.append(f"{name} {key}: python={calc_py[key]!r} js={calc_js[key]!r}")
        for key, py_value in calc_py["display"].items():
            comparisons += 1
            js_value = calc_js["display"][key]
            if py_value != js_value:
                failures.append(f"{name} display.{key}: python={py_value!r} js={js_value!r}")
        expect = HAND_EXPECTATIONS.get(name, {})
        for key, expected in expect.items():
            actual = calc_py[key]
            js_actual = calc_js[key]
            if not same_value(actual, expected) or not same_value(js_actual, expected):
                failures.append(f"{name} hand {key}: {actual!r} / {js_actual!r} != {expected!r}")
        texts = []
        walk_strings(narrative, texts)
        blob = "\n".join(texts).lower()
        for phrase in FORBIDDEN_PHRASES:
            if phrase in blob:
                failures.append(f"{name} narrative contains {phrase!r}")
        if calc_py["display"]["netValue"] not in texts and calc_py["display"]["netValue"] not in blob:
            # summary is one string; membership in joined text is enough
            if calc_py["display"]["netValue"] not in blob:
                failures.append(f"{name} narrative omits net figure {calc_py['display']['netValue']}")

    validations = js["validations"]
    expected_ok = [True, False, False, False, False, True, True, False, False, False, False, False, True, True]
    expected_warn = {
        5: "sharesVesting",
        6: "nextVestingDate",
        12: "ticker",
    }
    if len(validations) != len(expected_ok):
        failures.append("validation count mismatch")
    else:
        for index, (result, ok) in enumerate(zip(validations, expected_ok)):
            if result["ok"] is not ok:
                failures.append(f"validation[{index}] ok={result['ok']} errors={result['errors']}")
            if index in expected_warn:
                fields = [item["field"] for item in result["warnings"]]
                if expected_warn[index] not in fields:
                    failures.append(f"validation[{index}] missing warning {expected_warn[index]}")

    format_failures = 0
    for sample, formatted in zip(payload["formatSamples"], js["formatted"]):
        py_text = format(sample["n"], f",.{sample['d']}f")
        if py_text != formatted["js"]:
            format_failures += 1
            if format_failures <= 8:
                failures.append(
                    f"format {sample['n']!r} digits {sample['d']}: python={py_text!r} js={formatted['js']!r}"
                )
    if format_failures > 8:
        failures.append(f"{format_failures} formatter mismatches (showing the first 8)")

    from test_optin import collect_failures

    failures.extend(collect_failures(HTML_PATH))

    print("Exec comp optimizer parity")
    print(f"  cases: {len(named_cases)}")
    print(f"  numeric comparisons: {comparisons}")
    print(f"  max abs diff: {max_diff:.3e}")
    print(f"  formatter samples: {len(payload['formatSamples'])}")
    print(f"  hand-checked fixtures: {len(HAND_EXPECTATIONS)}")
    if failures:
        print(f"  FAILED: {len(failures)}")
        for item in failures:
            print(f"  - {item}")
        return 1
    print("  result: pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
