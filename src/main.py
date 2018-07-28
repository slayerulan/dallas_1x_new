import time
import traceback
from collections import deque

from requests_html import HTMLSession

import get_data
from send_msg import send_msg
from get_current_mirror import get_current_mirror
from find_related_games import find_related_games


maxlen = 10
sended = dict()
sended_update = deque(maxlen=maxlen)
while True:
    session = HTMLSession()
    try: 
        cur_mirror = get_current_mirror(session)
    except Exception as e:
        continue

    games_from_1x = get_data.get_games_from_1x(cur_mirror, session)
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
            print('Suitable game')
            if g[0].teams not in sended.keys():
                send_msg(g[0])
                sended[g[0].teams] = g[0].score
                print(g[0])

    for g in related_games:
        if g[0].teams not in sended.keys():
            continue
        if g[0].score != sended.get(g[0].teams) and g[0].teams not in sended_update:
            out = g[0].out
            old_score = [int(s) for s in sended.get(g[0].teams).split("-")]
            new_score = [int(s) for s in g[0].score.split("-")]
            who_score = 0 if new_score[0] > old_score[0] else 1
            if who_score == out:
                print("Забил аут")
                send_msg("Забил аут:\n " + g)
                sended_update.append(g[0].teams)

    if len(sended) >= maxlen:
        sended.pop(list(sended.keys)[0])
