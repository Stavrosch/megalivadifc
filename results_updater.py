# results_updater.py
# Reads "ΜΕΓΑ ΛΙΒΑΔΙ FC.xlsx" (sheet "Φύλλο2") and writes matches JSON.
# NO try/except blocks (per user's request).

import pandas as pd, re, json
from datetime import datetime

EXCEL_PATH = "ΜΕΓΑ ΛΙΒΑΔΙ FC.xlsx"
SHEET_NAME = "Φύλλο2"
OUTPUT_JSON = "matches.json"

df = pd.read_excel(EXCEL_PATH, sheet_name=SHEET_NAME, header=None)
nrows, ncols = df.shape

def find_date_row_above(row_idx, max_lookback=10):
    for r in range(row_idx-1, max(-1, row_idx - max_lookback - 1), -1):
        c0 = df.iat[r,0]
        if not pd.isna(c0) and str(c0).strip().lower() == "date":
            # Look for location (Home/Away) in this Date row
            location = "Home"  # default
            for c in range(ncols):
                v = df.iat[r, c]
                if not pd.isna(v):
                    vs = str(v).strip().lower()
                    if vs == "home":
                        location = "Home"
                    elif vs == "away":
                        location = "Away"
            
            # Find the actual date
            for c in range(ncols):
                v = df.iat[r, c]
                if isinstance(v, (pd.Timestamp, datetime)):
                    return v, r, c, location
            if r+1 < nrows:
                for c in range(ncols):
                    v = df.iat[r+1, c]
                    if isinstance(v, (pd.Timestamp, datetime)):
                        return v, r+1, c, location
    return None, None, None, "Home"  # default to Home if not found

def find_nearest_date_above(row_idx, max_lookback=10):
    for r in range(row_idx, max(-1, row_idx - max_lookback) , -1):
        for c in range(ncols):
            v = df.iat[r, c]
            if isinstance(v, (pd.Timestamp, datetime)):
                return v, r, c
    return None, None, None

def find_score_near(row_idx, max_up=8, max_down=3):
    """
    Look around a 'Match' row for a valid score like '3-2' or '0–5'.
    Skips NaN and non-numeric pairs, avoiding mistaken matches like '2025-03'.
    """
    pattern = re.compile(r"\b(\d{1,2})\s*[-–]\s*(\d{1,2})\b")
    for r in range(max(row_idx - max_up, 0), min(row_idx + max_down + 1, nrows)):
        for c in range(ncols):
            val = df.iat[r, c]
            if pd.isna(val) or isinstance(val, (pd.Timestamp, datetime)):
                continue
            s = str(val).strip()
            # skip year-month patterns
            if re.match(r"20\d{2}[-/]\d{1,2}", s):
                continue
            m = pattern.search(s)
            if m:
                home, away = int(m.group(1)), int(m.group(2))
                # sanity check: valid football scores only
                if 0 <= home <= 20 and 0 <= away <= 20:
                    return f"{home}-{away}", r, c
    return None, None, None


matches = []

