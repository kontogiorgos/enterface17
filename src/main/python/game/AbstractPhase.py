import logging
from Game import Game
from abc import ABCMeta
from abc import abstractmethod


class AbstractPhase(object):

    __metaclass__ = ABCMeta

    def __init__(self):
        self.name = "None"
        self.logger = logging.getLogger(Game.logname)

    def announce(self):
        return "{} phase started".format(self.name)

    @abstractmethod
    def start(self, game):
        raise NotImplementedError("use this function with one of the phases")
