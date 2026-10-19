# Parity results

Python source of truth: the original Streamlit formulas (transcribed in `tests/test_parity.py`) and `calc.py`, which `app.py` calls.
JavaScript: `fcmComputeExecComp` in `web/exec-comp-optimizer.html`.

- Cases: 33
- Mismatches: 0
- Formatter samples checked against Python `format`: 852
- Formatter mismatches: 0
- Numeric tolerance: absolute 1e-6 (display strings must match exactly, including half-even rounding)

## Worked example (default RSU, price $150, 5,000 shares, 32% federal, vest today)

- `price_display`: $150.00
- `gross_display`: $750,000
- `net_display`: $510,000
- `vesting_tax_display`: $60,000
- `tax_note`: RSU: Est. tax on next vesting ≈ $60,000
- `recommendation`: RSUs are taxed as ordinary income upon vesting. With 1,250 shares vesting in the next 0 months, plan for the immediate tax impact.
- `concentration_display`: 37.5%
- `risk_text`: High — consider diversifying
- `sell_display`: $127,500
- `hold_display`: $187,500
- `post_vesting_display`: 46.9%
- `future_net_display`: ['$510,000', '$535,500', '$561,000', '$586,500', '$612,000']

## Cases

- `default_rsu_vests_today` (RSU): net $510,000, vesting tax $60,000, concentration 37.5% High — consider diversifying, chart $510,000, $535,500, $561,000, $586,500, $612,000
- `rsu_three_months` (RSU): net $510,000, vesting tax $60,000, concentration 37.5% High — consider diversifying, chart $510,000, $535,500, $561,000, $586,500, $612,000
- `rsu_just_under_four_months` (RSU): net $510,000, vesting tax $60,000, concentration 37.5% High — consider diversifying, chart $510,000, $535,500, $561,000, $586,500, $612,000
- `rsu_four_months` (RSU): net $510,000, vesting tax $60,000, concentration 37.5% High — consider diversifying, chart $510,000, $535,500, $561,000, $586,500, $612,000
- `rsu_twelve_months` (RSU): net $510,000, vesting tax $60,000, concentration 37.5% High — consider diversifying, chart $510,000, $535,500, $561,000, $586,500, $612,000
- `rsu_just_over_twelve_months_calendar` (RSU): net $510,000, vesting tax $60,000, concentration 37.5% High — consider diversifying, chart $510,000, $535,500, $561,000, $586,500, $612,000
- `rsu_further_out` (RSU): net $510,000, vesting tax $60,000, concentration 37.5% High — consider diversifying, chart $510,000, $535,500, $561,000, $586,500, $612,000
- `rsu_past_date` (RSU): net $510,000, vesting tax $60,000, concentration 37.5% High — consider diversifying, chart $510,000, $535,500, $561,000, $586,500, $612,000
- `rsu_tax_22` (RSU): net $585,000, vesting tax $41,250, concentration 37.5% High — consider diversifying, chart $585,000, $614,250, $643,500, $672,750, $702,000
- `rsu_tax_37` (RSU): net $472,500, vesting tax $69,375, concentration 37.5% High — consider diversifying, chart $472,500, $496,125, $519,750, $543,375, $567,000
- `rsu_zero_vesting_shares` (RSU): net $510,000, vesting tax $0, concentration 37.5% High — consider diversifying, chart $510,000, $535,500, $561,000, $586,500, $612,000
- `rsu_min_grant` (RSU): net $680, vesting tax $80, concentration 1.0% Low, chart $680, $714, $748, $782, $816
- `price_zero_falls_back_to_150` (RSU): net $510,000, vesting tax $60,000, concentration 37.5% High — consider diversifying, chart $510,000, $535,500, $561,000, $586,500, $612,000
- `price_null_falls_back_to_150` (RSU): net $510,000, vesting tax $60,000, concentration 37.5% High — consider diversifying, chart $510,000, $535,500, $561,000, $586,500, $612,000
- `fractional_price` (RSU): net $209,865, vesting tax $24,690, concentration 15.4% Moderate, chart $209,865, $220,358, $230,852, $241,345, $251,838
- `concentration_exact_10` (RSU): net $68,000, vesting tax $3,200, concentration 10.0% Moderate, chart $68,000, $71,400, $74,800, $78,200, $81,600
- `concentration_just_under_10_displays_10` (RSU): net $68,000, vesting tax $3,200, concentration 10.0% Low, chart $68,000, $71,400, $74,800, $78,200, $81,600
- `concentration_exact_20` (RSU): net $68,000, vesting tax $3,200, concentration 20.0% High — consider diversifying, chart $68,000, $71,400, $74,800, $78,200, $81,600
- `concentration_just_under_20` (RSU): net $68,000, vesting tax $3,200, concentration 20.0% Moderate, chart $68,000, $71,400, $74,800, $78,200, $81,600
- `concentration_over_100` (RSU): net $680,000, vesting tax $32,000, concentration 1000.0% High — consider diversifying, chart $680,000, $714,000, $748,000, $782,000, $816,000
- `vesting_concentration_exact_5` (RSU): net $68,000, vesting tax $16,000, concentration 10.0% Moderate, chart $68,000, $71,400, $74,800, $78,200, $81,600
- `vesting_concentration_just_over_5` (RSU): net $68,000, vesting tax $16,016, concentration 10.0% Moderate, chart $68,000, $71,400, $74,800, $78,200, $81,600
- `vesting_warning_rounds_to_5_display` (RSU): net $136,000, vesting tax $16,128, concentration 20.0% High — consider diversifying, chart $136,000, $142,800, $149,600, $156,400, $163,200
- `net_worth_zero` (RSU): net $68,000, vesting tax $40,000, concentration 0.0% Low, chart $68,000, $71,400, $74,800, $78,200, $81,600
- `nso_in_the_money` (NSO): net $80,800, vesting tax $1,920, concentration 6.7% Low, chart $80,800, $84,200, $87,600, $91,000, $94,400
- `nso_out_of_the_money_until_growth` (NSO): net $42,000, vesting tax $0, concentration 5.2% Low, chart $42,000, $42,000, $43,360, $44,720, $46,080
- `nso_price_equals_strike` (NSO): net $225,000, vesting tax $0, concentration 11.2% Moderate, chart $225,000, $232,650, $240,300, $247,950, $255,600
- `nso_strike_zero` (NSO): net $91,200, vesting tax $5,760, concentration 6.0% Low, chart $91,200, $95,760, $100,320, $104,880, $109,440
- `iso_amt_26` (ISO): net $44,440, vesting tax $1,560, concentration 6.7% Low, chart $80,800, $84,200, $87,600, $91,000, $94,400
- `iso_amt_zero` (ISO): net $46,000, vesting tax $0, concentration 5.0% Low, chart $77,800, $80,950, $84,100, $87,250, $90,400
- `iso_amt_28` (ISO): net $460,760, vesting tax $131,740, concentration 40.1% High — consider diversifying, chart $1,345,300, $1,410,430, $1,475,560, $1,540,690, $1,605,820
- `large_grant` (RSU): net $441,315,000, vesting tax $16,199,062, concentration 1401.0% High — consider diversifying, chart $441,315,000, $463,380,750, $485,446,500, $507,512,250, $529,578,000
- `negative_price_kept` (NSO): net $10,000, vesting tax $0, concentration 0.5% Low, chart $10,000, $10,000, $10,000, $10,000, $10,000

All cases matched.

