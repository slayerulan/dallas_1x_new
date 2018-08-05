from itertools import product

from fuzzywuzzy import fuzz

def find_related_games(games_from_1x, games_from_odd):
    related_games = []
    seen = set()
    for g, g_odd in product(games_from_1x, games_from_odd):
        if ((g.teams, g_odd.teams) in seen
                or (g_odd.teams, g.teams) in seen):
            continue

        if g.teams == g_odd.teams:
            related_games.append((g, g_odd))
            continue

        ratio = fuzz.token_set_ratio(g.teams, g_odd.teams)
        if ratio > 80:
            related_games.append((g, g_odd))
            continue
        seen.add((g.teams, g_odd.teams))
        seen.add((g_odd.teams, g.teams))

    return related_games
