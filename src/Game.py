import json


class LiveGame:
    def __init__(self, id, league, teams, score, minute):
        self._id = id
        self._league = league
        self._teams = teams
        self._score = score
        self._minute = minute

    def __repr__(self):
        pass

    def __str__(self):
        return f'''*{self._league}*
{'-'.join(self._teams)}
Аут: {self._teams[self._out]}
Время: {self._minute}
Счёт: {'-'.join(str(s) for s in self._score)}
Атаки: {'/'.join(str(a) for a in self.attacks)} - {sum(self.attacks)}
Владение мячом: {'%/'.join(str(p) for p in self.possessions)}%
Опасные атаки: {'/'.join(str(d_a) for d_a in self.dan_attacks)} - {sum(self.dan_attacks)}
Удары в створ: {'/'.join(str(s) for s in self.shots_on)} - {sum(self.shots_on)}
Угловые: {'/'.join(str(c) for c in self.corners)} - {sum(self.corners)}'''

    def fill_stats(self, mirror, session):
        url = f"{mirror}/LiveFeed/GetGameZip?id={self._id}"
        try:
            info = session.get(url, timeout=10)
        except Exception as e:
            print(e)
            raise ConnectionError
        json_info = json.loads(info.text)
        self._stats = json_info.get('Value', {}).get('SC', {}).get('S', {})
        if not self._stats:
            raise ValueError('There is no stats')

        for i in self._stats:
            if i.get('Key') == 'Stat':
                stats_str = i.get('Value').split(";")
                i['Value'] = stats_str[2]

        self._stats_dict = {item.get('Key'): int(item.get('Value')) for item in self._stats}

    def is_target(self, out):
        self._out = out
        fav = 0 if out else 1
        self._fav = fav
        return all([
                self.dan_attacks[fav] > self.dan_attacks[out],
                self.attacks[fav] > self.attacks[out],
                self.possessions[fav] >= self.possessions[out],
                self.corners[fav] >= self.corners[out]
                ])
        

    @property
    def teams(self):
        return ' - '.join(self._teams)

    @property
    def possessions(self):
        f_pos = int(self._stats_dict.get('Stat', 0))
        return [
            f_pos,
            100 - f_pos if f_pos else 0
        ]

    @property
    def corners(self):
        return [
            self._stats_dict.get('ICorner1', 0), 
            self._stats_dict.get('ICorner2', 0)
        ]

    @property
    def reds(self):
        return [
            self._stats_dict.get('IRedCard1', 0), 
            self._stats_dict.get('IRedCard2', 0)
        ]

    @property
    def attacks(self):
        return [
            self._stats_dict.get('Attacks1', 0), 
            self._stats_dict.get('Attacks2', 0)
        ] 

    @property
    def dan_attacks(self):
        return [
            self._stats_dict.get('DanAttacks1', 0),
            self._stats_dict.get('DanAttacks2', 0)
        ]

    @property
    def shots_on(self):
        return [
            self._stats_dict.get('ShotsOn1', 0), 
            self._stats_dict.get('ShotsOn2', 0)
        ]

    @property
    def shots_off(self):
        return [
            self._stats_dict.get('ShotsOff1', 0), 
            self._stats_dict.get('ShotsOff2', 0)
        ]

    @property
    def url(self):
        return self._url

    @property
    def score(self):
        return self._score