for i in range(nrows):
    first = df.iat[i, 0] if not pd.isna(df.iat[i, 0]) else ""
    first_str = str(first).strip().lower() if first is not None else ""
    if first_str == "match":
        row = df.iloc[i]
        opponent = ""
        outcome = None
        match_date = None
        location = "Home"  # Default to home
        
        # Get date AND location from the Date row above
        match_date, drow, dcol, location = find_date_row_above(i, max_lookback=10)
        
        if match_date is None:
            for c in range(ncols):
                if isinstance(df.iat[i, c], (pd.Timestamp, datetime)):
                    match_date = df.iat[i, c]
                    break
        if match_date is None:
            match_date, drow, dcol = find_nearest_date_above(i, max_lookback=10)
        
        # Find opponent in the Match row
        for c in range(ncols):
            cell = row[c]
            if pd.isna(cell):
                continue
            s = str(cell).strip()
            if s.upper() in ("W","L","D"):
                outcome = s.upper()
            if "vs" in s.lower():
                idx = s.lower().find("vs")
                opponent_candidate = s[idx+2:].strip()
                opponent = opponent_candidate.strip(" :.-")
        
        # find explicit score nearby
        result, score_row, score_col = find_score_near(i, max_up=8, max_down=3)
        
        # Adjust score order based on home/away
        if result and location == "Away":
            # For away matches, swap the score to show opponent first
            home_goals, away_goals = result.split('-')
            result = f"{away_goals}-{home_goals}"
        
        # parse player block
        stats_idx = None
        j = i + 1
        while j < nrows:
            cell0 = df.iat[j, 0]
            if not pd.isna(cell0) and str(cell0).strip().lower() == "stats":
                stats_idx = j
                break
            if not pd.isna(cell0) and str(cell0).strip().lower() in ("match", "date"):
                break
            j += 1
        
        players = []
        player_of_match = ""
        if stats_idx is not None:
            header_row = df.iloc[stats_idx]
            col_map = {}
            for col_idx in range(ncols):
                h = header_row[col_idx]
                if pd.isna(h):
                    continue
                hs = str(h).strip().lower()
                if hs in ("#", "number", "num"):
                    col_map["number"] = col_idx
                elif "name" in hs or "names" in hs or "όνομα" in hs:
                    if "name" not in col_map:
                        col_map["name"] = col_idx
                elif "play" in hs:
                    col_map["played"] = col_idx
                elif "goal" in hs:
                    if "goals" not in col_map:
                        col_map["goals"] = col_idx
                elif "assist" in hs:
                    col_map["assists"] = col_idx
                elif "pom" in hs or "player of the match" in hs:
                    col_map["pom"] = col_idx
            
            k = stats_idx + 1
            while k < nrows:
                r0 = df.iat[k, 0]
                r0s = str(r0).strip() if not pd.isna(r0) else ""
                if r0s.lower().startswith("player of the match"):
                    pom_name = ""
                    for c in range(ncols):
                        cell = df.iat[k, c]
                        if pd.isna(cell):
                            continue
                        s = str(cell).strip()
                        if "player of the match" in s.lower():
                            continue
                        if s:
                            pom_name = s
                            break
                    player_of_match = pom_name
                    break
                if r0s.lower() in ("match", "date"):
                    break
                
                name_val = None
                if "name" in col_map:
                    name_val = df.iat[k, col_map["name"]]
                else:
                    for c in range(1, ncols):
                        v = df.iat[k, c]
                        if not pd.isna(v) and isinstance(v, str) and v.strip():
                            name_val = v
                            break
                
                number = 0
                if "number" in col_map:
                    numcell = df.iat[k, col_map["number"]]
                    if not pd.isna(numcell):
                        if isinstance(numcell, (int, float)):
                            number = int(numcell)
                        else:
                            number = int(float(str(numcell)))
                
                if (pd.isna(name_val) or str(name_val).strip() == "") and number == 0:
                    k += 1
                    continue
                
                name = str(name_val).strip() if not pd.isna(name_val) else ""
                position = ""
                if "played" in col_map:
                    pc = df.iat[k, col_map["played"]]
                    if not pd.isna(pc):
                        position = str(pc).strip()
                        # Convert numeric positions to empty string (they didn't play)
                        if position.replace('.', '').isdigit():
                            if float(position) == 0:
                                position = ""
                            else:
                                position = "Played" 
                
                if not position:
                    k += 1
                    continue  # fallback for non-zero numbers
                
                goals = 0
                if "goals" in col_map:
                    gc = df.iat[k, col_map["goals"]]
                    if not pd.isna(gc):
                        if isinstance(gc, (int, float)):
                            goals = int(gc)
                        else:
                            goals = int(float(str(gc)))
                
                assists = 0
                if "assists" in col_map:
                    ac = df.iat[k, col_map["assists"]]
                    if not pd.isna(ac):
                        if isinstance(ac, (int, float)):
                            assists = int(ac)
                        else:
                            assists = int(float(str(ac)))
                
                players.append({
                    "number": number,
                    "name": name,
                    "position": position,
                    "goals": int(goals),
                    "assists": int(assists)
                })
                k += 1
        
        # if no explicit result, compute team goals and mark opponent as unknown
        team_goals = sum(p["goals"] for p in players)
        if not result:
            result = f"{team_goals}-?"
        
        # parse gf/ga if possible
        m = re.search(r"(\d+)\s*[-–]\s*(\d+|\?)", result)
        gf = int(m.group(1)) if m else None
        ga = None if (not m or m.group(2) == "?") else int(m.group(2))
        
        if outcome is None and gf is not None and ga is not None:
            if gf > ga: outcome = "W"
            elif gf == ga: outcome = "D"
            else: outcome = "L"
        
        points = 0
        if outcome == "W": points = 3
        elif outcome == "D": points = 1
        
        date_str = ""
        if match_date is not None:
            date_str = pd.to_datetime(match_date).strftime("%Y-%m-%d")
        
        match = {
            "date": date_str,
            "opponent": opponent,
            "location": location,
            "result": result if result else "",
            "outcome": outcome if outcome else "",
            "points": points,
            "player_of_match": player_of_match if player_of_match else "",
            "players": players
        }
        print("Parsed:", match["date"], match["location"], match["opponent"], match["result"], "outcome:", match["outcome"], "players:", len(players), "POM:", match["player_of_match"])
        matches.append(match)

# summary
played = len(matches)
wins = sum(1 for m in matches if m["outcome"] == "W")
draws = sum(1 for m in matches if m["outcome"] == "D")
losses = sum(1 for m in matches if m["outcome"] == "L")
points = sum(m["points"] for m in matches)

def parse_score(s):
    if not s: return (0,0)
    m = re.search(r"(\d+)\s*[-–]\s*(\d+|\?)", s)
    if m:
        left = int(m.group(1))
        right = 0 if m.group(2) == "?" else int(m.group(2))
        return (left, right)
    return (0,0)

goals_for = sum(parse_score(m["result"])[0] for m in matches)
goals_against = sum(parse_score(m["result"])[1] for m in matches)
goal_diff = goals_for - goals_against
win_pct = round((wins/played)*100,1) if played else 0.0

data = {
    "metadata": {
        "last_updated": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "total_matches": played,
        "source_file": EXCEL_PATH,
        "season": "2024-2025"
    },
    "summary": {
        "played": played,
        "wins": wins,
        "draws": draws,
        "losses": losses,
        "points": points,
        "goals_for": goals_for,
        "goals_against": goals_against,
        "goal_difference": goal_diff,
        "win_percentage": win_pct
    },
    "matches": matches
}

with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Wrote", OUTPUT_JSON)