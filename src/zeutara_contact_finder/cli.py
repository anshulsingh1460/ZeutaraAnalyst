from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from .finder import find_contacts, load_signals, to_dicts


def main() -> None:
    parser = argparse.ArgumentParser(description="Find and quality-gate real founder contacts for Zeutara outreach.")
    parser.add_argument("--accounts", required=True, help="Path to accounts CSV")
    parser.add_argument("--signals", required=True, help="Path to local contact signal JSON")
    parser.add_argument("--out", default="output", help="Output directory")
    args = parser.parse_args()

    accounts_df = pd.read_csv(args.accounts)
    signals = load_signals(args.signals)
    results = find_contacts(accounts_df.to_dict("records"), signals)
    results_df = pd.DataFrame(to_dicts(results))

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    approved_path = out_dir / "approved_contacts.csv"
    quarantine_path = out_dir / "quarantined_contacts.csv"

    approved = results_df[results_df["status"] == "approved"]
    quarantined = results_df[results_df["status"] == "quarantined"]

    approved.to_csv(approved_path, index=False)
    quarantined.to_csv(quarantine_path, index=False)

    print(f"Processed {len(results_df)} accounts")
    print(f"Approved contacts: {len(approved)}")
    print(f"Quarantined records: {len(quarantined)}")
    print(f"Wrote {approved_path}")
    print(f"Wrote {quarantine_path}")


if __name__ == "__main__":
    main()
