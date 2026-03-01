import type { KalshiMarket } from "../api/kalshi";
import type { EdgeResult } from "../api/edge";
import { colors } from "../../colors.js";

export interface MarketRow {
  ticker: string;
  team1: string;
  team2: string;
  team1Color: string;
  team2Color: string;
  league: string;
  type: string;
  closesIn: string;
  closingUrgent: boolean;
  expiresAt: string; // ISO timestamp of game/event expiration
  volume: number;
  marketPrice: string;
  modelProb: string;
  edge: string;
  edgePositive: boolean;
  ev: string;
  evPositive: boolean;
  signal: "YES" | "NO";
  confidence: "High" | "Med" | "Low";
  confidencePercent: number;
}

// ── League + bet-type from series prefix ──────────────────────────────────────

const SERIES_META: Record<string, { league: string; type: string }> = {
  // NBA
  KXNBAGAME:   { league: "NBA",   type: "MONEYLINE" },
  KXNBASPREAD: { league: "NBA",   type: "SPREAD" },
  KXNBATOTAL:  { league: "NBA",   type: "TOTAL" },
  KXNBAPTS:    { league: "NBA",   type: "PROPS" },
  KXNBASTS:    { league: "NBA",   type: "PROPS" },
  KXNBAAST:    { league: "NBA",   type: "PROPS" },
  KXNBAREB:    { league: "NBA",   type: "PROPS" },
  KXNBA:       { league: "NBA",   type: "MONEYLINE" },
  // NFL
  KXNFLGAME:   { league: "NFL",   type: "MONEYLINE" },
  KXNFLSPREAD: { league: "NFL",   type: "SPREAD" },
  KXNFLTOTAL:  { league: "NFL",   type: "TOTAL" },
  KXNFL:       { league: "NFL",   type: "MONEYLINE" },
  // MLB
  KXMLBGAME:   { league: "MLB",   type: "MONEYLINE" },
  KXMLBSPREAD: { league: "MLB",   type: "SPREAD" },
  KXMLBTOTAL:  { league: "MLB",   type: "TOTAL" },
  KXMLB:       { league: "MLB",   type: "MONEYLINE" },
  // NHL
  KXNHLGAME:   { league: "NHL",   type: "MONEYLINE" },
  KXNHLTOTAL:  { league: "NHL",   type: "TOTAL" },
  KXNHL:       { league: "NHL",   type: "MONEYLINE" },
  // Soccer
  KXEPLGAME:   { league: "EPL",   type: "MONEYLINE" },
  KXEPL:       { league: "EPL",   type: "MONEYLINE" },
  KXMLSGAME:   { league: "MLS",   type: "MONEYLINE" },
  KXMLS:       { league: "MLS",   type: "MONEYLINE" },
  // Other
  KXUFC:       { league: "UFC",   type: "MONEYLINE" },
  KXNCAABGAME: { league: "NCAAB", type: "MONEYLINE" },
  KXNCAAB:     { league: "NCAAB", type: "MONEYLINE" },
  KXNCAAFGAME: { league: "NCAAF", type: "MONEYLINE" },
  KXNCAAF:     { league: "NCAAF", type: "MONEYLINE" },
};

function extractSeriesMeta(seriesTicker?: string, ticker?: string): { league: string; type: string } {
  // series_ticker is often empty in Kalshi responses — fall back to the ticker prefix
  const source = seriesTicker || ticker || "";
  const prefix = source.split("-")[0];
  // Try longest-match prefix first
  const sorted = Object.keys(SERIES_META).sort((a, b) => b.length - a.length);
  const match = sorted.find((k) => prefix.startsWith(k));
  return SERIES_META[match ?? ""] ?? { league: "SPORTS", type: "MONEYLINE" };
}

// ── Team code lookup tables ───────────────────────────────────────────────────

