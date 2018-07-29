import time
import traceback
from collections import deque

from requests_html import HTMLSession

import get_data
from send_msg import send_msg
from get_current_mirror import get_current_mirror
from find_related_games import find_related_games


TARGET_SCORES = [
    (0, 0),
    (1, 0),
    (0, 1),
    (2, 0),
    (0, 2)
]

maxlen = 10
sended = dict()
sended_update = deque(maxlen=maxlen)
while True:
    session = HTMLSession()
    try: 
        cur_mirror = get_current_mirror(session)
    except Exception as e:
        print(traceback.format_exc())
        continue

    unfiltred_games_from_1x = get_data.get_games_from_1x(cur_mirror, session)
    games_from_1x = [
        game 
        for game in unfiltred_games_from_1x
        if (game._minute in range(10, 25) and 
            game._score in TARGET_SCORES)
    ]
    games_from_odd = get_data.get_games_from_odd(session)

    related_games = find_related_games(games_from_1x, games_from_odd)
    print(f"Find {len(related_games)} related games")

    for g in related_games:
        try:
            g[0].fill_stats(cur_mirror, session)
            g[1].fill_stats(session)
        except ValueError as e:
            print(traceback.format_exc())
            print(e)
            continue

        if g[0].is_target(g[1].out) and g[1].averages_is_target():
            if not g[1].fav_coef >= 1.7:
                print('Coef is not match')
                continue
            if g[0].teams not in sended.keys():
                g[0].odd_url = g[1].url
                print('Suitable game')
                send_msg(str(g[0]))
                print('Sended')
                sended[g[0].teams] = (g[0].score, g[0].out)
                print(g[0])

    print(unfiltred_games_from_1x)
    print(sended.keys())
    for g in unfiltred_games_from_1x:
        if g.teams not in sended.keys():
            continue
        if g.score != sended.get(g.teams)[0] and g.teams not in sended_update:
            out = sended.get(g.teams)[1]
            old_score = sended.get(g.teams)[0]
            new_score = g.score[out]
            if new_score != old_score:
                print("Забил аут")
                send_msg("Забил аут:\n " + g.teams)
                sended_update.append(g.teams)

    if len(sended) >= maxlen:
        sended.pop(list(sended.keys)[0])
