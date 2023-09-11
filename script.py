from yahoo_oauth import OAuth2
import yahoo_fantasy_api as y
import statistics
import tabulate
import logging
import string

logging.getLogger("yahoo_oauth").setLevel(logging.CRITICAL)
oauth = OAuth2(None, None, from_file="oauth2.json")

g = y.game.Game(oauth, "nfl")
leagueID = g.league_ids()[2]
l = y.league.League(oauth, leagueID)
standings = l.standings()
current_week = l.current_week()
print("running sync")
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

for week, scores in scoreboard.items():
    weeks_median = statistics.median(scores.values())
    
    median_scores[week] = weeks_median
    for id, score in scores.items():
        if score > weeks_median:
            teams[id]["wins"] += 1
        else:
            teams[id]["losses"] += 1
        teams[id]["total"] = teams[id].get("total", 0) + float(score)

s = [
    x[1]
    for x in sorted(
        teams.items(), key=lambda x: (x[1]["wins"], x[1]["total"]), reverse=True
    )
]

table = tabulate.tabulate([x.values() for x in s], s[0].keys(), tablefmt="html")
weeks_median = statistics.median(scoreboard[current_week -2].values())
weeks_max    = max(scoreboard[current_week - 2].items(), key = lambda k :k[1])
max_score = teams[weeks_max[0]]['name'] + ' ' f'{weeks_max[1]:3.2f}'
data = {'table': table, 'median': f'{weeks_median:3.2f}', 'max': max_score}

with open('index.template') as template_file:
    template = string.Template(template_file.read())

with open('index.html', 'w') as output_file:
    output_file.write(template.substitute(data))
    

