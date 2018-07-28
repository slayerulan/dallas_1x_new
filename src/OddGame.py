from lxml.html import fromstring
from requests_html import HTMLSession


class OddGame:
    def __init__(self, url, teams):
        self._url = url
        self._teams = teams

    def __str__(self):
        return f"""
{self.teams}
{self._url}
"""

    @property
    def teams(self):
        return ' - '.join(self._teams)

    def averages_is_target(self):
        averages = self.calculate_averages(self._out)
        return averages[0] < averages[1]

    def concat_titles(self, games):
        n = []
        for g in games:
            for t in g.split(" vs "):
                if t.strip():
                    n.append(t.strip())
        return list(zip(n[::3], n[1::3], n[2::3]))

    def calculate_averages(self, team_number):
        team = self._teams[team_number]
        sum_goals = 0
        sum_missed_goals = 0
        if not self._teams_history[team_number]:
            return [0, 0]
        for g in self._teams_history[team_number]:
            try:
                goals = [int(goal) for goal in g[2].split("-")]
            except ValueError:
                print('Verror in calculate_averages')
                print(f"{g}")
                return [0, 0]
            if g[0] == team:
                sum_goals += goals[0]
                sum_missed_goals += goals[1]
            else:
                sum_goals += goals[1]
                sum_missed_goals += goals[0]
        stats = [
            sum_goals / len(self._teams_history[team_number]),
            sum_missed_goals / len(self._teams_history[team_number]),
        ]
        return stats

    def fill_stats(self, session):
        try:
            html_doc = session.get(self._url, timeout=10)
        except Exception as e:
            print(e)
            raise ValueError("Can't get html_doc")
        self._tree = fromstring(html_doc.text)
        self.identify_fav_and_out()
        history = self.parse_head2head()
        self.fill_teams_history(history)
        self._fav_averages = self.calculate_averages(self._fav) 
        self._out_averages = self.calculate_averages(self._out) 

    @property
    def out(self):
        return self._out

    @property
    def fav(self):
        return self._fav

    def parse_coef(self, win_or_loose):
        try:
            return float(
            self._tree.xpath(f'//td[@class="odds-row-{win_or_loose}"]//text()')[0]
        )
        except IndexError:
            return 0

    def identify_fav_and_out(self):
        win_coef = self.parse_coef("win")
        loose_coef = self.parse_coef("loose")
        self._fav = 0 if win_coef < loose_coef else 1
        self._out = int(not self._fav)
        self._fav_coef = min(win_coef, loose_coef)

    @property
    def fav_coef(self):
        return self._fav_coef

    def parse_head2head(self):
        h2h = [
            g
            for g in self._tree.xpath(
                '//tr[@class="h2h-data"]//td//table//tr//td//text()'
            )
            if "/" not in g
        ]
        return self.concat_titles(h2h)

    def fill_teams_history(self, history):
        self._teams_history = []

        self._teams_history.append(
            [g for g in history if self._teams[0] in g and self._teams[1] not in g]
        )
        if len(self._teams_history[0]) > 5:
            self._teams_history[0] = self._teams_history[0][:5]

        self._teams_history.append(
            [g for g in history if self._teams[1] in g and self._teams[0] not in g]
        )
        if len(self._teams_history[1]) > 5:
            self._teams_history[1] = self._teams_history[1][:5]

