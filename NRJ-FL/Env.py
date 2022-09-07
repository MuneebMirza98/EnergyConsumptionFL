from Simulation.Network import Network
from Simulation.States import States
from Simulation.Computation import Computation


class Env:
    """
    Orchestrate the whole simulation environment. Creates all the other classes, sends the information about the
    simulation and ask for all energy consumption of the experiment to send the information to Bridge.
    """

    def __init__(self, **kwargs):
        """
        FIXME attributs de SimulationEnvironment à compléter
        """
        self.network = Network()
        self.states = States()
        self.computation = Computation()

        # self.training_energy_consumed = None
        # self.training_time = None
        #
        # self.network_energy_consumed = None
        # self.network_time = None

    def get_states(self, guid, timestamp):
        """
        Fonction qui permettra de connaître l'état de l'ensemble des devices

        :param guid: Guid du device dont on souhaite connaître l'état
        :param timestamp: timestamp qui nous intéresse

        :return: booléen True ou False. True si disponible, False sinon
        """
        return self.states.simulated_state(guid, timestamp)

    def simulate_experience(self,):
        """
        Fonction qui permettra de lancer toute la simulation, les calculs,
        """