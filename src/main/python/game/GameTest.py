from Game import Game
from Player import Player
from ruamel import yaml
import os
from DayPhase import DayPhase


if __name__ == "__main__":
    game = Game(settings_file="settings.yaml")
    # print(yaml.round_trip_dump(game.status_all()).strip())

    players = game.players
    while game.in_progress:
        game.advance_phase()
    # game.kill_player(players[2])
    # game.advance_phase()
    # game.kill_player(players[5])
    # game.advance_phase()
    # game.kill_player(players[0])
    # game.advance_phase()

    # print("\n\nGame history\n" + "\n".join(game.history))