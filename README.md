# Zeutara Real Contact Finder Prototype

A runnable prototype for **Step 3: Find Real Contacts** in the Zeutara BD pipeline.

This prototype takes a list of ICP-qualified companies and returns founder-level contacts that are ready for outreach only if they pass the data quality gate:

1. Verified direct email address
2. LinkedIn profile URL
3. Confirmed funding event within the last 18 months
4. Composite ICP score of 70 or above

Records that fail any gate are quarantined rather than deleted.

## Why this component is load-bearing

The contact-finding step is the narrow point between a good target market and actual outreach. If this component is weak, the rest of the funnel fails quietly: emails bounce, sequences go to the wrong person, founder relevance drops, and Zeutara burns credibility before a human conversation ever starts.

This prototype focuses on proving the logic of the component rather than recreating a full Clay, Apollo, LinkedIn Sales Navigator, or Salesforce implementation. It simulates the waterfall enrichment motion with local data so a reviewer can run it in under 15 minutes.

## What it does

- Loads target accounts from a CSV
- Scores each account using Zeutara's ICP model
- Searches a local enrichment dataset for founder or GTM decision-maker contacts
- Generates likely direct email candidates when needed
- Validates email format, domain match, role fit, LinkedIn URL presence, funding recency, and ICP score
- Exports two CSV files:
  - `output/approved_contacts.csv`
  - `output/quarantined_contacts.csv`
- Produces a terminal summary with approved vs. quarantined counts

## What it does not do

- It does not call live Apollo, Clay, Hunter, Clearbit, Proxycurl, LinkedIn, Salesforce, or Smartlead APIs
- It does not scrape LinkedIn or bypass paywalls
- It does not send emails
- It does not guarantee that a guessed email exists on a real mail server
- It does not replace a production enrichment vendor

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m src.zeutara_contact_finder.cli --accounts data/sample_accounts.csv --signals data/sample_contact_signals.json --out output
```

Expected output:

```text
Processed 8 accounts
Approved contacts: 3
Quarantined records: 5
Wrote output/approved_contacts.csv
Wrote output/quarantined_contacts.csv
```

## Input format

`data/sample_accounts.csv` contains one row per company:

| column | description |
| --- | --- |
| company | Company name |
| domain | Company website domain |
| funding_stage | Pre-seed, Seed, Series A, etc. |
| last_funding_date | YYYY-MM-DD |
| revenue_signal | confirmed_arr, pre_rev_with_traction, none |
| intent_signal | active, mild, none |
| team_size | Employee count |
| sector | B2B SaaS, fintech, proptech, climate-tech, etc. |
| warm_connection | shared, portfolio_adjacent, cold |

## Output fields

`approved_contacts.csv` includes:

- company
- contact_name
- title
- email
- linkedin_url
- icp_score
- funding_age_months
- quality_score
- source
- reason

`quarantined_contacts.csv` includes the same fields plus the failed gate reason.

## How the prototype maps to the pipeline

Production pipeline equivalent:

- Apollo and LinkedIn Sales Navigator: contact sourcing
- Clay waterfall: enrichment and fallback search
- Hunter, Clearbit, Proxycurl, Apollo: alternate contact and email sources
- Salesforce: approved and quarantined records
- Smartlead: only receives records that pass the quality gate

Prototype equivalent:

- Local JSON signal file: mock enrichment sources
- Python scorer: ICP and data quality logic
- CSV outputs: approved records and quarantine queue

## Design choices

### 1. Quarantine over deletion

Failed records are preserved with a reason. This mirrors the operating rule that bad records should not disappear, because failure reasons reveal whether the issue is list quality, missing contact data, stale funding information, or ICP mismatch.

### 2. Human-reviewable output

The output is intentionally simple CSV so a reviewer can inspect it quickly. In production, this would write to Salesforce contact fields and trigger a Smartlead queue only after AE approval.

### 3. Small surface area

The prototype proves the most important behavior: only real, role-relevant, quality-gated contacts move forward. It does not attempt to build the full BD system.

## Run tests

```bash
pytest
```
