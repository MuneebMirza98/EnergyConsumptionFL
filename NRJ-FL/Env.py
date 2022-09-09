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
        # self.training_time = None

        self.network_energy_consumed = None
        # self.network_time = None

    # def start_simulation(self):
    #     self. simulation_started = True
    #
    # def stop_simulation(self):
    #     self.simulation_started = False

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
        # TODO read the yaml file and ask network and training energy consumption from Network and Computation
        error_msg = "not this information in my database, please make experiment and feed it"
        config_list = ["name of dataset",
                       "size of dataset",
                       "size of model",
                       "batch_size",
                       "number of workers",
                       "nbr of rounds",
                       "hardware",
                       "CPU_count",
                       "CPU freq"]  # Get values from YAML config

        self.network_energy_consumed = (self.network.network_energy_consumption_and_time_calculation(config_list[2]))*config_list[5]*config_list[4]
        self.training_energy_consumed = self.computation.training_energy_consumption(config_list)

        if self.computation.training_energy_consumption(config_list) == error_msg:
            return print(error_msg)

        return print(f'Total experiment energy consumption is {self.network_energy_consumed + self.training_energy_consumed}')
