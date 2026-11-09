"""Euroball builder: turns Euroball.xlsx play-by-play into a player-season table + index.html"""
import pandas as pd, json, re, sys
SRC = sys.argv[1] if len(sys.argv) > 1 else '/mnt/user-data/uploads/Euroball.xlsx'
x = pd.read_excel(SRC, sheet_name=None)
F = ['pts','fgm','fga','tpm','tpa','ftm','fta','reb','oreb','ast','stl','tov','blk','blka','pf','fd']
MAP = {  # PLAYTYPE -> stat increments (old play-by-play sheets)
 '2FGM':dict(pts=2,fgm=1,fga=1), '2FGA':dict(fga=1), '2FGAB':dict(fga=1),
 'LAYUPMD':dict(pts=2,fgm=1,fga=1), 'LAYUPATT':dict(fga=1), 'DUNK':dict(pts=2,fgm=1,fga=1),
 '3FGM':dict(pts=3,fgm=1,fga=1,tpm=1,tpa=1), '3FGA':dict(fga=1,tpa=1), '3FGAB':dict(fga=1,tpa=1),
 'FTM':dict(pts=1,ftm=1,fta=1), 'FTA':dict(fta=1), 'D':dict(reb=1), 'O':dict(reb=1,oreb=1),
 'AS':dict(ast=1), 'ST':dict(stl=1), 'TO':dict(tov=1), 'FV':dict(blk=1), 'AG':dict(blka=1),
 'CM':dict(pf=1), 'OF':dict(pf=1), 'RV':dict(fd=1)}
rows = []
for sheet, comp in [('euroleague','Euroleague'), ('eurocup','EuroCup')]:
    d = x[sheet].dropna(subset=['PLAYER']).copy()
    d['t'] = d.PLAYTYPE.str.strip(); d = d[d.t.isin(MAP)]
    for c in F: d[c] = d.t.map(lambda t: MAP[t].get(c, 0))
    d['g'] = d.year.astype(str)+'-'+d.gamenumber.astype(str)
    d = d.rename(columns={'PLAYER':'player','TEAM':'team','year':'season'})
    d['comp'] = comp; rows.append(d[['player','team','season','comp','g']+F])
e = x['dataset'].dropna(subset=['player']).copy()
st = e.stat.str.strip()
def S(p): return st.str.startswith(p).astype(int)
mk2, ms2, mk3, ms3 = S('Two Pointer'), S('Missed Two'), S('Three Pointer'), S('Missed Three')
ftm, fts = S('Free Throw In'), S('Missed Free')
e = e.assign(fgm=mk2+mk3, fga=mk2+ms2+mk3+ms3, tpm=mk3, tpa=mk3+ms3, ftm=ftm, fta=ftm+fts, pts=2*mk2+3*mk3+ftm,
             reb=S('Def Reb')+S('Off Reb'), oreb=S('Off Reb'), ast=S('Assist'), stl=S('Steal'), tov=S('Turnover'),
             blk=S('Block'), blka=S('Shot Rejected'), pf=S('Foul')+S('Offensive Foul')+S('Technical')+S('Unsportsmanlike')+S('Coach Foul')+S('Bench Foul'), fd=S('Foul Drawn'))
e['pf'] = e.pf - e.fd   # 'Foul Drawn' also starts with 'Foul'
e['g'] = e['round'].astype(str)+'-'+e.game.astype(str); e['season'] = 2021; e['comp'] = 'Euroleague'
rows.append(e[['player','team','season','comp','g']+F])
a = pd.concat(rows)
# 2021-22 box-score columns can include non-FG point rows; keep as-is (PTS from source)
agg = a.groupby(['player','comp','season']).agg(team=('team', lambda s: s.mode().iat[0]), g=('g','nunique'), **{c:(c,'sum') for c in F}).reset_index()
agg = agg[agg.g >= 1]
def nice(n):
    p = [w.strip().title() for w in n.split(',')]; return ' '.join(p[::-1]) if len(p)==2 else n.title()
agg['name'] = agg.player.map(nice)
agg['team'] = agg.team.str.title().str.replace(r'\bB\.C\.$','',regex=True).str.strip()
cols = ['name','team','comp','season','g']+F
agg[cols].to_csv('euroball_player_seasons.csv', index=False)
# team-season shot mix for the trends tab
rows_json = agg[cols].values.tolist()
tr = agg.groupby(['comp','season'])[F].sum().reset_index()
trend = {c: tr[tr.comp==c][['season','fga','tpa','tpm','fgm','pts','tov','ast']].values.tolist() for c in tr.comp.unique()}
html = open('template.html').read().replace('/*DATA*/', 'const COLS=%s;const ROWS=%s;const TREND=%s;' % (json.dumps(cols), json.dumps(rows_json, separators=(',',':')), json.dumps(trend)))
open('index.html','w').write(html)
print(len(agg), agg.name.nunique(), 'player-seasons /', 'players')
