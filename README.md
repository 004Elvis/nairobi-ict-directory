# Nairobi ICT Attachment & Internship Directory

A directory of 53 companies across Nairobi that take diploma and degree
students for ICT industrial attachment or internships, searchable by
name, filterable by area, category, diploma eligibility and stipend, and
checked automatically so the links don't go stale.

Live: https://nairobi-ict-directory.netlify.app 

Compiled for diploma and degree ICT students in Nairobi. Company data was
last manually reviewed in May 2026.

## What's here

- A searchable, filterable directory of companies, rendered from a single JSON file
- An application guide: what to prepare, who accepts walk-ins, where else to look
- A Python script that periodically checks every company link and flags dead ones
- A "freshness" indicator on every listing showing when it was last auto-checked
- No build step, no framework, no dependencies to install for the site itself

## Project structure

```
index.html                       main page
assets/
  style.css                      all styling
  app.js                         search, filter, sort, rendering
  favicon.svg
data/
  companies.json                 every listing 
scraper/
  scrape.py                      the link/freshness checker
  requirements.txt
  last_run_report.md             written each time the checker runs
.github/workflows/
  update-data.yml                optional scheduled automation
netlify.toml                     deploy config, cache headers
```

## Running it locally

Inside the project folder, run the command below:

```
python -m http.server 8000
```

Then visit `http://localhost:8000`. Any static server works fine here 
VS Code's Live Server extension, `npx serve`, among others.


## The link checker

`scraper/scrape.py` opens each company's careers page, confirms it still
loads, and scans the text for attachment/internship-related keywords. It
writes the result back into `data/companies.json` and produces a plain
summary in `scraper/last_run_report.md`.

It deliberately does **not** try to extract the deadline, stipend amount,
or diploma policy automatically career pages are too inconsistent in
structure for that to be done reliably.

Install the two dependencies and run it from the project root:

```
pip install -r scraper/requirements.txt
python3 scraper/scrape.py
```

Useful flags:

```
python scraper/scrape.py --verbose        # print results as it runs
python scraper/scrape.py --dry-run        # check everything, write nothing
python scraper/scrape.py --only kra       # check one company (id substring)
python scraper/scrape.py --limit 5        # check only the first 5
python scraper/scrape.py --delay 2.5      # seconds between requests (default 1.5)
```

It also checks each site's `robots.txt` before fetching and skips pages
that disallow it, rather than ignoring the request.

**Every result lands in one of three buckets, on purpose:** `ok` (loaded
fine), `broken` (the company's own server returned a real HTTP error), or `unverified` (the request failed at the network
level timeout, connection refused, or a certificate error even after
one retry). `unverified` is deliberately *not* shown as "may be down" on
the site.

## Keeping it automatic

`.github/workflows/update-data.yml` runs the checker on a schedule (every
Monday by default) and commits any changes. If your GitHub repo is
connected to Netlify for continuous deployment, that commit triggers a new
deploy automatically the site updates itself with no further action
from you. You can also trigger it manually any time from the Actions tab
in GitHub ("Run workflow"), without waiting for the schedule.

This is entirely optional running `scraper/scrape.py` locally whenever
you feel like it and pushing the result works just as well.


## A note on the data

Deadlines and stipend details change often. The automated checker helps
catch dead links and gives a rough freshness signal, but it isn't a
substitute for confirming directly on each company's own careers page
before you apply.

## Credits

Directory maintained by Elvis Midega.
