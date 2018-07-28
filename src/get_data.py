import json
from lxml.html import fromstring

from requests_html import HTMLSession

from Game import LiveGame
from OddGame import OddGame


TARGET_SCORES = [
    (0, 0),
    (1, 0),
    (0, 1),
    (2, 0),
    (0, 2)
]

def get_games_from_1x(mirror, session):
    """
    Scrape 1x for all live soccer games and returns a list of Games
    """
    url = f"{mirror}/LiveFeed/Get1x2_Zip?sports=1&count=1000&mode=4&"
    try:
        data = session.get(url, timeout=10)
    except Exception as e:
        print(e)

    json_data = json.loads(data.text)
    games = []
    for g in json_data.get('Value'):
        if not g.get('SC').get('CP'):
            continue

        minute = int(int(g.get('SC').get('TS', 0)) / 60)
#        if minute not in range(10, 25):
#            continue

        score = (
            g.get('SC').get('FS').get('S1', 0),
            g.get('SC').get('FS').get('S2', 0)
        )
#         if score not in TARGET_SCORES:
#             continue

        id = g.get('I')
        league = g.get('LE')
        teams = (g.get('O1E'), g.get('O2E'))
        games.append(LiveGame(id, league, teams, score, minute))

    return games


def get_games_from_odd(session):
    """
    Parse oddsekspert and return dict of live games
    """
    url = "https://oddsekspert.dk/livescore"

    try:
        html_doc = session.get(url, timeout=10).text
    except Exception as e:
        print("Exception in get_live_games()")
        print(e)
        return {}

    tree = fromstring(html_doc)
    left_teams = [t for t in tree.xpath('//tr[@class="match_list event_playing"]//td[@align="right"]//text()')]
    right_teams = [t for t in tree.xpath('//tr[@class="match_list event_playing"]//td[@align="left"]//text()')]
    teams = zip(left_teams, right_teams)

    links = [
        l.get("href") for l in tree.xpath('//td[@class="event_live"]//a')
    ]

    games = [OddGame(link, team) for team, link in zip(teams, links)]
    return games
