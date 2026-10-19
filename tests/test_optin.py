"""Opt-in subscribe tests. Fetch is always a mock. Nothing calls the production endpoint."""

from __future__ import annotations

import json
import re
import subprocess
import tempfile
from pathlib import Path

PRODUCTION_HOST = "go.forecastcapitalmanagement.com"
MOCK_URL = "https://optin.test/subscribe"


def extract_library(html_path: Path) -> str:
    html = html_path.read_text(encoding="utf-8")
    match = re.search(
        r"/\* FCM_ECO_LIB_START \*/(.*)/\* FCM_ECO_LIB_END \*/",
        html,
        re.S,
    )
    if not match:
        raise RuntimeError("Could not find FCM_ECO_LIB markers in the HTML file.")
    return match.group(1)


def run_scenario(library: str, steps, fetch_behavior="ok"):
    harness = r"""
globalThis.fetch = function () {
  throw new Error("global fetch must not be called");
};
const input = JSON.parse(require("fs").readFileSync(0, "utf8"));
const calls = [];
let releaseHang = null;
function mockFetch(url, init) {
  const record = {
    url: String(url),
    method: init && init.method,
    mode: init && init.mode,
    contentType: init && init.headers && init.headers["Content-Type"],
    body: init && init.body
  };
  calls.push(record);
  if (input.fetchBehavior === "reject") return Promise.reject(new Error("offline"));
  if (input.fetchBehavior === "hang") {
    return new Promise(function (resolve) { releaseHang = resolve; });
  }
  return Promise.resolve({ type: "opaque" });
}
const optIn = globalThis.fcmEcoCreateOptIn({
  url: input.url,
  source: input.source,
  fetchImpl: mockFetch
});
const results = [];
function finish() {
  process.stdout.write(JSON.stringify({ results: results, calls: calls }));
}
if (input.fetchBehavior === "hang") {
  const step = input.steps[0];
  const first = optIn.submit(step);
  const second = optIn.submit(step);
  second.then(function (duplicate) {
    results.push(duplicate);
    releaseHang({ type: "opaque" });
    return first;
  }).then(function (sent) {
    results.push(sent);
    finish();
  }).catch(function (err) {
    console.error(err && err.stack ? err.stack : err);
    process.exit(1);
  });
} else {
  let chain = Promise.resolve();
  input.steps.forEach(function (step) {
    chain = chain.then(function () {
      return optIn.submit(step).then(function (result) { results.push(result); });
    });
  });
  chain.then(finish).catch(function (err) {
    console.error(err && err.stack ? err.stack : err);
    process.exit(1);
  });
}
"""
    payload = {
        "url": MOCK_URL,
        "source": "exec-comp-optimizer",
        "steps": steps,
        "fetchBehavior": fetch_behavior,
    }
    with tempfile.TemporaryDirectory() as tmp:
        script = Path(tmp) / "optin.js"
        script.write_text(library + "\n" + harness, encoding="utf-8")
        proc = subprocess.run(
            ["node", str(script)],
            input=json.dumps(payload),
            text=True,
            capture_output=True,
            check=False,
        )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr or proc.stdout or "node failed")
    if PRODUCTION_HOST in proc.stdout or PRODUCTION_HOST in proc.stderr:
        raise RuntimeError("opt-in test output mentioned the production host")
    return json.loads(proc.stdout)


def collect_failures(html_path: Path):
    failures = []
    library = extract_library(html_path)
    if PRODUCTION_HOST in library:
        failures.append("subscribe URL must stay in the page config, outside the calculation library")

    def check(name, steps, behavior, expect_results, expect_calls):
        try:
            out = run_scenario(library, steps, behavior)
        except Exception as exc:
            failures.append(f"{name}: {exc}")
            return
        if out["results"] != expect_results:
            failures.append(f"{name} results {out['results']!r} != {expect_results!r}")
        if out["calls"] != expect_calls:
            failures.append(f"{name} calls {out['calls']!r} != {expect_calls!r}")
        for call in out["calls"]:
            if PRODUCTION_HOST in call["url"]:
                failures.append(f"{name} called the production host")

    body = json.dumps(
        {"email": "ada@example.com", "name": "Ada", "source": "exec-comp-optimizer"},
        separators=(",", ":"),
    )
    sent_call = {
        "url": MOCK_URL,
        "method": "POST",
        "mode": "no-cors",
        "contentType": "text/plain;charset=UTF-8",
        "body": body,
    }
    check(
        "valid with name",
        [{"email": "  ada@example.com  ", "name": "  Ada  ", "honeypot": ""}],
        "ok",
        [{"ok": True, "reason": "sent", "sent": True}],
        [sent_call],
    )
    empty_name = json.dumps(
        {"email": "ada@example.com", "name": "", "source": "exec-comp-optimizer"},
        separators=(",", ":"),
    )
    check(
        "optional name",
        [{"email": "ada@example.com", "name": "   ", "honeypot": ""}],
        "ok",
        [{"ok": True, "reason": "sent", "sent": True}],
        [{**sent_call, "body": empty_name}],
    )
    check(
        "invalid email",
        [{"email": "not-an-email", "name": "Ada", "honeypot": ""}],
        "ok",
        [{"ok": False, "reason": "email", "sent": False}],
        [],
    )
    check(
        "honeypot",
        [{"email": "ada@example.com", "name": "Ada", "honeypot": "https://spam.example"}],
        "ok",
        [{"ok": False, "reason": "honeypot", "sent": False}],
        [],
    )
    check(
        "second submit after success",
        [
            {"email": "ada@example.com", "name": "Ada", "honeypot": ""},
            {"email": "ada@example.com", "name": "Ada", "honeypot": ""},
        ],
        "ok",
        [
            {"ok": True, "reason": "sent", "sent": True},
            {"ok": False, "reason": "duplicate", "sent": False},
        ],
        [sent_call],
    )
    check(
        "double submit while in flight",
        [{"email": "ada@example.com", "name": "Ada", "honeypot": ""}],
        "hang",
        [
            {"ok": False, "reason": "duplicate", "sent": False},
            {"ok": True, "reason": "sent", "sent": True},
        ],
        [sent_call],
    )
    check(
        "network failure can retry",
        [
            {"email": "ada@example.com", "name": "Ada", "honeypot": ""},
            {"email": "ada@example.com", "name": "Ada", "honeypot": ""},
        ],
        "reject",
        [
            {"ok": False, "reason": "network", "sent": False},
            {"ok": False, "reason": "network", "sent": False},
        ],
        [sent_call, sent_call],
    )
    return failures


def main():
    html_path = Path(__file__).resolve().parents[1] / "web" / "exec-comp-optimizer.html"
    failures = collect_failures(html_path)
    print("Exec comp opt-in")
    print(f"  scenarios: 7")
    print("  fetch: mock only")
    if failures:
        print(f"  FAILED: {len(failures)}")
        for item in failures:
            print(f"  - {item}")
        return 1
    print("  result: pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
