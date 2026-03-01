"""ESPN API integration for multi-sport team stats, injuries, schedules, and head-to-head."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import httpx

ESPN_API_BASE = "https://site.api.espn.com/apis/site/v2/sports"
_TIMEOUT = 10.0

# ── Sport configuration ───────────────────────────────────────────────────────

SPORT_CONFIG: dict[str, dict] = {
    "nba":   {"path": "basketball/nba"},
    "nfl":   {"path": "football/nfl"},
    "nhl":   {"path": "hockey/nhl"},
    "mlb":   {"path": "baseball/mlb"},
    "ncaab": {"path": "basketball/mens-college-basketball"},
    "ncaaf": {"path": "football/college-football"},
}


def _espn_base(sport: str) -> str:
    config = SPORT_CONFIG.get(sport.lower())
    if not config:
        return f"{ESPN_API_BASE}/basketball/nba"
    return f"{ESPN_API_BASE}/{config['path']}"


# ── Team maps (verified ESPN IDs) ─────────────────────────────────────────────

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

NFL_TEAM_MAP: dict[str, dict] = {
    "cardinals":      {"id": "22", "full": "Arizona Cardinals",          "abbr": "ARI"},
    "falcons":        {"id": "1",  "full": "Atlanta Falcons",            "abbr": "ATL"},
    "ravens":         {"id": "33", "full": "Baltimore Ravens",           "abbr": "BAL"},
    "bills":          {"id": "2",  "full": "Buffalo Bills",              "abbr": "BUF"},
    "panthers":       {"id": "29", "full": "Carolina Panthers",          "abbr": "CAR"},
    "bears":          {"id": "3",  "full": "Chicago Bears",              "abbr": "CHI"},
    "bengals":        {"id": "4",  "full": "Cincinnati Bengals",         "abbr": "CIN"},
    "browns":         {"id": "5",  "full": "Cleveland Browns",           "abbr": "CLE"},
    "cowboys":        {"id": "6",  "full": "Dallas Cowboys",             "abbr": "DAL"},
    "broncos":        {"id": "7",  "full": "Denver Broncos",             "abbr": "DEN"},
    "lions":          {"id": "8",  "full": "Detroit Lions",              "abbr": "DET"},
    "packers":        {"id": "9",  "full": "Green Bay Packers",          "abbr": "GB"},
    "texans":         {"id": "34", "full": "Houston Texans",             "abbr": "HOU"},
    "colts":          {"id": "11", "full": "Indianapolis Colts",         "abbr": "IND"},
    "jaguars":        {"id": "30", "full": "Jacksonville Jaguars",       "abbr": "JAX"},
    "chiefs":         {"id": "12", "full": "Kansas City Chiefs",         "abbr": "KC"},
    "raiders":        {"id": "13", "full": "Las Vegas Raiders",          "abbr": "LV"},
    "chargers":       {"id": "24", "full": "Los Angeles Chargers",       "abbr": "LAC"},
    "rams":           {"id": "14", "full": "Los Angeles Rams",           "abbr": "LAR"},
    "dolphins":       {"id": "15", "full": "Miami Dolphins",             "abbr": "MIA"},
    "vikings":        {"id": "16", "full": "Minnesota Vikings",          "abbr": "MIN"},
    "patriots":       {"id": "17", "full": "New England Patriots",       "abbr": "NE"},
    "saints":         {"id": "18", "full": "New Orleans Saints",         "abbr": "NO"},
    "giants":         {"id": "19", "full": "New York Giants",            "abbr": "NYG"},
    "jets":           {"id": "20", "full": "New York Jets",              "abbr": "NYJ"},
    "eagles":         {"id": "21", "full": "Philadelphia Eagles",        "abbr": "PHI"},
    "steelers":       {"id": "23", "full": "Pittsburgh Steelers",        "abbr": "PIT"},
    "49ers":          {"id": "25", "full": "San Francisco 49ers",        "abbr": "SF"},
    "seahawks":       {"id": "26", "full": "Seattle Seahawks",           "abbr": "SEA"},
    "buccaneers":     {"id": "27", "full": "Tampa Bay Buccaneers",       "abbr": "TB"},
    "bucs":           {"id": "27", "full": "Tampa Bay Buccaneers",       "abbr": "TB"},
    "titans":         {"id": "10", "full": "Tennessee Titans",           "abbr": "TEN"},
    "commanders":     {"id": "28", "full": "Washington Commanders",      "abbr": "WSH"},
}

NHL_TEAM_MAP: dict[str, dict] = {
    "ducks":          {"id": "25",     "full": "Anaheim Ducks",            "abbr": "ANA"},
    "bruins":         {"id": "1",      "full": "Boston Bruins",            "abbr": "BOS"},
    "sabres":         {"id": "2",      "full": "Buffalo Sabres",           "abbr": "BUF"},
    "flames":         {"id": "3",      "full": "Calgary Flames",           "abbr": "CGY"},
    "hurricanes":     {"id": "7",      "full": "Carolina Hurricanes",      "abbr": "CAR"},
    "blackhawks":     {"id": "4",      "full": "Chicago Blackhawks",       "abbr": "CHI"},
    "avalanche":      {"id": "17",     "full": "Colorado Avalanche",       "abbr": "COL"},
    "blue jackets":   {"id": "29",     "full": "Columbus Blue Jackets",    "abbr": "CBJ"},
    "stars":          {"id": "9",      "full": "Dallas Stars",             "abbr": "DAL"},
    "red wings":      {"id": "5",      "full": "Detroit Red Wings",        "abbr": "DET"},
    "oilers":         {"id": "6",      "full": "Edmonton Oilers",          "abbr": "EDM"},
    "panthers":       {"id": "26",     "full": "Florida Panthers",         "abbr": "FLA"},
    "kings":          {"id": "8",      "full": "Los Angeles Kings",        "abbr": "LA"},
    "wild":           {"id": "30",     "full": "Minnesota Wild",           "abbr": "MIN"},
    "canadiens":      {"id": "10",     "full": "Montreal Canadiens",       "abbr": "MTL"},
    "predators":      {"id": "27",     "full": "Nashville Predators",      "abbr": "NSH"},
    "devils":         {"id": "11",     "full": "New Jersey Devils",        "abbr": "NJ"},
    "islanders":      {"id": "12",     "full": "New York Islanders",       "abbr": "NYI"},
    "rangers":        {"id": "13",     "full": "New York Rangers",         "abbr": "NYR"},
    "senators":       {"id": "14",     "full": "Ottawa Senators",          "abbr": "OTT"},
    "flyers":         {"id": "15",     "full": "Philadelphia Flyers",      "abbr": "PHI"},
    "penguins":       {"id": "16",     "full": "Pittsburgh Penguins",      "abbr": "PIT"},
    "sharks":         {"id": "18",     "full": "San Jose Sharks",          "abbr": "SJ"},
    "kraken":         {"id": "124292", "full": "Seattle Kraken",           "abbr": "SEA"},
    "blues":          {"id": "19",     "full": "St. Louis Blues",          "abbr": "STL"},
    "lightning":      {"id": "20",     "full": "Tampa Bay Lightning",      "abbr": "TB"},
    "maple leafs":    {"id": "21",     "full": "Toronto Maple Leafs",      "abbr": "TOR"},
    "canucks":        {"id": "22",     "full": "Vancouver Canucks",        "abbr": "VAN"},
    "mammoth":        {"id": "129764", "full": "Utah Mammoth",             "abbr": "UTAH"},
    "golden knights": {"id": "37",     "full": "Vegas Golden Knights",     "abbr": "VGK"},
    "capitals":       {"id": "23",     "full": "Washington Capitals",      "abbr": "WSH"},
    "jets":           {"id": "28",     "full": "Winnipeg Jets",            "abbr": "WPG"},
}

MLB_TEAM_MAP: dict[str, dict] = {
    "diamondbacks":   {"id": "29", "full": "Arizona Diamondbacks",       "abbr": "ARI"},
    "braves":         {"id": "15", "full": "Atlanta Braves",             "abbr": "ATL"},
    "orioles":        {"id": "1",  "full": "Baltimore Orioles",          "abbr": "BAL"},
    "red sox":        {"id": "2",  "full": "Boston Red Sox",             "abbr": "BOS"},
    "cubs":           {"id": "16", "full": "Chicago Cubs",               "abbr": "CHC"},
    "white sox":      {"id": "4",  "full": "Chicago White Sox",          "abbr": "CHW"},
    "reds":           {"id": "17", "full": "Cincinnati Reds",            "abbr": "CIN"},
    "guardians":      {"id": "5",  "full": "Cleveland Guardians",        "abbr": "CLE"},
    "rockies":        {"id": "27", "full": "Colorado Rockies",           "abbr": "COL"},
    "tigers":         {"id": "6",  "full": "Detroit Tigers",             "abbr": "DET"},
    "astros":         {"id": "18", "full": "Houston Astros",             "abbr": "HOU"},
    "royals":         {"id": "7",  "full": "Kansas City Royals",         "abbr": "KC"},
    "angels":         {"id": "3",  "full": "Los Angeles Angels",         "abbr": "LAA"},
    "dodgers":        {"id": "19", "full": "Los Angeles Dodgers",        "abbr": "LAD"},
    "marlins":        {"id": "28", "full": "Miami Marlins",              "abbr": "MIA"},
    "brewers":        {"id": "8",  "full": "Milwaukee Brewers",          "abbr": "MIL"},
    "twins":          {"id": "9",  "full": "Minnesota Twins",            "abbr": "MIN"},
    "mets":           {"id": "21", "full": "New York Mets",              "abbr": "NYM"},
    "yankees":        {"id": "10", "full": "New York Yankees",           "abbr": "NYY"},
    "athletics":      {"id": "11", "full": "Athletics",                  "abbr": "ATH"},
    "phillies":       {"id": "22", "full": "Philadelphia Phillies",      "abbr": "PHI"},
    "pirates":        {"id": "23", "full": "Pittsburgh Pirates",         "abbr": "PIT"},
    "padres":         {"id": "25", "full": "San Diego Padres",           "abbr": "SD"},
    "giants":         {"id": "26", "full": "San Francisco Giants",       "abbr": "SF"},
    "mariners":       {"id": "12", "full": "Seattle Mariners",           "abbr": "SEA"},
    "cardinals":      {"id": "24", "full": "St. Louis Cardinals",        "abbr": "STL"},
    "rays":           {"id": "30", "full": "Tampa Bay Rays",             "abbr": "TB"},
    "rangers":        {"id": "13", "full": "Texas Rangers",              "abbr": "TEX"},
    "blue jays":      {"id": "14", "full": "Toronto Blue Jays",          "abbr": "TOR"},
    "nationals":      {"id": "20", "full": "Washington Nationals",       "abbr": "WSH"},
}

SPORT_TEAM_MAPS: dict[str, dict[str, dict]] = {
    "nba": NBA_TEAM_MAP,
    "nfl": NFL_TEAM_MAP,
    "nhl": NHL_TEAM_MAP,
    "mlb": MLB_TEAM_MAP,
}

# ── ESPN web URLs (for user-facing links) ─────────────────────────────────────

_ESPN_WEB_SPORT = {"nba": "nba", "nfl": "nfl", "nhl": "nhl", "mlb": "mlb"}

_ESPN_WEB_TEMPLATES: dict[str, str] = {
    "injury_report": "https://www.espn.com/{sport}/team/injuries/_/name/{abbr}",
    "team_stats":    "https://www.espn.com/{sport}/team/stats/_/name/{abbr}",
    "schedule":      "https://www.espn.com/{sport}/team/schedule/_/name/{abbr}",
    "head_to_head":  "https://www.espn.com/{sport}/team/schedule/_/name/{abbr}",
}


def get_espn_web_url(fn_name: str, team_name: str, sport: str = "nba") -> str | None:
    """Build a clickable ESPN web URL for a given tool call and team."""
    sport_key = sport.lower()
    web_sport = _ESPN_WEB_SPORT.get(sport_key)
    if not web_sport:
        return None
    info = resolve_team(team_name, sport_key)
    if not info:
        return None
    fn_key = fn_name.replace("get_", "")
    template = _ESPN_WEB_TEMPLATES.get(fn_key)
    if not template:
        return None
    return template.format(sport=web_sport, abbr=info["abbr"].lower())


# ── Team resolution ───────────────────────────────────────────────────────────

def resolve_team(name: str, sport: str = "nba") -> dict | None:
    """Resolve a team name/nickname to its ESPN mapping entry."""
    team_map = SPORT_TEAM_MAPS.get(sport.lower(), NBA_TEAM_MAP)
    key = name.lower().strip()
    if key in team_map:
        return team_map[key]
    # Try last word (handles "Los Angeles Lakers" → "lakers")
    last_word = key.rsplit(" ", 1)[-1]
    if last_word in team_map:
        return team_map[last_word]
    # Try matching against full names
    for entry in team_map.values():
        if key in entry["full"].lower():
            return entry
    return None


# ── ESPN API functions ────────────────────────────────────────────────────────

async def get_team_stats(team: str, stat_types: list[str] | None = None, sport: str = "nba") -> str:
    """Get current season stats for a team."""
    info = resolve_team(team, sport)
    if not info:
        return f"Error: Unknown team '{team}' for sport '{sport}'"

    base = _espn_base(sport)
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.get(f"{base}/teams/{info['id']}")
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


async def get_injury_report(team: str, sport: str = "nba") -> str:
    """Get the current injury report for a team."""
    info = resolve_team(team, sport)
    if not info:
        return f"Error: Unknown team '{team}' for sport '{sport}'"

    base = _espn_base(sport)
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.get(f"{base}/injuries")
            resp.raise_for_status()
            data = resp.json()
    except Exception as exc:
        return f"Error fetching injuries: {exc}"

    target_id = info["id"]
    full_name = info["full"]

    for team_entry in data.get("injuries", []):
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
    team_a: str, team_b: str, num_games: int = 5, sport: str = "nba",
) -> str:
    """Get recent head-to-head results between two teams."""
    info_a = resolve_team(team_a, sport)
    info_b = resolve_team(team_b, sport)
    if not info_a:
        return f"Error: Unknown team '{team_a}' for sport '{sport}'"
    if not info_b:
        return f"Error: Unknown team '{team_b}' for sport '{sport}'"

    base = _espn_base(sport)
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.get(f"{base}/teams/{info_a['id']}/schedule")
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
    team: str, days_back: int = 7, days_forward: int = 3, sport: str = "nba",
) -> str:
    """Get recent and upcoming schedule, detecting back-to-backs."""
    info = resolve_team(team, sport)
    if not info:
        return f"Error: Unknown team '{team}' for sport '{sport}'"

    base = _espn_base(sport)
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.get(f"{base}/teams/{info['id']}/schedule")
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
