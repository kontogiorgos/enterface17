from AbstractPhase import AbstractPhase


class SetupPhase(AbstractPhase):

    def __init__(self):
        super(SetupPhase, self).__init__()
        self.name = "Setup"

    def start(self, game):
        # TODO: werewolves see each other. anything else?
        pass
