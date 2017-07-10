from AbstractPhase import AbstractPhase
from random import choice


class NightPhase(AbstractPhase):

    def __init__(self):
        super(NightPhase, self).__init__()
        self.name = "Day"

    def start(self, game):
        # TODO: elimination part

        # choose a random alive villager
        return choice([p for p in game.get_alive_players() if not p.is_werewolf])

    @staticmethod
    def _collect_votes(alive_players):
        return {p: p.vote(alive_players) for p in alive_players}