const NBA_CODES: Record<string, string> = {
  ATL: "Atlanta Hawks",       BOS: "Boston Celtics",
  BKN: "Brooklyn Nets",       CHA: "Charlotte Hornets",
  CHI: "Chicago Bulls",       CLE: "Cleveland Cavaliers",
  DAL: "Dallas Mavericks",    DEN: "Denver Nuggets",
  DET: "Detroit Pistons",     GSW: "Golden State Warriors",
  HOU: "Houston Rockets",     IND: "Indiana Pacers",
  LAC: "LA Clippers",         LAL: "Los Angeles Lakers",
  MEM: "Memphis Grizzlies",   MIA: "Miami Heat",
  MIL: "Milwaukee Bucks",     MIN: "Minnesota Timberwolves",
  NOP: "New Orleans Pelicans",NYK: "New York Knicks",
  OKC: "Oklahoma City Thunder",ORL: "Orlando Magic",
  PHI: "Philadelphia 76ers",  PHX: "Phoenix Suns",
  POR: "Portland Trail Blazers",SAC: "Sacramento Kings",
  SAS: "San Antonio Spurs",   TOR: "Toronto Raptors",
  UTA: "Utah Jazz",           WAS: "Washington Wizards",
};

const NFL_CODES: Record<string, string> = {
  ARI: "Arizona Cardinals",   ATL: "Atlanta Falcons",
  BAL: "Baltimore Ravens",    BUF: "Buffalo Bills",
  CAR: "Carolina Panthers",   CHI: "Chicago Bears",
  CIN: "Cincinnati Bengals",  CLE: "Cleveland Browns",
  DAL: "Dallas Cowboys",      DEN: "Denver Broncos",
  DET: "Detroit Lions",       GB:  "Green Bay Packers",
  GNB: "Green Bay Packers",   HOU: "Houston Texans",
  IND: "Indianapolis Colts",  JAX: "Jacksonville Jaguars",
  KC:  "Kansas City Chiefs",  KAN: "Kansas City Chiefs",
  LAC: "LA Chargers",         LAR: "Los Angeles Rams",
  LVR: "Las Vegas Raiders",   MIA: "Miami Dolphins",
  MIN: "Minnesota Vikings",   NE:  "New England Patriots",
  NWE: "New England Patriots",NO:  "New Orleans Saints",
  NOR: "New Orleans Saints",  NYG: "New York Giants",
  NYJ: "New York Jets",       PHI: "Philadelphia Eagles",
  PIT: "Pittsburgh Steelers", SEA: "Seattle Seahawks",
  SF:  "San Francisco 49ers", SFO: "San Francisco 49ers",
  TB:  "Tampa Bay Buccaneers",TAM: "Tampa Bay Buccaneers",
  TEN: "Tennessee Titans",    WAS: "Washington Commanders",
};

const MLB_CODES: Record<string, string> = {
  ARI: "Arizona Diamondbacks", ATL: "Atlanta Braves",
  BAL: "Baltimore Orioles",    BOS: "Boston Red Sox",
  CHC: "Chicago Cubs",         CWS: "Chicago White Sox",
  CIN: "Cincinnati Reds",      CLE: "Cleveland Guardians",
  COL: "Colorado Rockies",     DET: "Detroit Tigers",
  HOU: "Houston Astros",       KC:  "Kansas City Royals",
  KCR: "Kansas City Royals",   LAA: "Los Angeles Angels",
  LAD: "Los Angeles Dodgers",  MIA: "Miami Marlins",
  MIL: "Milwaukee Brewers",    MIN: "Minnesota Twins",
  NYM: "New York Mets",        NYY: "New York Yankees",
  OAK: "Oakland Athletics",    PHI: "Philadelphia Phillies",
  PIT: "Pittsburgh Pirates",   SD:  "San Diego Padres",
  SDP: "San Diego Padres",     SEA: "Seattle Mariners",
  SF:  "San Francisco Giants", SFG: "San Francisco Giants",
  STL: "St. Louis Cardinals",  TB:  "Tampa Bay Rays",
  TBR: "Tampa Bay Rays",       TEX: "Texas Rangers",
  TOR: "Toronto Blue Jays",    WAS: "Washington Nationals",
  WSN: "Washington Nationals",
};

