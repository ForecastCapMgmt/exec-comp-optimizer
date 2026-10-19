"""Pure math for the Exec Comp Optimizer.

These formulas are the ones the Streamlit app applies. A few of them are
asymmetric on purpose so the client-side page can match the original tool:

- RSU tax uses the full market value. NSO tax uses the bargain element
  (price minus strike, floored at zero) and the federal rate. ISO tax on the
  next vesting date uses the AMT rate on that same bargain element.
- Headline net value for an ISO uses the vesting tranche after AMT, plus
  strike times every share in the grant. NSO headline net value uses the
  whole grant.
- The one-year growth chart uses the federal rate and the whole grant for
  both NSO and ISO. It does not use the AMT rate.
- A missing or zero price becomes $150, which is what the Streamlit app does
  when a live quote is unavailable.
"""

from __future__ import annotations

from datetime import date


GROWTH_RATES = (0.0, 0.05, 0.10, 0.15, 0.20)


def _as_date(value: date | str) -> date:
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value))


def _coerce_price(price: float | None) -> float:
    # Mirrors `if not price: price = 150.0` in app.py. Negative prices are kept.
    if price is None or price == "" or price == 0:
        return 150.0
    return float(price)


def _fmt_shares(shares: float) -> str:
    number = float(shares)
    if number.is_integer():
        return f"{int(number):,}"
    return f"{number:,}"


def compute_exec_comp(
    *,
    price: float | None,
    total_shares: float,
    option_type: str,
    strike: float,
    federal_tax_rate: float,
    amt_rate: float,
    shares_vesting: float,
    next_vesting_date: date | str,
    net_worth: float,
    today: date | str | None = None,
) -> dict:
    """Return every figure the Streamlit results view prints."""
    price = _coerce_price(price)
    total_shares = float(total_shares)
    strike = float(strike)
    federal_tax_rate = float(federal_tax_rate)
    amt_rate = float(amt_rate)
    shares_vesting = float(shares_vesting)
    net_worth = float(net_worth)
    vesting_date = _as_date(next_vesting_date)
    as_of = _as_date(today) if today is not None else date.today()

    gross_value = price * total_shares
    intrinsic_value = max(0.0, price - strike) * total_shares
    vesting_gross = price * shares_vesting
    vesting_intrinsic = max(0.0, price - strike) * shares_vesting

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

    days_to_vesting = (vesting_date - as_of).days
    months_to_vesting = max(0, days_to_vesting // 30)
    shares_fmt = _fmt_shares(shares_vesting)
    if months_to_vesting <= 3:
        timing_advice = (
            f"With {shares_fmt} shares vesting in the next {months_to_vesting} months, "
            "plan for the immediate tax impact."
        )
    elif months_to_vesting <= 12:
        timing_advice = (
            f"{shares_fmt} shares vesting in about {months_to_vesting} months "
            "gives you planning time."
        )
    else:
        timing_advice = "Vesting is further out — good opportunity to model scenarios."

    recommendation = f"{base_rec} {timing_advice}"

    position_value = gross_value if option_type == "RSU" else (intrinsic_value + total_shares * strike)
    concentration_pct = (position_value / net_worth * 100) if net_worth > 0 else 0.0
    vesting_concentration = (vesting_gross / net_worth * 100) if net_worth > 0 else 0.0

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

    future_net: list[float] = []
    for rate in GROWTH_RATES:
        future_price = price * (1 + rate)
        if option_type == "RSU":
            future_net.append(future_price * total_shares * (1 - federal_tax_rate / 100))
        else:
            future_intrinsic = max(0.0, future_price - strike) * total_shares
            future_net.append(
                future_intrinsic * (1 - federal_tax_rate / 100) + total_shares * strike
            )

    sell_after_tax = (
        vesting_gross * (1 - federal_tax_rate / 100)
        if option_type == "RSU"
        else (vesting_intrinsic * (1 - federal_tax_rate / 100))
    )
    hold_value = (
        vesting_gross
        if option_type == "RSU"
        else vesting_intrinsic + shares_vesting * strike
    )
    post_vesting_conc = (
        ((position_value + vesting_gross) / net_worth * 100) if net_worth > 0 else 0.0
    )

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
        "growth_rates": list(GROWTH_RATES),
        "growth_labels": [f"{int(rate * 100)}%" for rate in GROWTH_RATES],
        "future_net": future_net,
        "future_net_display": [f"${value:,.0f}" for value in future_net],
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
