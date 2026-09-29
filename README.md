# TMT Bot

An automated market-intelligence reporting system for finance and investment-
banking preparation. The Generator collects recent market news, selects and
enriches relevant sources, produces structured LLM analysis, renders daily PDF
briefs and short-form summaries, and publishes the resulting artefacts through
a separate Flask application.

The production path covers five sectors across three regions. Scheduled GitHub
Actions runs keep report generation independent from the report-serving site:
the workflows generate and version the artefacts, while the Flask application
only discovers and serves files that already exist.

## Contents

- [Architecture](#architecture)
  - [Daily brief pipeline](#daily-brief-pipeline)
  - [Weekly recap pipeline](#weekly-recap-pipeline)
  - [Generator and web-app boundary](#generator-and-web-app-boundary)
- [Coverage and report structure](#coverage-and-report-structure)
- [Generated artefacts](#generated-artefacts)
- [Automation](#automation)
- [Tech stack](#tech-stack)
- [Conventions](#conventions)
- [Configuration](#configuration)
- [Running the Generator locally](#running-the-generator-locally)
- [Running the web application locally](#running-the-web-application-locally)
- [Project structure](#project-structure)
- [Current implementation notes](#current-implementation-notes)

## Architecture

```text
.github/workflows/
    Auto_run_briefs.yml             Daily schedule / manual dispatch
    weekly_recaps_auto_run.yml      Sunday schedule / manual dispatch
                    │
                    │ installs requirements_generator.txt and injects secrets
                    ▼
Generator/main.py   Orchestrates the complete daily matrix:
                    3 regions × 5 sectors. For each pair it selects the
                    category set and prompt matrix, then delegates the report
                    work to IBDMarketAnalyst and the PDF renderer.
                    │
                    ├── Generator/config.py
                    │       Sector categories, regional search anchors,
                    │       deal vocabulary and generator configuration.
                    │
                    ├── Generator/prompts.py
                    │       Seven-section prompt matrices for TMT, Energy,
                    │       Healthcare, Industry and Consumer.
                    │
                    ├── Generator/report_generator.py
                    │       News collection, LLM article selection, article
                    │       extraction, company enrichment, report generation,
                    │       link validation, glossary extraction and TL;DRs.
                    │
                    ├── Generator/additional_info_collector.py
                    │       Company-name-to-symbol resolution, exchange/region
                    │       scoring, symbol caching and Yahoo Finance snapshots.
                    │
                    ├── Generator/transcript_crawler.py
                    │       Latest macroeconomic podcast transcript used by the
                    │       final daily-report section.
                    │
                    ├── Generator/pdf_report.py
                    │       Parser and fpdf renderer for the report's constrained
                    │       Markdown-like format, including tables and links.
                    │
                    ├── Generator/email_briefs.py
                    │       Optional SMTP delivery of selected generated PDFs.
                    │
                    └── Generator/weekly_recap.py
                            Aggregates the previous week's daily raw reports and
                            contexts into one cross-sector recap per region.
                    │
                    ▼
api/static/assets/ Versioned output store: source context, raw model output,
                   report PDFs, TL;DR PDFs and weekly recap PDFs.
                    │
                    │ read-only at request time
                    ▼
api/index.py       Flask application. Scans the committed artefacts, exposes
                   report metadata, renders raw briefs as HTML, serves PDFs,
                   and provides report-grounded chat. It does not run the
                   Generator when a user requests a report.
```

### Daily brief pipeline

`Generator/main.py` calls `main(4)` when executed directly. That is the full
batch mode: it iterates through `US`, `Europe` and `APAC`, and within each
region generates TMT, Energy, Healthcare, Industry and Consumer reports.

For each sector-region pair, `generate_daily_brief(...)` performs the following
steps:

1. **Build sector- and region-aware news queries.**
   `IBDMarketAnalyst.collect_news` combines each sector's five configured
   categories with M&A/deal vocabulary and optional regional anchors. It asks
   NewsAPI for English-language articles from the configured seven-day lookback
   window, tries title search first, falls back to full-text search, and moves
   through backup NewsAPI keys when a key is rate-limited.
2. **Select the most relevant sources.**
   `choose_best_news_with_gpt` sends each category's candidate titles,
   descriptions and original URLs to `gpt-4o-mini`. It requests up to four
   articles per category and extracts both the selected URLs and mentioned
   company names. The prompt requires URLs to be copied rather than invented.
3. **Fetch full source text and company context.**
   `find_news_populate_context` downloads and parses each selected article with
   `newspaper3k`, removes common boilerplate, and appends its title, cleaned
   body and source URL. Mentioned companies are resolved against Yahoo and
   Finnhub candidates using name similarity, exchange quality, regional fit
   and junk-instrument penalties. `yfinance` then supplies a compact snapshot
   such as symbol, market capitalisation, P/E, enterprise value, EBITDA,
   revenue and net income. Symbol decisions are cached in
   `Generator/symbol_cache.json`.
4. **Persist the evidence supplied to the model.**
   The assembled source material is written to
   `api/static/assets/context/<region>_<sector>_context_<date>.txt`, with clear
   separators between the five category blocks. These files make the inputs to
   a historical report inspectable after the run.
5. **Generate the structured report.**
   `analyze_news` injects the five category contexts into the sector-specific
   matrix in `Generator/prompts.py`. The first five sections are generated
   separately with a small sliding conversation window; Recommended Readings
   is generated afterwards, and the final macroeconomic section is grounded in
   the latest transcript returned by `transcript_crawler.py`. The assembled
   pre-validation report is saved before rendering as
   `api/static/assets/raw/<region>_<sector>_Brief_<date>_raw.txt`.
6. **Validate report links.**
   `replace_broken_links` checks Markdown links with an HTTP `HEAD` request and
   a `GET` fallback. When a link fails, the generator asks the OpenAI search
   model for a replacement and verifies the replacement before inserting it.
7. **Extract technical terms.**
   `detect_technical_terms` asks `gpt-3.5-turbo` for a newcomer-oriented
   finance/M&A glossary and reads the shared `api/term_definitions.json` store.
   See [Current implementation notes](#current-implementation-notes) for the
   current persistence limitation in this step.
8. **Render the long-form PDF.**
   `format_brief` parses the Generator's constrained Markdown-like output and
   renders headings, subsections, bullets, tables and clickable links with
   `fpdf`. The result is written to
   `api/static/assets/briefs/<region>_<sector>_Brief_<date>.pdf`.
9. **Generate and render three summary lengths.**
   `generate_TLDR` turns the report into 30-second, one-minute and two-minute
   versions. The same renderer writes them as one PDF under
   `api/static/assets/TLDR/`.
10. **Continue through the configured matrix, then deliver.**
    After the batch finishes, `send_emails` attaches its configured subset of
    daily briefs and sends them through SMTP. GitHub Actions subsequently
    stages the generated artefacts and commits them back to the repository.

The pipeline is deliberately artefact-first: the context file, raw report and
rendered PDFs are all retained rather than collapsing generation into one
opaque model call.

### Weekly recap pipeline

`Generator/weekly_recap.py` is a separate aggregation path rather than a mode
inside the daily Generator:

1. Calculate the previous seven-day window.
2. For each of `US`, `Europe` and `APAC`, scan all five sectors and all days in
   the window.
3. Load section one from each available raw daily report and the corresponding
   first context block; missing days are skipped.
4. Combine the material into one region-specific system prompt covering both
   primary-market activity and secondary-market/macroeconomic themes.
5. Generate one cross-sector recap with `gpt-4o-mini`.
6. Render the result as
   `api/static/assets/recaps/<region>_Recap_<date>.pdf`.

The weekly workflow runs independently every Sunday, so recap generation can
use whatever daily artefacts are present without changing the serving layer.

### Generator and web-app boundary

The Generator and the Flask application share an artefact contract, not a
runtime call:

```text
GitHub Actions or local process
        │
        └── runs Generator/*.py
                │
                └── writes api/static/assets/* + term_definitions.json
                                │
                                └── committed as versioned outputs
                                                │
                                                ▼
Vercel / Flask deployment reads the repository snapshot
```

`api/index.py` dynamically scans the brief and recap folders when building its
report listings. It can also load a raw report and its source context for HTML
rendering and report-grounded Q&A. A browser request never waits for daily
generation, and a failed Generator run does not take the existing report site
offline.

The web application additionally stores user and subscription data in
PostgreSQL and report-chat conversations/messages in MongoDB. That application
layer is intentionally secondary in this README; the scheduled Generator and
its artefact contract are the core of the repository.

## Coverage and report structure

Full batch mode covers up to 15 combinations per run:

| Dimension | Values |
|---|---|
| Regions | US, Europe, APAC |
| Sectors | TMT, Energy, Healthcare, Industry, Consumer |
| Category groups per sector | 5 |
| Daily outputs per successful combination | Raw report, source context, long-form PDF, TL;DR PDF |

Each sector has its own prompt matrix, but the high-level daily report shape is
consistent:

1. Recent sector M&A activity
2. Market dynamics and sentiment
3. Banking pipeline
4. Stakeholder impact and forward-looking analysis
5. Sector trends
6. Recommended readings
7. Macroeconomic update

The report format is a contract between `Generator/prompts.py`,
`Generator/pdf_report.py` and the HTML parser in `api/index.py`. Prompts use
`###` for numbered sections, `####` or `**...**` for subsections, `- **...**`
for labelled bullets, pipe-delimited Markdown tables, and a fixed Markdown link
shape. Changing the prompt syntax without updating both parsers can produce a
valid model response that renders incorrectly.

## Generated artefacts

| Path | Producer | Purpose |
|---|---|---|
| `api/static/assets/context/` | Daily Generator | Full extracted article text plus company/market-data enrichment; the inspectable evidence supplied to report generation |
| `api/static/assets/raw/` | Daily Generator | Unrendered structured model output captured before the broken-link replacement pass; consumed by the HTML report view, weekly recaps and report-grounded chat |
| `api/static/assets/briefs/` | Daily Generator | Long-form sector-region PDF briefs served by the Flask application |
| `api/static/assets/TLDR/` | Daily Generator | PDFs containing the 30-second, one-minute and two-minute summaries |
| `api/term_definitions.json` | Daily Generator | Shared finance-term glossary loaded by the report renderer |
| `api/static/assets/recaps/` | Weekly Generator | Cross-sector weekly recap PDFs for US, Europe and APAC |
| `api/static/assets/recaps_raw/` | Weekly workflow staging rule | Intended location for raw weekly recap text; see the path mismatch noted below |
| `Generator/symbol_cache.json` | Company enrichment | Cached company-name/region to listed-symbol resolutions |

Generated files are committed rather than treated as disposable CI artefacts.
That makes historical runs diffable and leaves the serving deployment with a
stable, versioned report snapshot.

## Automation

### Daily reports

`.github/workflows/Auto_run_briefs.yml` runs at `00:00 UTC` every day and also
supports manual dispatch. It:

1. Checks out full repository history.
2. Installs Python 3.12.2.
3. Restores a pip download cache keyed from the requirements files.
4. Installs `requirements_generator.txt`.
5. Supplies the configured API/email secrets and runs `Generator/main.py`.
6. Stages PDFs, TL;DRs, raw outputs, source contexts and the glossary JSON.
7. Creates a date-stamped commit only when files changed.
8. Pushes the commit to `main` with the workflow token.

### Weekly recaps

`.github/workflows/weekly_recaps_auto_run.yml` runs at `00:00 UTC` each Sunday
and supports manual dispatch. It uses the same Python/cache/dependency setup,
runs `Generator/weekly_recap.py`, stages recap outputs and pushes a separate
date-stamped commit.

The workflow files are the operational specification for scheduled execution.
The repository also contains manual diagnostic workflows for recap and Yahoo
Finance testing; they are not a unit-test suite.

## Tech stack

| Layer | Technology |
|---|---|
| Orchestration | Python 3.12, `Generator/main.py`, GitHub Actions cron/manual workflows |
| LLM analysis | OpenAI Chat Completions: `gpt-4o-mini` for selection, reports, recaps and TL;DRs; `gpt-4o-mini-search-preview` for failed-link recovery; `gpt-3.5-turbo` for glossary extraction |
| News discovery | NewsAPI with sector deal terms, regional anchors, title-first/full-text fallback and backup-key rotation |
| Article extraction | `newspaper3k`, `requests`, Beautiful Soup/lxml dependencies |
| Company enrichment | Yahoo and Finnhub symbol search, region/exchange scoring, `yfinance`, pandas and a JSON symbol cache |
| PDF generation | `fpdf` with a repository-specific parser for headings, bullets, tables and hyperlinks |
| Delivery | SMTP over SSL plus GitHub commits as the publication mechanism |
| Web application | Flask 3, Jinja templates, Flask-Login, Flask-SQLAlchemy, PostgreSQL and MongoDB |
| Hosting | Vercel Python serverless function rewriting all routes to `api/index.py` |

## Conventions

- **Sector matrices stay aligned.** In full batch mode, `sectors`, `categories`
  and `prompt_matrices` are parallel lists. Add or reorder a sector in all
  three places, and add its configuration and prompt matrix at the same time.
- **Region names are part of the file contract.** The Generator, Flask report
  scanner, weekly recap loader and chat prompt builder all derive paths from
  `US`, `Europe` and `APAC`. Treat filename changes as an API change.
- **Preserve source URLs.** Article-selection prompts require exact input URLs.
  Link replacement happens only after a URL fails an explicit network check.
- **Persist intermediate state.** Context and raw report text are first-class
  outputs, not temporary files. New pipeline stages should continue to leave
  useful evidence that can be inspected after a run.
- **Prompt syntax is renderer syntax.** Formatting tokens emitted by the model
  are parsed by both the PDF and HTML paths. Update prompt examples, parser
  regular expressions and renderers together.
- **Missing weekly inputs are tolerated.** The recap loader skips absent daily
  files so one failed day does not prevent the next weekly aggregation.
- **The Generator is synchronous and sequential.** Network calls, model calls
  and the 15 sector-region runs execute in process rather than through an async
  worker pool. This makes the control flow easy to inspect but full runs can be
  long and API-intensive.
- **Generated history is not development history.** Many commits are scheduled
  output snapshots. When reviewing implementation changes, distinguish those
  commits from edits to `Generator/`, `api/` and `.github/workflows/`.

## Configuration

The scheduled workflows and web application use these configuration names:

| Variable | Used for |
|---|---|
| `OPENAI_API` | OpenAI client authentication in the Generator and web application |
| `NEWS_API` | Intended NewsAPI credential supplied by GitHub Actions |
| `EMAIL_USER` | Intended SMTP username |
| `EMAIL_PASS` | Intended SMTP password/app password |
| `GITHUB_TOKEN` | Pushing generated artefact commits from GitHub Actions |
| `DATABASE_URL` | PostgreSQL connection for the Flask user/subscription layer |
| `MONGO_DB_NAME` | Optional MongoDB database-name override |

`Generator/config.py` also defines NewsAPI backup keys, market-data provider
keys, the lookback window, sector categories, deal terms and regional anchors.
`Generator/config_template.py` is only a minimal example; it does not currently
cover every value imported by the production Generator.

> **Security boundary.** The current codebase mixes environment variables with
> deployment-specific values in source files, including Generator, database and
> email configuration. Before running a fork or deploying publicly, rotate any
> historical credentials, move secrets and recipient lists to environment
> variables, replace the Flask secret key, and do not treat checked-in values as
> safe or reusable. The workflow's `NEWS_API`, `EMAIL_USER` and `EMAIL_PASS`
> variables are not consistently consumed by the current Python modules.

## Running the Generator locally

Create an isolated environment from the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements_generator.txt
```

Before running, configure the OpenAI, NewsAPI and market-data credentials used
by `Generator/config.py`. Also review `Generator/email_briefs.py`: full batch
mode calls `send_emails()` after generation, so a local report-only run should
disable that call or replace the SMTP configuration and recipients with your
own environment-backed settings.

Then run the full matrix:

```bash
export OPENAI_API="<your key>"
python Generator/main.py
```

The script is designed to run from the repository root. Successful outputs
appear under `api/static/assets/`; partial artefacts may remain if a later stage
or later sector fails. A full run makes many paid/network API calls, so test
with a deliberately reduced region/sector matrix in a fork before enabling the
complete batch.

To generate weekly recaps from daily artefacts already present locally:

```bash
export OPENAI_API="<your key>"
python Generator/weekly_recap.py
```

## Running the web application locally

The web app has a separate dependency set:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export OPENAI_API="<your key>"
export DATABASE_URL="<postgres connection URL>"
export MONGO_DB_NAME="tmtbot"
python api/index.py
```

The application expects its database and MongoDB configuration to be valid at
runtime. It reads existing reports from `api/static/assets/`; starting Flask
does not generate missing reports. See `api/README.md` for the application
pages and API routes, but treat its demo credentials and older security notes
as development documentation rather than production setup.

## Project structure

```text
.
├── .github/workflows/
│   ├── Auto_run_briefs.yml           # Daily generation + versioned outputs
│   ├── weekly_recaps_auto_run.yml    # Weekly cross-sector recaps
│   ├── run_recap_test.yml            # Manual recap diagnostic
│   └── run_yf_test.yml               # Manual market-data diagnostic
├── Generator/
│   ├── main.py                       # Daily 3-region × 5-sector orchestrator
│   ├── report_generator.py           # Core collection/analysis pipeline
│   ├── additional_info_collector.py  # Symbol resolution + financial data
│   ├── transcript_crawler.py         # Macroeconomic transcript source
│   ├── prompts.py                    # Sector report contracts
│   ├── pdf_report.py                 # PDF parser and renderer
│   ├── weekly_recap.py               # Seven-day regional aggregation
│   ├── email_briefs.py               # SMTP delivery
│   ├── config.py                     # Runtime categories/anchors/configuration
│   ├── config_template.py            # Minimal credential example
│   ├── symbol_cache.json             # Persistent symbol lookup cache
│   └── *_deal_report*.py             # Separate one-off deal-report utilities
├── api/
│   ├── index.py                      # Flask server and report/chat consumers
│   ├── term_definitions.json         # Shared glossary store
│   ├── static/assets/
│   │   ├── briefs/                   # Daily long-form PDFs
│   │   ├── TLDR/                     # Daily short-form PDFs
│   │   ├── raw/                      # Structured model output
│   │   ├── context/                  # Source/evidence snapshots
│   │   ├── recaps/                   # Weekly regional PDFs
│   │   └── recaps_raw/               # Intended raw recap store
│   └── templates/                    # Landing, dashboard, report and chat UI
├── requirements_generator.txt        # Generator-only dependencies
├── requirements.txt                  # Flask application dependencies
└── vercel.json                       # Routes the deployment to api/index.py
```

The deal-report scripts under `Generator/` and historical PDFs under the asset
folders are adjacent capabilities. They are not part of the scheduled daily
brief path described above.

## Current implementation notes

- `detect_technical_terms` parses a glossary from the model, but the current
  write path serialises the previously loaded dictionary without first merging
  the newly extracted terms. The stage returns the new terms to its caller, but
  `api/term_definitions.json` is not expanded until that merge is restored.
- `weekly_recap.py` writes raw recap text to the process working directory,
  while the weekly workflow stages `api/static/assets/recaps_raw/*.txt`. Weekly
  PDFs are versioned correctly; raw recap text is not committed by the current
  path combination.
- Email delivery currently has a fixed attachment matrix and does not cover all
  15 generated combinations. Its configuration should be made environment-
  backed before reuse.
- The daily loop catches failures at the region level. If one sector raises,
  the remaining sectors in that region are skipped and generation continues
  with the next region.
- The repository contains generated reports and scheduled output commits as
  part of its operating model. Clones are therefore substantially larger than
  the source code alone.
- There is no automated unit-test suite for the report pipeline. The workflow
  diagnostics and script entry points are useful smoke tests, but successful
  generation still depends on live external APIs and model output satisfying
  the formatting contract.
