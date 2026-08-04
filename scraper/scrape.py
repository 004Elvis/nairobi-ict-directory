#!/usr/bin/env python3
"""
Nairobi ICT Attachment & Internship Directory — link & freshness checker


What this does
---------------
For every company in data/companies.json, this script:

  1. Checks that the company's careers-page link still loads (catches the
     dead links and site redesigns that make directories like this go stale).
  2. Scans the page text for attachment/internship-related keywords, as a
     rough signal of whether the page still talks about student placements.
  3. Records the result (link_status, keyword_hit, last_checked) back into
     data/companies.json, which assets/app.js reads to show the little
     freshness dot on each card.
  4. Writes a plain-language run report to scraper/last_run_report.md so
     you can see what changed without reading logs.

On link_status values
-----------------------
There are four: "ok", "broken", "unverified", and "unchecked" (the seed
state before this script has ever run once). "broken" means the server
itself responded with a real HTTP error (404, 410, etc.), a fairly
confident signal. "unverified" means the request failed at the network
level (timeout, connection refused, SSL/certificate error) even after a
retry this is NOT confident evidence the link is dead. It very often
means a corporate firewall/WAF rejected an automated request that a real
browser would sail through, or a one-off network hiccup. The two are kept
separate on purpose so the site never tells a student "this link may be
down" about a company that's actually fine.

On the User-Agent
-------------------
This identifies as a normal desktop browser rather than as a bot. Several
Kenyan corporate sites run bot-detection that blocks anything self-
identifying as automated, which produces false "broken" results for
perfectly live pages that's worse than not checking at all. robots.txt
is still fully respected (see RobotsCache below), which is the standard
and correct channel for a site to opt out of being crawled; the User-
Agent string itself is just about not tripping naive bot filters for a
benign, rate-limited, single-page-per-company check.

What this does NOT do
-----------------------
It does not and cannot reliably tell you the actual deadline, stipend
amount, or whether a diploma student will be accepted this quarter. Career
pages are too inconsistent for that to be automated honestly. Those fields
still need a human to read the page and update data/companies.json by hand.


Usage
------
    python scraper/scrape.py                  # check every company
    python scraper/scrape.py --only kra        # check one company (id substring)
    python scraper/scrape.py --limit 5         # check only the first 5 (for testing)
    python scraper/scrape.py --dry-run         # check, but don't write changes
    python scraper/scrape.py --delay 2.5       # seconds between requests (default 1.5)
    python scraper/scrape.py --verbose         # print per-company detail as it runs
    python scraper/scrape.py --allow-insecure  # see note below, off by default

--allow-insecure: if (and only if) a request fails specifically with a
certificate error, retry once without verifying the certificate. A couple
of Kenyan .go.ke sites have real certificate-chain issues that browsers
paper over but Python's stricter verification catches.

Runs anywhere Python 3.8+ and the two packages in requirements.txt are
available. See README.md for how to schedule this automatically with
GitHub Actions so Netlify redeploys with fresh data on its own.
"""

import argparse
import json
import logging
import sys
import time
import urllib.robotparser
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "companies.json"
REPORT_PATH = ROOT / "scraper" / "last_run_report.md"

# Looks like a normal browser on purpose — see "On the User-Agent" above.
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}
REQUEST_TIMEOUT = 15   # seconds
DEFAULT_DELAY = 1.5    # seconds between companies, kept polite on purpose
RETRY_PAUSE = 2.0      # seconds before a single retry on a network-level failure

# Rough, intentionally broad signal — not a precise classifier. A page can
# legitimately not mention any of these and still run a program (e.g. behind
# a login), which is exactly why link_status and keyword_hit are recorded
# and shown separately rather than collapsed into one confident verdict.
KEYWORDS = [
    "attachment", "attach\u00e9", "internship", "intern program", "interns",
    "industrial attachment", "graduate trainee", "trainee program",
    "student attachment", "apprenticeship",
]

log = logging.getLogger("scraper")