const NHL_CODES: Record<string, string> = {
  ANA: "Anaheim Ducks",        ARI: "Arizona Coyotes",
  BOS: "Boston Bruins",        BUF: "Buffalo Sabres",
  CGY: "Calgary Flames",       CAR: "Carolina Hurricanes",
  CHI: "Chicago Blackhawks",   COL: "Colorado Avalanche",
  CBJ: "Columbus Blue Jackets",DAL: "Dallas Stars",
  DET: "Detroit Red Wings",    EDM: "Edmonton Oilers",
  FLA: "Florida Panthers",     LA:  "Los Angeles Kings",
  LAK: "Los Angeles Kings",    MIN: "Minnesota Wild",
  MTL: "Montreal Canadiens",   NSH: "Nashville Predators",
  NJD: "New Jersey Devils",    NYI: "New York Islanders",
  NYR: "New York Rangers",     OTT: "Ottawa Senators",
  PHI: "Philadelphia Flyers",  PIT: "Pittsburgh Penguins",
  SJ:  "San Jose Sharks",       SJS: "San Jose Sharks",
  SEA: "Seattle Kraken",
  STL: "St. Louis Blues",      TBL: "Tampa Bay Lightning",
  TOR: "Toronto Maple Leafs",  VAN: "Vancouver Canucks",
  UTA: "Utah Hockey Club",     VGK: "Vegas Golden Knights",
  WSH: "Washington Capitals",  WPG: "Winnipeg Jets",
};

const LEAGUE_CODES: Record<string, Record<string, string>> = {
  NBA: NBA_CODES, NFL: NFL_CODES, MLB: MLB_CODES, NHL: NHL_CODES,
};

function resolveTeamName(code: string, league: string): string {
  const table = LEAGUE_CODES[league];
  return table?.[code] ?? code;
}

// ── Parse matchup from event_ticker ──────────────────────────────────────────
// Format: SERIES-YYMMMDDTEAM1TEAM2 e.g. KXNBAGAME-26MAR01SACLAL
// The date is always YYMMMDD = 7 chars; remainder is concatenated team codes.
// For NBA/NHL/MLB 3-char codes → split at 3. For NFL 2-3 char codes, try both.

function parseMatchupFromEventTicker(eventTicker: string, league: string): [string, string] | null {
  const parts = eventTicker.split("-");
  if (parts.length < 2) return null;
  const datePlusTeams = parts[parts.length - 1]; // e.g. "26MAR01SACLAL"
  // Date is YYMMMDD = 7 chars
  const teamPart = datePlusTeams.slice(7); // e.g. "SACLAL"
  if (!teamPart || teamPart.length < 4) return null;

  const table = LEAGUE_CODES[league];
  if (!table) return null;

  // Try 3+3 split first (NBA, NHL, MLB)
  if (teamPart.length === 6) {
    const c1 = teamPart.slice(0, 3);
    const c2 = teamPart.slice(3, 6);
    if (table[c1] && table[c2]) {
      return [resolveTeamName(c1, league), resolveTeamName(c2, league)];
    }
  }
  // Try 2+2, 2+3, 3+2 for NFL short codes
  for (const split of [2, 3]) {
    const c1 = teamPart.slice(0, split);
    const c2 = teamPart.slice(split);
    if (table[c1] && table[c2]) {
      return [resolveTeamName(c1, league), resolveTeamName(c2, league)];
    }
  }
  // Partial: resolve what we can
  if (teamPart.length >= 3 && table[teamPart.slice(0, 3)]) {
    return [resolveTeamName(teamPart.slice(0, 3), league), "TBD"];
  }
  return null;
}

