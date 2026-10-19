# exec-comp-optimizer

Stock Options & RSU Decision Tool for Executives, for Forecast Capital Management LLC.

The calculator estimates net after-tax value, tax on the next vesting date, concentration, and a one-year growth sketch for RSUs, NSOs, and ISOs. It is educational only. It is not investment, tax, or legal advice.

## Streamlit app

`app.py` is the original Streamlit app. Run it with:

```bash
pip install -r requirements.txt
streamlit run app.py
```

The math lives in `calc.py`. The page below uses the same formulas.

Lead email from the Streamlit app still reads `sender_email` and `sender_password` from Streamlit secrets at runtime. Those values are not in this repository. Keep them in Streamlit Cloud secrets or a local `secrets.toml` that is not committed (`.gitignore` already excludes it).

## Squarespace

The visitor-facing tool is a single file, `web/exec-comp-optimizer.html`. It does not need a server or a build step. CSS and JavaScript are inline. Open the file in a browser to use it on its own.

### Paste into a Code Block

1. In Squarespace, edit the page and add a **Code** block.
2. Open `web/exec-comp-optimizer.html`.
3. Copy from the line `BEGIN SQUARESPACE` through `END SQUARESPACE`, including those comments, and paste that into the Code block. That fragment carries its own stylesheet and script, scoped to `#fcm-exec-comp`, so it does not restyle the rest of the theme.
4. Pasting the whole file also works. The rules in `<head>` apply only when the page itself has `class="fcm-standalone"` on `<html>`, which a Code Block does not keep.
5. Save, then check the page on a phone and on a desktop browser.

### Or embed with an iframe

Host the file (any static host, or Squarespace's file hosting) and paste:

```html
<iframe src="URL_OF_THE_HTML_FILE" title="Exec Comp Optimizer" style="width:100%;min-height:1600px;border:0;"></iframe>
```

### Email opt-in

The calculator runs with no signup. Under the results, “Email me my results” is a normal HTML form. Set its destination at the top of the file:

```javascript
var FCM_RESULTS_FORM_ACTION = "https://example.com/replace-with-kit-or-email-form-action";
```

Replace that placeholder with the Kit form action, or another endpoint the firm controls, before publishing. The form posts `first_name`, `email_address`, `ticker`, `compensation_type`, and `results_summary`. It does not send mail by itself.

## Parity test

```bash
python3 tests/test_parity.py
```

The test runs the original formulas, `calc.py`, and the JavaScript in the HTML file on the same cases (including vesting-date boundaries, concentration cutoffs, out-of-the-money options, and ISO versus NSO). Display strings have to match Python’s rounding. The latest write-up is `tests/PARITY_RESULTS.md`.