def load_data():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data):
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class RobotsCache:
    """Fetches and caches robots.txt per domain so we only ask once per run."""

    def __init__(self, session):
        self.session = session
        self._cache = {}

    def can_fetch(self, url):
        domain = urlparse(url).netloc
        if domain not in self._cache:
            rp = urllib.robotparser.RobotFileParser()
            robots_url = f"{urlparse(url).scheme}://{domain}/robots.txt"
            try:
                resp = self.session.get(robots_url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
                if resp.status_code == 200:
                    rp.parse(resp.text.splitlines())
                else:
                    rp.allow_all = True
            except requests.RequestException:
                # If robots.txt itself is unreachable, don't block the check
                # over it, but don't cache a false "allowed" for a domain
                # that's actually just down; the real fetch will fail too.
                rp.allow_all = True
            self._cache[domain] = rp
        try:
            return self._cache[domain].can_fetch(HEADERS["User-Agent"], url)
        except Exception:
            return True


def extract_visible_text(html):
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript", "template"]):
        tag.decompose()
    return soup.get_text(separator=" ", strip=True).lower()


def find_keywords(text):
    hits = [kw for kw in KEYWORDS if kw in text]
    return (len(hits) > 0, hits)


def fetch(session, url, allow_insecure):
    """GETs url with one retry on network-level failure. Returns
    (response_or_None, error_description_or_None, used_insecure_fallback)."""

    last_err = None
    for attempt in (1, 2):
        try:
            resp = session.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT, allow_redirects=True)
            return resp, None, False
        except requests.exceptions.SSLError as exc:
            if allow_insecure:
                try:
                    resp = session.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT,
                                        allow_redirects=True, verify=False)
                    return resp, None, True
                except requests.RequestException as exc2:
                    last_err = f"{type(exc2).__name__}: {exc2}"
            else:
                last_err = f"{type(exc).__name__}: {exc}"
        except requests.RequestException as exc:
            last_err = f"{type(exc).__name__}: {exc}"

        if attempt == 1:
            time.sleep(RETRY_PAUSE)

    return None, last_err, False


def check_company(company, session, robots, dry_run, allow_insecure):
    """Checks one company's careers_url. Mutates `company` in place (unless
    dry_run) and returns a small result dict for the run report."""

    url = company["careers_url"]
    name = company["company"]
    result = {"company": name, "id": company["id"], "url": url}

    if not robots.can_fetch(url):
        result.update(outcome="skipped", detail="disallowed by robots.txt")
        log.info("SKIP       %-40s robots.txt disallows this path", name)
        return result

    resp, err, used_insecure = fetch(session, url, allow_insecure)

    if resp is None:
        result.update(outcome="unverified", detail=err)
        log.info("UNVERIFIED %-40s %s", name, err)
        if not dry_run:
            company["link_status"] = "unverified"
            company["keyword_hit"] = None
            company["last_checked"] = now_iso()
        return result

    if resp.status_code >= 400:
        result.update(outcome="broken", detail=f"HTTP {resp.status_code}")
        log.info("BROKEN     %-40s HTTP %s", name, resp.status_code)
        if not dry_run:
            company["link_status"] = "broken"
            company["keyword_hit"] = None
            company["last_checked"] = now_iso()
        return result

    text = extract_visible_text(resp.text)
    hit, matched = find_keywords(text)
    detail = ("mentions: " + ", ".join(matched)) if hit else "no keyword match"
    if used_insecure:
        detail += " (certificate not verified)"
    result.update(outcome="ok", detail=detail)
    log.info("OK         %-40s HTTP %s  %s%s", name, resp.status_code,
              "\u2713 keyword" if hit else "\u2013 no keyword",
              "  [insecure]" if used_insecure else "")

    if not dry_run:
        company["link_status"] = "ok"
        company["keyword_hit"] = hit
        company["last_checked"] = now_iso()

    return result


