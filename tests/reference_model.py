"""Pure-Python mirror of the calculations in app.py.

The formulas are copied to match the Streamlit tool, including behaviors that
are easy to misread:

- NSO "net" is the after-tax bargain element on the full grant, plus strike
  times every share.
- ISO "net" is the next tranche's bargain element minus estimated AMT, plus
  strike times every share in the grant (not just the tranche).
- The growth chart uses the federal rate and the full grant for NSOs and ISOs.
- Post-vesting concentration adds the next tranche's pretax value on top of
  the full-grant position value.
- A month is 30 days, integer division, never negative.

`future_net_wide` is not shown in app.py. It applies the same future-net
formula at extra growth rates so the page can show a down move.
"""

from datetime import date


GROWTH_RATES = (0.0, 0.05, 0.10, 0.15, 0.20)
WIDE_RATES = (-0.20, -0.10, 0.0, 0.10, 0.20)


def _iso_date(iso):
    year, month, day = (int(part) for part in iso.split("-"))
    return date(year, month, day)


def days_between(as_of, vesting):
    return (_iso_date(vesting) - _iso_date(as_of)).days


def growth_label(rate):
    return f"{int(rate * 100)}%"


def future_point(price, rate, option_type, total_shares, strike, federal_tax_rate):
    future_price = price * (1 + rate)
    if option_type == "RSU":
        net = future_price * total_shares * (1 - federal_tax_rate / 100)
    else:
        intrinsic = max(0, future_price - strike) * total_shares
        net = intrinsic * (1 - federal_tax_rate / 100) + total_shares * strike
    return future_price, net


def calculate(inputs):
    price = inputs["price"]
    total_shares = inputs["totalShares"]
    option_type = inputs["optionType"]
    strike = inputs["strike"]
    federal_tax_rate = inputs["federalTaxRate"]
    amt_rate = inputs["amtRate"]
    shares_vesting = inputs["sharesVesting"]
    net_worth = inputs["netWorth"]

    gross_value = price * total_shares
    intrinsic_value = max(0, price - strike) * total_shares
    vesting_gross = price * shares_vesting
    vesting_intrinsic = max(0, price - strike) * shares_vesting

    if option_type == "RSU":
        vesting_tax = vesting_gross * (federal_tax_rate / 100)
        net_value = gross_value * (1 - federal_tax_rate / 100)
        tax_note = f"RSU: Est. tax on next vesting ≈ ${vesting_tax:,.0f}"
    else:
        if option_type == "NSO":
            vesting_tax = vesting_intrinsic * (federal_tax_rate / 100)
        else:
            vesting_tax = vesting_intrinsic * (amt_rate / 100)
        if option_type != "ISO":
            net_value = (intrinsic_value * (1 - federal_tax_rate / 100)) + (
                total_shares * strike
            )
        else:
            net_value = (vesting_intrinsic - vesting_tax) + (total_shares * strike)
        if option_type == "ISO":
            tax_note = f"ISO: Est. AMT on next vesting spread ≈ ${vesting_tax:,.0f}"
        else:
            tax_note = f"NSO: Est. tax on next vesting spread ≈ ${vesting_tax:,.0f}"

    days_to_vesting = days_between(inputs["asOf"], inputs["nextVestingDate"])
    months_to_vesting = max(0, days_to_vesting // 30)
    if months_to_vesting <= 3:
        timing_band = "near"
    elif months_to_vesting <= 12:
        timing_band = "mid"
    else:
        timing_band = "far"

    if option_type == "RSU":
        position_value = gross_value
    else:
        position_value = intrinsic_value + total_shares * strike

    if net_worth > 0:
        concentration_pct = position_value / net_worth * 100
        vesting_concentration = vesting_gross / net_worth * 100
        post_vesting_conc = (position_value + vesting_gross) / net_worth * 100
    else:
        concentration_pct = 0
        vesting_concentration = 0
        post_vesting_conc = 0

    if concentration_pct < 10:
        risk_band = "low"
    elif concentration_pct < 20:
        risk_band = "moderate"
    else:
        risk_band = "high"

    future = [
        future_point(price, rate, option_type, total_shares, strike, federal_tax_rate)
        for rate in GROWTH_RATES
    ]
    future_wide = [
        future_point(price, rate, option_type, total_shares, strike, federal_tax_rate)
        for rate in WIDE_RATES
    ]

    if option_type == "RSU":
        sell_after_tax = vesting_gross * (1 - federal_tax_rate / 100)
        hold_value = vesting_gross
    else:
        sell_after_tax = vesting_intrinsic * (1 - federal_tax_rate / 100)
        hold_value = vesting_intrinsic + shares_vesting * strike

    return {
        "price": price,
        "grossValue": gross_value,
        "intrinsicValue": intrinsic_value,
        "vestingGross": vesting_gross,
        "vestingIntrinsic": vesting_intrinsic,
        "vestingTax": vesting_tax,
        "netValue": net_value,
        "taxNote": tax_note,
        "daysToVesting": days_to_vesting,
        "monthsToVesting": months_to_vesting,
        "timingBand": timing_band,
        "positionValue": position_value,
        "concentrationPct": concentration_pct,
        "vestingConcentration": vesting_concentration,
        "showVestingWarning": vesting_concentration > 5,
        "riskBand": risk_band,
        "growthLabels": [growth_label(rate) for rate in GROWTH_RATES],
        "futurePrices": [point[0] for point in future],
        "futureNet": [point[1] for point in future],
        "wideLabels": [growth_label(rate) for rate in WIDE_RATES],
        "futurePricesWide": [point[0] for point in future_wide],
        "futureNetWide": [point[1] for point in future_wide],
        "sellAfterTax": sell_after_tax,
        "holdValue": hold_value,
        "postVestingConc": post_vesting_conc,
        "strikeTimesShares": total_shares * strike,
        "display": {
            "price": f"${price:,.2f}",
            "grossValue": f"${gross_value:,.0f}",
            "netValue": f"${net_value:,.0f}",
            "vestingTax": f"${vesting_tax:,.0f}",
            "concentrationPct": f"{concentration_pct:,.1f}",
            "vestingConcentration": f"{vesting_concentration:,.1f}",
            "sellAfterTax": f"${sell_after_tax:,.0f}",
            "holdValue": f"${hold_value:,.0f}",
            "postVestingConc": f"{post_vesting_conc:,.1f}",
            "futureNet": [f"${value:,.0f}" for value in (point[1] for point in future)],
        },
    }
