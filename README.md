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

### Email me my results

The illustration still runs with no signup. The optional form under the figures posts to the firm’s email system:

`POST https://go.forecastcapitalmanagement.com/api/subscribe`

The JSON body is `{ "email", "name", "source": "exec-comp-optimizer" }`, the same shape the landing page sends. Name is optional. `subscribeUrl` and `subscribeSource` live in `FCM_ECO_CONFIG` at the top of `web/exec-comp-optimizer.html`.

That endpoint does not send CORS headers, and this page is served from `www.forecastcapitalmanagement.com`. A `fetch` with `Content-Type: application/json` would preflight and be blocked. The page instead uses `fetch` with `mode: "no-cors"` and `Content-Type: text/plain;charset=UTF-8`, and the body is the JSON string. That is a simple request, so the browser does not preflight. The response is opaque, so the page does not read it. After the request is handed off it shows “Thanks — check your inbox.”

The form checks the email address, ignores a filled honeypot (`fcm_eco_hp`), and will not send a second request while one is in flight or after one has been accepted. A network failure leaves the button available to try again. The contact line under the form is the only follow-up link.

The Streamlit app sent a lead notice through Gmail SMTP using `st.secrets`. That path is not in the HTML file. `secrets.toml` has been removed from the repository and listed in `.gitignore`. The password should be rotated; older commits may still contain it. This change does not rewrite history.

### Live prices

The Streamlit app fetched a quote with Yahoo Finance. A browser page on Squarespace cannot do that without a server or a third-party key. The price is entered by hand. It is prefilled at $150 — the same fallback the Streamlit app used when a quote failed — so a result is visible immediately.

### Run the parity test

```bash
python3 tests/test_parity.py
```

That command also runs the opt-in checks. `python3 tests/test_optin.py` runs those on their own. Both use a mock `fetch`. They do not call `go.forecastcapitalmanagement.com`.

Requires Python 3 and Node.js. No extra packages. The parity portion runs the formulas from `app.py` (via `tests/reference_model.py`) and the JavaScript embedded in the HTML on the same inputs, including edge cases, and compares the numbers within rounding. It also checks that displayed dollar amounts use the same half-even rounding as Python.