def write_report(results, dry_run):
    ok = [r for r in results if r["outcome"] == "ok"]
    broken = [r for r in results if r["outcome"] == "broken"]
    unverified = [r for r in results if r["outcome"] == "unverified"]
    skipped = [r for r in results if r["outcome"] == "skipped"]
    no_kw = [r for r in ok if "no keyword" in r["detail"]]

    lines = []
    lines.append("# Directory check \u2014 run report")
    lines.append("")
    lines.append(f"Run at: {now_iso()}" + ("  (dry run \u2014 no data written)" if dry_run else ""))
    lines.append("")
    lines.append(f"- Checked: {len(results)}")
    lines.append(f"- Link OK: {len(ok)}")
    lines.append(f"- Confirmed broken (server returned an error): {len(broken)}")
    lines.append(f"- Unverified (network/SSL issue, not confident either way): {len(unverified)}")
    lines.append(f"- Skipped (robots.txt): {len(skipped)}")
    lines.append(f"- OK but no attachment/internship keyword found: {len(no_kw)}")
    lines.append("")

    if broken:
        lines.append("## Confirmed broken \u2014 the server itself returned an error")
        lines.append("")
        lines.append("These got a real HTTP error response, which is a fairly confident signal.")
        lines.append("")
        for r in broken:
            lines.append(f"- **{r['company']}** \u2014 {r['detail']} \u2014 {r['url']}")
        lines.append("")

    if unverified:
        lines.append("## Unverified \u2014 worth a manual click before trusting this")
        lines.append("")
        lines.append("The request failed at the network level (timeout, connection refused, or an")
        lines.append("SSL/certificate error), even after a retry. This is often a corporate firewall")
        lines.append("or bot-protection rejecting an automated request that a real browser would get")
        lines.append("through fine \u2014 it is NOT strong evidence the link is actually dead. Open a few")
        lines.append("of these yourself before assuming anything is wrong.")
        lines.append("")
        for r in unverified:
            lines.append(f"- **{r['company']}** \u2014 {r['detail']} \u2014 {r['url']}")
        lines.append("")

    if no_kw:
        lines.append("## Loaded fine, but no internship/attachment keyword found")
        lines.append("")
        lines.append("Not necessarily a problem \u2014 some programs sit behind a login or a")
        lines.append("separate portal \u2014 but these are worth a skim next time you're updating listings.")
        lines.append("")
        for r in no_kw:
            lines.append(f"- **{r['company']}** \u2014 {r['url']}")
        lines.append("")

    if skipped:
        lines.append("## Skipped")
        lines.append("")
        for r in skipped:
            lines.append(f"- **{r['company']}** \u2014 {r['detail']}")
        lines.append("")

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    log.info("Report written to %s", REPORT_PATH.relative_to(ROOT))


def main(argv=None):
    parser = argparse.ArgumentParser(description="Check directory links and refresh freshness data.")
    parser.add_argument("--only", help="only check companies whose id contains this text")
    parser.add_argument("--limit", type=int, help="only check the first N companies (useful for a quick test)")
    parser.add_argument("--delay", type=float, default=DEFAULT_DELAY, help="seconds to wait between requests")
    parser.add_argument("--dry-run", action="store_true", help="check everything but don't write changes")
    parser.add_argument("--verbose", action="store_true", help="print per-company results as they happen")
    parser.add_argument("--allow-insecure", action="store_true",
                         help="on a certificate error, retry once without verifying it (see module docstring)")
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO if args.verbose else logging.WARNING, format="%(message)s")

    if args.allow_insecure:
        print("--allow-insecure is on: certificate errors will retry unverified. "
              "Only page text is read, but treat this as a deliberate, occasional choice, not a default.\n")
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    data = load_data()
    companies = data["companies"]
    if args.only:
        companies = [c for c in companies if args.only.lower() in c["id"]]
        if not companies:
            print(f"No company id contains '{args.only}'.")
            return 1
    if args.limit:
        companies = companies[: args.limit]

    print(f"Checking {len(companies)} of {len(data['companies'])} companies "
          f"({args.delay}s delay between requests)\u2026")

    session = requests.Session()
    robots = RobotsCache(session)
    results = []
    for i, company in enumerate(companies):
        results.append(check_company(company, session, robots, args.dry_run, args.allow_insecure))
        if i < len(companies) - 1:
            time.sleep(args.delay)

    if not args.dry_run:
        data["meta"]["last_scraped"] = now_iso()
        save_data(data)
        print(f"\nUpdated {DATA_PATH.relative_to(ROOT)}")
    else:
        print("\nDry run \u2014 data/companies.json was not modified.")

    write_report(results, args.dry_run)

    ok = sum(1 for r in results if r["outcome"] == "ok")
    broken = sum(1 for r in results if r["outcome"] == "broken")
    unverified = sum(1 for r in results if r["outcome"] == "unverified")
    skipped = len(results) - ok - broken - unverified
    print(f"Done. {ok} ok, {broken} confirmed broken, {unverified} unverified, {skipped} skipped.")
    print(f"See {REPORT_PATH.relative_to(ROOT)} for the full breakdown.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
