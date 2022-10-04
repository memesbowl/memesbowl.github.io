from yahoo_oauth import OAuth2
import yahoo_fantasy_api as y
import statistics
import tabulate
import logging
import string

logging.getLogger("yahoo_oauth").setLevel(logging.CRITICAL)
oauth = OAuth2(None, None, from_file="oauth2.json")

g = y.game.Game(oauth, "nfl")
for year in range(0,3):
    leagueID = g.league_ids()[year]
    l = y.league.League(oauth, leagueID)
    standings = l.standings()
    current_week = l.current_week()
    teams = {}
    for v in standings:
        teamkey = v["team_key"]
        teams[teamkey] = {
            "name": v["name"],
            "wins": int(v["outcome_totals"]["wins"]),
            "losses": int(v["outcome_totals"]["losses"]),
        }


    scoreboard = {}
    # For each week
    for week in range(1, current_week):
        matchup = l.matchups(week)
        weeks_matchups = matchup["fantasy_content"]["league"][1]["scoreboard"]["0"][
            "matchups"
        ]

        dict = {}
        total = {}
        # For each mactchup that week
        for k, v in weeks_matchups.items():
            if k == "count":
                continue
            match = v["matchup"]
            match_teams = match["0"]["teams"]

            # For each player in the matchup
            for k, v in match_teams.items():
                if k == "count":
                    break
                team_id = v["team"][0][0]["team_key"]
                points = v["team"][1]["team_points"]["total"]
                proj_points = v["team"][1]["team_projected_points"]["total"]
                dict[team_id] = float(points)
            scoreboard[week-1] = dict

    median_scores = {}
    weeks_median = None
    #weeks_max = max(scoreboard.values())
    min_score = 0

    for week, scores in scoreboard.items():

        for id, score in scores.items():
            teams[id]["total"] = teams[id].get("total", 0) + float(score)
            if score > min_score:
                max_team = teams[id]

    print(min_score)
    

