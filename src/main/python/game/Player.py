from abc import abstractmethod
from random import choice


class Player(object):

    def __init__(self, name, is_robot=False, is_werewolf=False, gaze=(0, 0, 0)):
        self.name = name
        self.is_werewolf = is_werewolf
        self.is_robot = is_robot
        self.is_alive = True
        self.gaze = gaze

    @staticmethod
    def create_players(players_yaml_list):

        """
        Create a player tuple from a list of dictionaries.

        :param players_yaml_list: list(dict)
            a list of player descriptions.
            example of a list with a single description:
              - name: player1
                robot: False
                werewolf: True
        :return: tuple (Player)
            a tuple with Player objects based on the descriptions
        """

        players = []
        for player in players_yaml_list:
            players.append(RobotPlayer(player['name'], player['robot'], player['werewolf']) if player['robot'] else
                           HumanPlayer(player['name'], player['robot'], player['werewolf']))
        return tuple(players)

    def kill(self):

        """
        Kill this player.
        """

        self.is_alive = False

    def status(self):

        """
        Generate a YAML representation of the players's info and status.

        :return: str
            a YAML representation of the players's info and status
        """

        return\
            "- name: {}\n".format(self.name) +\
            "  alive: {}\n".format(self.is_alive) +\
            "  robot: {}\n".format(self.is_robot) +\
            "  werewolf: {}\n".format(self.is_werewolf)

    def status_short(self):
        return ("W" if self.is_werewolf else "V") + ("+" if self.is_alive else "-")

    @abstractmethod
    def vote(self, alive_players):
        pass


class HumanPlayer(Player):

    def __init__(self, name, is_robot=False, is_werewolf=False, gaze=(0, 0, 0)):
        super(HumanPlayer, self).__init__(name, is_robot=is_robot, is_werewolf=is_werewolf, gaze=gaze)

    def vote(self, alive_players):
        return choice(alive_players)


class RobotPlayer(Player):

    def __init__(self, name, is_robot=False, is_werewolf=False, gaze=(0, 0, 0)):
        super(RobotPlayer, self).__init__(name, is_robot=is_robot, is_werewolf=is_werewolf, gaze=gaze)

    def vote(self, alive_players):
        return choice(alive_players)
