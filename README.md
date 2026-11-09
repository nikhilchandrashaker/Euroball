# Euroball Analytics

Interactive Euroleague / EuroCup player explorer built from play-by-play data: **player search**, skill radar, PIR trends, **statistical twins**, a sortable leaderboard, and league-wide trend charts (the three-point revolution).

## Run it
Open `index.html` in a browser (Chart.js loads from a CDN). To rebuild from the source workbook:
```
pip install pandas openpyxl
python build.py path/to/Euroball.xlsx
```

## Data
`Euroball.xlsx` has three sheets: Euroleague 2007-2019 and EuroCup 2012-2019 (play-by-play samples, ~10 / 8-17 games per season) and Euroleague 2021-22 (rounds 1-15, with box-score columns). Events are aggregated into `euroball_player_seasons.csv`.

## Metrics
- **PIR** = PTS + REB + AST + STL + BLK + FD - missed FG - missed FT - TO - shots rejected - PF
- **TS%** = PTS / (2 x (FGA + 0.44 x FTA)); **3PA rate** = 3PA / FGA
- **Radar**: percentile ranks (>= 5 games) for scoring, efficiency, rebounding, playmaking, defense (STL+BLK), foul drawing
- **Statistical twins**: nearest neighbors on z-scored per-game vectors (PTS, REB, AST, STL, BLK, TO, 3PA, FTA, FD, TS%)

## Caveats
The 2007-2019 sheets cover only ~10 Euroleague games per season, so most players there have 1-2 games; percentiles/twins need 5+ career games (mostly 2021-22 regulars).
Sampled games, not full seasons; "games" = games where a player logged at least one event; no minutes data (no per-36/usage); players matched by name across competitions.
