from yahoo_oauth import OAuth2
import yahoo_fantasy_api as y
import statistics
import tabulate
import logging
import string

def calc_scores(player_id, week):
    s = l.player_stats(player_id, 'week',week=week)
    points = (s[0]['Pass Yds'] * 0.04) \
            + (s[0]['Pass TD'] * 4) \
            + (s[0]['Int'] * -1) \
            + (s[0]['Rush Yds'] * 0.1) \
            + (s[0]['Rush TD'] * 6) \
            + (s[0]['Rec'] * 1) \
            + (s[0]['Rec Yds'] * 0.1) \
            + (s[0]['Rec TD'] * 6) \
            + (s[0]['Ret TD'] * 6) \
            + (s[0]['2-PT'] * 2) \
            + (s[0]['Fum Lost'] * -2) \
            + (s[0]['Fum Ret TD'] * 6) 
    return points

logging.getLogger("yahoo_oauth").setLevel(logging.CRITICAL)
oauth = OAuth2(None, None, from_file="oauth2.json")

g = y.game.Game(oauth, "nfl")
leagueID = g.league_ids()[3]
l = y.league.League(oauth, leagueID)
standings = l.standings()
current_week = l.current_week() 
if current_week == 1:
    current_week = 2

print("running sync")

teams = {}
for v in standings:
    teamkey = v["team_key"]
    teams[teamkey] = {
        "name": v["name"],
        "wins": int(v["outcome_totals"]["wins"]),
        "losses": int(v["outcome_totals"]["losses"]),
        "team": y.Team(oauth, team_key=teamkey)
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

            dict[team_id] = float(points)
        scoreboard[week-1] = dict

median_scores = {}
weeks_median = None

for week, scores in scoreboard.items():
    weeks_median = statistics.median(scores.values())
    
    median_scores[week] = weeks_median
    for id, score in scores.items():
        if score > weeks_median:
            teams[id]["wins"] += 1
        else:
            teams[id]["losses"] += 1
        teams[id]["total"] = teams[id].get("total", 0) + float(score)

max_flex = 0
winning_team = ''
flex_player = ''
for team_id, t in teams.items():
    roster = t['team'].roster();
    for player in roster:
        if player['selected_position'] == 'W/R/T':
            points = calc_scores(player['player_id'], current_week - 1)
            if points > max_flex: 
                max_flex = points
                flex_player = player['name']
                winning_team = t['name']

s = [
    {key: value for key, value in x[1].items() if key != 'team'}
    for x in sorted(
        teams.items(), key=lambda x: (x[1]["wins"], x[1]["total"]), reverse=True
    )
]

table = tabulate.tabulate([x.values() for x in s], s[0].keys(), tablefmt="html")
weeks_median = statistics.median(scoreboard[current_week - 2].values())
weeks_max    = max(scoreboard[current_week - 2].items(), key = lambda k :k[1])
max_score = teams[weeks_max[0]]['name'] + ' ' f'{weeks_max[1]:3.2f}'
data = {'table': table, 'median': f'{weeks_median:3.2f}', 'max': max_score, 'max_flex': winning_team + ' ' + flex_player + ' ' + f'{max_flex:3.2f}'}

with open('index.template') as template_file:
    template = string.Template(template_file.read())

with open('index.html', 'w') as output_file:
    output_file.write(template.substitute(data))
    

