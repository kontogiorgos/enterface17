from AbstractPhase import AbstractPhase
from collections import Counter


class DayPhase(AbstractPhase):

    def __init__(self):
        super(DayPhase, self).__init__()
        self.name = "Day"

    def start(self, game):
        # TODO: discussion part
        # TODO: accusation part

        # execution part - choose who to kill
        votes = self._collect_votes(game.get_alive_players())
        # TODO: if there is a tie, go for another vote
        return Counter(votes.values()).most_common(1)[0][0]

    @staticmethod
    def _collect_votes(alive_players):
        return {p: p.vote(alive_players) for p in alive_players}