// ── Title-based fallback ──────────────────────────────────────────────────────

function extractTeamsFromTitle(title: string): [string, string] {
  // Strip leading "yes " / "no " Kalshi prefix
  const clean = title.replace(/^(yes|no)\s+/i, "").trim();
  const vsMatch = clean.match(/^(.+?)\s+(?:vs?\.?)\s+(.+?)(?:\s*[?•\-].*)?$/i);
  if (vsMatch) return [vsMatch[1].trim(), vsMatch[2].trim()];
  const dashMatch = clean.match(/^(.+?)\s*[-–]\s*(.+)$/);
  if (dashMatch) return [dashMatch[1].trim(), dashMatch[2].trim()];
  return [clean.slice(0, 16), "TBD"];
}

function extractTeams(market: KalshiMarket, league: string): [string, string] {
  // Best: parse event_ticker for known leagues
  const fromTicker = parseMatchupFromEventTicker(market.event_ticker ?? "", league);
  if (fromTicker) return fromTicker;
  // Fallback: parse title
  return extractTeamsFromTitle(market.title ?? "");
}

// ── Team color ────────────────────────────────────────────────────────────────

function getTeamColor(teamName: string, league: string): string {
  const leagueColors = (colors as Record<string, Record<string, { primary: string }>>)[league];
  if (leagueColors) {
    if (leagueColors[teamName]) return leagueColors[teamName].primary;
    const match = Object.keys(leagueColors).find(
      (k) =>
        k.toLowerCase().includes(teamName.toLowerCase()) ||
        teamName.toLowerCase().includes(k.toLowerCase().split(" ").pop()!)
    );
    if (match) return leagueColors[match].primary;
  }
  return "#475569";
}

// ── Time helpers ──────────────────────────────────────────────────────────────

function formatClosesIn(closeTime: string): string {
  const diff = new Date(closeTime).getTime() - Date.now();
  if (diff <= 0) return "Closed";
  const h = Math.floor(diff / 3_600_000);
  const m = Math.floor((diff % 3_600_000) / 60_000);
  const s = Math.floor((diff % 60_000) / 1_000);
  if (h > 0)
    return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
  return `${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
}

function isUrgent(closeTime: string): boolean {
  return new Date(closeTime).getTime() - Date.now() < 3_600_000;
}

// ── Edge formatting ───────────────────────────────────────────────────────────

function formatEdge(edge: EdgeResult) {
  return {
    edge: `${Math.abs(edge.edge * 100).toFixed(1)}%`,
    edgePositive: edge.edge > 0,
    ev: `${edge.ev >= 0 ? "+" : ""}${(edge.ev * 100).toFixed(1)}%`,
    evPositive: edge.ev > 0,
    signal: (edge.signal === "BUY YES" ? "YES" : "NO") as "YES" | "NO",
  };
}

// ── Main transform ────────────────────────────────────────────────────────────

export function toMarketRow(market: KalshiMarket, edgeResult: EdgeResult): MarketRow {
  const { league, type } = extractSeriesMeta(market.series_ticker, market.ticker);
  const [team1, team2] = extractTeams(market, league);
  const { edge, edgePositive, ev, evPositive, signal } = formatEdge(edgeResult);

  return {
    ticker: market.ticker,
    team1,
    team2,
    team1Color: getTeamColor(team1, league),
    team2Color: getTeamColor(team2, league),
    league,
    type,
    expiresAt: market.expected_expiration_time ?? market.close_time,
    closesIn: formatClosesIn(market.expected_expiration_time ?? market.close_time),
    closingUrgent: isUrgent(market.expected_expiration_time ?? market.close_time),
    volume: market.volume_24h ?? market.volume ?? 0,
    marketPrice: `${market.last_price.toFixed(1)}%`,
    modelProb: "—",
    edge,
    edgePositive,
    ev,
    evPositive,
    signal,
    confidence: "Low",
    confidencePercent: 0,
  };
}
