from AbstractPhase import AbstractPhase
from collections import Counter


class DayPhase(AbstractPhase):

    def __init__(self):
        super(DayPhase, self).__init__()
        self.name = "Day"

    def start(self, game):
        # TODO: discussion part
        # TODO: accusation part

        # Execution part
        self._vote_to_execute(game.get_alive_players())

    def _vote_to_execute(self, alive_players, kill_targets):

        """
        Pick a player (villager or werewolf) to kill

        In case of tie(s), continue voting till there is
        a single player with the highest number of votes.
        The actual voting is performed by Player.vote(),
        see _collect_votes() for more details.

        :param alive_players: list(Player)
            the players in the game that are still alive
            (and therefore are allowed to vote).
        :param kill_targets: list(Player)
            the list of players that can be voted to be killed.
            this list is getting smaller and smaller (due to ties)
            till there is a single player in it (who will be killed),
            and does not store the full list of alive players in the game!
        :return: Player
            the player that was chosen to be killed
        """

        while len(kill_targets) != 1:
            votes = {p: p.vote(alive_players) for p in alive_players}
            kill_targets = Counter(votes.values()).most_common(1)[0]
        return kill_targets[0]
