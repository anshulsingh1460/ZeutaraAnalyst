from __future__ import annotations

import json
import re
from dataclasses import dataclass, asdict
from datetime import date
from pathlib import Path
from typing import Any, Dict, Iterable, List

from .scoring import months_since, score_account

EMAIL_RE = re.compile(r"^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$", re.IGNORECASE)
DECISION_TITLES = ("founder", "co-founder", "ceo", "chief executive", "president")


@dataclass
class ContactResult:
    company: str
    domain: str
    contact_name: str
    title: str
    email: str
    linkedin_url: str
    icp_score: int
    funding_age_months: int | str
    quality_score: int
    source: str
    status: str
    reason: str


def load_signals(path: str | Path) -> Dict[str, List[Dict[str, Any]]]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def email_is_direct_and_domain_matched(email: str, domain: str) -> bool:
    if not EMAIL_RE.match(email or ""):
        return False
    local, email_domain = email.lower().split("@", 1)
    if email_domain != domain.lower():
        return False
    generic_locals = {"hello", "info", "sales", "contact", "team", "support"}
    return local not in generic_locals


def title_is_decision_maker(title: str) -> bool:
    title_l = (title or "").lower()
    return any(t in title_l for t in DECISION_TITLES)


def validate_contact(account: Dict[str, Any], contact: Dict[str, Any], today: date | None = None) -> ContactResult:
    today = today or date.today()
    score, score_reasons = score_account(account, today=today)
    domain = str(account.get("domain", "")).lower().strip()
    failures: list[str] = []

    try:
        funding_age = months_since(str(account.get("last_funding_date", "")), today=today)
    except Exception:
        funding_age = "unknown"
        failures.append("missing_funding_date")

    if score < 70:
        failures.append("icp_score_below_70")

    if isinstance(funding_age, int) and funding_age > 18:
        failures.append("funding_event_older_than_18_months")

    if not email_is_direct_and_domain_matched(str(contact.get("email", "")), domain):
        failures.append("email_not_verified_direct_domain_match")

    if not str(contact.get("linkedin_url", "")).startswith("https://www.linkedin.com/in/"):
        failures.append("missing_linkedin_profile_url")

    if not title_is_decision_maker(str(contact.get("title", ""))):
        failures.append("not_founder_or_decision_maker")

    if "disqualified_sector" in score_reasons or "disqualified_series_b_or_later" in score_reasons:
        failures.extend([r for r in score_reasons if r.startswith("disqualified")])

    quality_score = 100 - (len(set(failures)) * 15)
    status = "approved" if not failures else "quarantined"
    reason = "passed_all_quality_gates" if not failures else ";".join(sorted(set(failures)))

    return ContactResult(
        company=str(account.get("company", "")),
        domain=domain,
        contact_name=str(contact.get("name", "")),
        title=str(contact.get("title", "")),
        email=str(contact.get("email", "")),
        linkedin_url=str(contact.get("linkedin_url", "")),
        icp_score=score,
        funding_age_months=funding_age,
        quality_score=max(0, quality_score),
        source=str(contact.get("source", "unknown")),
        status=status,
        reason=reason,
    )


def find_contacts(accounts: Iterable[Dict[str, Any]], signals: Dict[str, List[Dict[str, Any]]], today: date | None = None) -> List[ContactResult]:
    results: list[ContactResult] = []
    for account in accounts:
        domain = str(account.get("domain", "")).lower().strip()
        candidates = signals.get(domain, [])
        if not candidates:
            score, _ = score_account(account, today=today)
            results.append(ContactResult(
                company=str(account.get("company", "")),
                domain=domain,
                contact_name="",
                title="",
                email="",
                linkedin_url="",
                icp_score=score,
                funding_age_months="unknown",
                quality_score=0,
                source="none",
                status="quarantined",
                reason="no_contact_found",
            ))
            continue
        ranked = sorted(candidates, key=lambda c: title_is_decision_maker(c.get("title", "")), reverse=True)
        results.append(validate_contact(account, ranked[0], today=today))
    return results


def to_dicts(results: Iterable[ContactResult]) -> list[dict[str, Any]]:
    return [asdict(r) for r in results]
