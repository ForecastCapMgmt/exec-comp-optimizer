# exec-comp-optimizer

Stock Options & RSU Decision Tool for Executives, from Forecast Capital Management.

The Streamlit app in `app.py` is unchanged and can still be run with `streamlit run app.py`. The visitor-facing page is a single file, `web/exec-comp-optimizer.html`, so a blog call-to-action does not have to wait for a free Streamlit host to wake up.

## Pasting the tool into Squarespace

`web/exec-comp-optimizer.html` has no build step and no server. CSS and JavaScript are inline. The charts are HTML and CSS, so the page does not load a charting library. Google Fonts supplies Cormorant Garamond and Lora; Georgia is the fallback.

### Code block

1. In Squarespace, edit the page and add a **Code** block (not a Markdown block).
2. Open `web/exec-comp-optimizer.html` and copy the entire file.
3. Paste it into the Code block and save.
4. Styles and ids live under `#fcm-eco` and classes start with `fcm-eco-`, so the block should not restyle the rest of the theme.
5. Check the page on a phone as well as a desktop browser.

If a full HTML document is awkward in the block, paste from the comment `FCM-ECO-EMBED-START` through `FCM-ECO-EMBED-END`. That span includes the config, the stylesheet, the markup, and the script. The page viewport still comes from Squarespace.

### iframe

Host the file at a URL you control and embed it:

```html
<iframe
  src="https://YOUR-HOST/exec-comp-optimizer.html"
  title="Executive compensation illustration"
  style="width:100%;min-height:3200px;border:0;"
></iframe>
```

### Connect the optional email form

The illustration runs with no signup. Near the bottom, “Email me my results” is a normal HTML form. Nothing is emailed until the placeholder address is replaced.

1. Open `web/exec-comp-optimizer.html`.
2. Find `FCM_ECO_CONFIG` at the top of the file.
3. Set `optInFormAction` to the Kit form action or other intake URL. The script assigns that URL to the form on load.
4. The POST body includes `first_name`, `email_address`, a plain-text `results_summary`, and the individual figures. The field names are listed in the comment above the form. `fcm_eco_hp` is a honeypot; ignore the submission when it is filled in.

Until that URL is changed, submitting the form stays on the page and says that email is not connected. Visitors can print or copy the results instead.

The Streamlit app sent a lead notice through Gmail SMTP using `st.secrets`. That path is not in the HTML file. `secrets.toml` has been removed from the repository and listed in `.gitignore`. The password should be rotated; older commits may still contain it. This change does not rewrite history.

### Live prices

The Streamlit app fetched a quote with Yahoo Finance. A browser page on Squarespace cannot do that without a server or a third-party key. The price is entered by hand. It is prefilled at $150 — the same fallback the Streamlit app used when a quote failed — so a result is visible immediately.

### Run the parity test

```bash
python3 tests/test_parity.py
```

Requires Python 3 and Node.js. No extra packages. The test runs the formulas from `app.py` (via `tests/reference_model.py`) and the JavaScript embedded in the HTML on the same inputs, including edge cases, and compares the numbers within rounding. It also checks that displayed dollar amounts use the same half-even rounding as Python.
