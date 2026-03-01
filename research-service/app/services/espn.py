"""ESPN API integration for NBA team stats, injuries, schedules, and head-to-head."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import httpx

ESPN_BASE = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba"
_TIMEOUT = 10.0

# ESPN team IDs for all 30 NBA teams.
# Keys are lowercase nicknames for fuzzy lookup.
NBA_TEAM_MAP: dict[str, dict] = {
    "hawks":          {"id": "1",  "full": "Atlanta Hawks",              "abbr": "ATL"},
    "celtics":        {"id": "2",  "full": "Boston Celtics",             "abbr": "BOS"},
    "nets":           {"id": "17", "full": "Brooklyn Nets",              "abbr": "BKN"},
    "hornets":        {"id": "30", "full": "Charlotte Hornets",          "abbr": "CHA"},
    "bulls":          {"id": "4",  "full": "Chicago Bulls",              "abbr": "CHI"},
    "cavaliers":      {"id": "5",  "full": "Cleveland Cavaliers",        "abbr": "CLE"},
    "cavs":           {"id": "5",  "full": "Cleveland Cavaliers",        "abbr": "CLE"},
    "mavericks":      {"id": "6",  "full": "Dallas Mavericks",           "abbr": "DAL"},
    "mavs":           {"id": "6",  "full": "Dallas Mavericks",           "abbr": "DAL"},
    "nuggets":        {"id": "7",  "full": "Denver Nuggets",             "abbr": "DEN"},
    "pistons":        {"id": "8",  "full": "Detroit Pistons",            "abbr": "DET"},
    "warriors":       {"id": "9",  "full": "Golden State Warriors",      "abbr": "GSW"},
    "rockets":        {"id": "10", "full": "Houston Rockets",            "abbr": "HOU"},
    "pacers":         {"id": "11", "full": "Indiana Pacers",             "abbr": "IND"},
    "clippers":       {"id": "12", "full": "LA Clippers",                "abbr": "LAC"},
    "lakers":         {"id": "13", "full": "Los Angeles Lakers",         "abbr": "LAL"},
    "grizzlies":      {"id": "29", "full": "Memphis Grizzlies",          "abbr": "MEM"},
    "heat":           {"id": "14", "full": "Miami Heat",                 "abbr": "MIA"},
    "bucks":          {"id": "15", "full": "Milwaukee Bucks",            "abbr": "MIL"},
    "timberwolves":   {"id": "16", "full": "Minnesota Timberwolves",     "abbr": "MIN"},
    "wolves":         {"id": "16", "full": "Minnesota Timberwolves",     "abbr": "MIN"},
    "pelicans":       {"id": "3",  "full": "New Orleans Pelicans",       "abbr": "NOP"},
    "knicks":         {"id": "18", "full": "New York Knicks",            "abbr": "NYK"},
    "thunder":        {"id": "25", "full": "Oklahoma City Thunder",      "abbr": "OKC"},
    "magic":          {"id": "19", "full": "Orlando Magic",              "abbr": "ORL"},
    "76ers":          {"id": "20", "full": "Philadelphia 76ers",         "abbr": "PHI"},
    "sixers":         {"id": "20", "full": "Philadelphia 76ers",         "abbr": "PHI"},
    "suns":           {"id": "21", "full": "Phoenix Suns",               "abbr": "PHX"},
    "trail blazers":  {"id": "22", "full": "Portland Trail Blazers",     "abbr": "POR"},
    "blazers":        {"id": "22", "full": "Portland Trail Blazers",     "abbr": "POR"},
    "kings":          {"id": "23", "full": "Sacramento Kings",           "abbr": "SAC"},
    "spurs":          {"id": "24", "full": "San Antonio Spurs",          "abbr": "SAS"},
    "raptors":        {"id": "28", "full": "Toronto Raptors",            "abbr": "TOR"},
    "jazz":           {"id": "26", "full": "Utah Jazz",                  "abbr": "UTA"},
    "wizards":        {"id": "27", "full": "Washington Wizards",         "abbr": "WAS"},
}


def resolve_team(name: str) -> dict | None:
    """Resolve a team name/nickname to its ESPN mapping entry."""
    key = name.lower().strip()
    if key in NBA_TEAM_MAP:
        return NBA_TEAM_MAP[key]
    # Try last word (handles "Los Angeles Lakers" → "lakers")
    last_word = key.rsplit(" ", 1)[-1]
    if last_word in NBA_TEAM_MAP:
        return NBA_TEAM_MAP[last_word]
    # Try matching against full names
    for entry in NBA_TEAM_MAP.values():
        if key in entry["full"].lower():
            return entry
    return None


async def get_team_stats(team: str, stat_types: list[str] | None = None) -> str:
    """Get current season stats for an NBA team."""
    info = resolve_team(team)
    if not info:
        return f"Error: Unknown team '{team}'"

    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.get(f"{ESPN_BASE}/teams/{info['id']}")
            resp.raise_for_status()
            data = resp.json()
    except Exception as exc:
        return f"Error fetching stats for {team}: {exc}"

    team_data = data.get("team", {})
    full_name = team_data.get("displayName", info["full"])

    lines = [f"=== {full_name} Season Stats ==="]

    record_items = team_data.get("record", {}).get("items", [])
    for item in record_items:
        rec_type = item.get("type", "")
        summary = item.get("summary", "N/A")
        if rec_type == "total":
            lines.append(f"Overall Record: {summary}")
            stats = {s["name"]: s["value"] for s in item.get("stats", [])}
            games_played = stats.get("gamesPlayed", stats.get("wins", 0) + stats.get("losses", 0))
            if "pointsFor" in stats and games_played:
                ppg = stats["pointsFor"] / games_played
                lines.append(f"Points Per Game: {ppg:.1f}")
            if "pointsAgainst" in stats and games_played:
                opp_ppg = stats["pointsAgainst"] / games_played
                lines.append(f"Points Against Per Game: {opp_ppg:.1f}")
        elif rec_type == "home":
            lines.append(f"Home Record: {summary}")
        elif rec_type == "road":
            lines.append(f"Away Record: {summary}")

    if len(lines) == 1:
        lines.append("No detailed stats available")

    return "\n".join(lines)


async def get_injury_report(team: str) -> str:
    """Get the current injury report for an NBA team."""
    info = resolve_team(team)
    if not info:
        return f"Error: Unknown team '{team}'"

    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.get(f"{ESPN_BASE}/injuries")
            resp.raise_for_status()
            data = resp.json()
    except Exception as exc:
        return f"Error fetching injuries: {exc}"

    target_id = info["id"]
    full_name = info["full"]

    for team_entry in data.get("injuries", []):
        # ESPN uses top-level id/displayName, not a nested "team" object
        entry_id = str(team_entry.get("id", ""))
        if entry_id == target_id:
            injuries = team_entry.get("injuries", [])
            if not injuries:
                return f"No injuries reported for {full_name}"
            lines = [f"=== {full_name} Injury Report ==="]
            for inj in injuries:
                player = inj.get("athlete", {}).get("displayName", "Unknown")
                status = inj.get("status", "Unknown")
                details = inj.get("details", {})
                injury_type = details.get("type", "")
                detail = details.get("detail", "")
                side = details.get("side", "")
                parts = [p for p in [side, injury_type, detail] if p and p != "Not Specified"]
                desc = " ".join(parts) if parts else inj.get("shortComment", "Unknown")
                lines.append(f"{player} - {status} ({desc})")
            return "\n".join(lines)

    return f"No injury data found for {full_name}"


async def get_head_to_head(
    team_a: str, team_b: str, num_games: int = 5
) -> str:
    """Get recent head-to-head results between two NBA teams."""
    info_a = resolve_team(team_a)
    info_b = resolve_team(team_b)
    if not info_a:
        return f"Error: Unknown team '{team_a}'"
    if not info_b:
        return f"Error: Unknown team '{team_b}'"

    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.get(f"{ESPN_BASE}/teams/{info_a['id']}/schedule")
            resp.raise_for_status()
            data = resp.json()
    except Exception as exc:
        return f"Error fetching schedule for {team_a}: {exc}"

    matchups: list[str] = []
    a_wins = 0
    b_wins = 0
    target_id_b = info_b["id"]

    for event in data.get("events", []):
        competitions = event.get("competitions", [])
        if not competitions:
            continue
        comp = competitions[0]
        competitors = comp.get("competitors", [])
        if len(competitors) < 2:
            continue

        opponent_ids = [c.get("team", {}).get("id") for c in competitors]
        if target_id_b not in opponent_ids:
            continue

        status = comp.get("status", {}).get("type", {})
        if not status.get("completed", False):
            continue

        date_str = event.get("date", "")[:10]
        scores = {}
        for c in competitors:
            tid = c.get("team", {}).get("id")
            raw_score = c.get("score", "?")
            if isinstance(raw_score, dict):
                raw_score = raw_score.get("displayValue", "?")
            scores[tid] = raw_score

        score_a = scores.get(info_a["id"], "?")
        score_b = scores.get(target_id_b, "?")

        winner_id = None
        for c in competitors:
            if c.get("winner"):
                winner_id = c.get("team", {}).get("id")

        if winner_id == info_a["id"]:
            a_wins += 1
            result = f"{info_a['abbr']} win"
        elif winner_id == target_id_b:
            b_wins += 1
            result = f"{info_b['abbr']} win"
        else:
            result = "unknown"

        matchups.append(f"{date_str}: {info_a['abbr']} {score_a} - {info_b['abbr']} {score_b} ({result})")

    matchups = matchups[-num_games:]

    if not matchups:
        return f"No recent head-to-head games found between {info_a['full']} and {info_b['full']}"

    lines = [f"=== {info_a['full']} vs {info_b['full']} (last {len(matchups)} games) ==="]
    lines.append(f"Series: {info_a['abbr']} {a_wins} - {b_wins} {info_b['abbr']}")
    lines.extend(matchups)
    return "\n".join(lines)


async def get_schedule(
    team: str, days_back: int = 7, days_forward: int = 3
) -> str:
    """Get recent and upcoming schedule, detecting back-to-backs."""
    info = resolve_team(team)
    if not info:
        return f"Error: Unknown team '{team}'"

    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.get(f"{ESPN_BASE}/teams/{info['id']}/schedule")
            resp.raise_for_status()
            data = resp.json()
    except Exception as exc:
        return f"Error fetching schedule for {team}: {exc}"

    now = datetime.now(timezone.utc)
    window_start = now - timedelta(days=days_back)
    window_end = now + timedelta(days=days_forward)

    games: list[dict] = []
    for event in data.get("events", []):
        date_str = event.get("date", "")
        try:
            game_dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except ValueError:
            continue

        if game_dt < window_start or game_dt > window_end:
            continue

        competitions = event.get("competitions", [])
        if not competitions:
            continue
        comp = competitions[0]
        competitors = comp.get("competitors", [])

        opponent = "Unknown"
        home_away = "unknown"
        for c in competitors:
            tid = c.get("team", {}).get("id")
            if tid == info["id"]:
                home_away = c.get("homeAway", "unknown")
            else:
                opponent = c.get("team", {}).get("displayName", "Unknown")

        status = comp.get("status", {}).get("type", {})
        completed = status.get("completed", False)

        score = ""
        if completed:
            scores = {}
            for c in competitors:
                tid = c.get("team", {}).get("id")
                raw_score = c.get("score", "?")
                if isinstance(raw_score, dict):
                    raw_score = raw_score.get("displayValue", "?")
                scores[tid] = raw_score
            our_score = scores.get(info["id"], "?")
            their_score = [s for t, s in scores.items() if t != info["id"]]
            their_score = their_score[0] if their_score else "?"
            won = any(c.get("winner") and c.get("team", {}).get("id") == info["id"] for c in competitors)
            score = f"{'W' if won else 'L'} {our_score}-{their_score}"

        games.append({
            "date": game_dt,
            "date_str": game_dt.strftime("%b %d"),
            "opponent": opponent,
            "home_away": "HOME" if home_away == "home" else "AWAY",
            "score": score,
            "completed": completed,
        })

    games.sort(key=lambda g: g["date"])

    # Detect back-to-backs
    for i in range(1, len(games)):
        diff = (games[i]["date"].date() - games[i - 1]["date"].date()).days
        if diff <= 1:
            games[i]["b2b"] = True
            games[i - 1]["b2b_next"] = True

    lines = [f"=== {info['full']} Schedule ({days_back}d back, {days_forward}d forward) ==="]
    for g in games:
        tag = ""
        if g.get("b2b"):
            tag = " [BACK-TO-BACK]"
        elif g.get("b2b_next"):
            tag = " [B2B NEXT DAY]"

        if g["completed"]:
            lines.append(f"{g['date_str']}: vs {g['opponent']} ({g['home_away']}) - {g['score']}{tag}")
        else:
            lines.append(f"{g['date_str']}: vs {g['opponent']} ({g['home_away']}) - UPCOMING{tag}")

    # Compute rest days to next game
    upcoming = [g for g in games if not g["completed"]]
    past = [g for g in games if g["completed"]]
    if past and upcoming:
        rest_days = (upcoming[0]["date"].date() - past[-1]["date"].date()).days - 1
        lines.append(f"\nRest days before next game: {rest_days}")

    if len(lines) == 1:
        lines.append("No games found in the requested window")

    return "\n".join(lines)
