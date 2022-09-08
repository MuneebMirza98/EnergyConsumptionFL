from Simulation.Network import Network
from Simulation.States import States
from Simulation.Computation import Computation


class Env:
    """
    Orchestrate the whole simulation environment. Creates all the other classes, sends the information about the
    simulation and ask for all energy consumption of the experiment to send the information to Bridge.
    """
    def __init__(self, simulation_config_yaml, **kwargs):
        """
        Attributes of Env. We have the 3 major instances (Computation, States and Network).
        """

        self.simulation_config_yaml = simulation_config_yaml

        self.simulation_started = False

        self.network = Network()
        self.states = States()
        self.computation = Computation()

        self.training_energy_consumed = None
        self.training_time = None

        self.network_energy_consumed = None
        self.network_time = None

    def start_simulation(self):
        self. simulation_started = True

    def stop_simulation(self):
        self.simulation_started = False

    def get_states(self, guid, timestamp):
        """
        Function which will give the state of each device at the timestamp needed

        :param guid: Guid of the device we want
        :param timestamp: timestamp needed

        """
        return self.states.simulated_state(guid, timestamp)

    def simulate_experience(self):
        """
        Function which will run all the simulation
        """
