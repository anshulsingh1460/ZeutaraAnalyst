from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, Tuple

TIER_ONE_SECTORS = {"b2b saas", "fintech", "proptech", "climate-tech", "climatetech"}
ADJACENT_SECTORS = {"consumer saas", "marketplace"}
DISQUALIFIED_SECTORS = {"hardware", "biotech", "deep tech", "government", "government contracting"}


def months_since(date_string: str, today: date | None = None) -> int:
    today = today or date.today()
    dt = datetime.strptime(date_string, "%Y-%m-%d").date()
    return (today.year - dt.year) * 12 + today.month - dt.month - (1 if today.day < dt.day else 0)


def score_account(row: Dict[str, Any], today: date | None = None) -> Tuple[int, list[str]]:
    score = 0
    reasons: list[str] = []

    stage = str(row.get("funding_stage", "")).strip().lower()
    if stage == "seed":
        score += 25
    elif stage == "pre-seed":
        score += 15
    elif stage == "series a":
        score += 10
    else:
        reasons.append("funding_stage_misfit")

    try:
        age = months_since(str(row.get("last_funding_date", "")), today=today)
        if 6 <= age <= 18:
            score += 20
        elif 0 <= age <= 5:
            score += 10
        elif 19 <= age <= 36:
            score += 5
        else:
            reasons.append("funding_event_outside_window")
    except Exception:
        reasons.append("missing_or_invalid_funding_date")

    revenue = str(row.get("revenue_signal", "")).strip().lower()
    if revenue == "confirmed_arr":
        score += 15
    elif revenue == "pre_rev_with_traction":
        score += 8
    else:
        reasons.append("weak_revenue_signal")

    intent = str(row.get("intent_signal", "")).strip().lower()
    if intent == "active":
        score += 15
    elif intent == "mild":
        score += 7

    try:
        team_size = int(row.get("team_size", 0))
        if 3 <= team_size <= 12:
            score += 10
        elif 13 <= team_size <= 25:
            score += 6
        elif 26 <= team_size <= 50:
            score += 2
        else:
            reasons.append("team_size_misfit")
    except Exception:
        reasons.append("missing_team_size")

    sector = str(row.get("sector", "")).strip().lower()
    if sector in TIER_ONE_SECTORS:
        score += 10
    elif sector in ADJACENT_SECTORS:
        score += 5
    else:
        reasons.append("sector_misfit")

    warm = str(row.get("warm_connection", "")).strip().lower()
    if warm == "shared":
        score += 5
    elif warm == "portfolio_adjacent":
        score += 3

    if stage in {"series b", "series c", "series d"}:
        reasons.append("disqualified_series_b_or_later")
    if sector in DISQUALIFIED_SECTORS:
        reasons.append("disqualified_sector")

    return score, reasons
