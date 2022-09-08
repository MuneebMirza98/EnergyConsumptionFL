import math
import pandas as pd
from ..States.States import *


class Network:
    """
    Mother class of every possible networks (cellular, access and core). This class creates the numeric network,
    with energy consumption values per Go which will be used by Env calculate the energy total consumption.
    """
    def __init__(self, **kwarg):
        """
        Attributes of Network. Kwargs params are precised here
        :param kwarg: - Connexion of the devices, if the access network is 2G/3G/4G/5G, upload and download speeds.
                      - Path where we want to save the CSV output
        """

        self.network_path = kwarg.get(
            'network_path',
            '/home/osboxes/PycharmProjects/clustered-fl/SimEnv/Simulation/Network/network_output.csv'
        )

        self.worker_numbers = None

        self.mobile_1GO = kwarg.get('mobile_1GO', 495)  # Wh
        self.download_speed_2G = kwarg.get('download_speed_2G', 7.2)  # Mbps
        self.download_speed_3G = kwarg.get('download_speed_3G', 42)  # Mbps
        self.download_speed_4G = kwarg.get('download_speed_4G', 300)  # Mbps
        self.download_speed_5G = kwarg.get('download_speed_5G', 10000)  # Mbps
        self.upload_speed_2G = kwarg.get('upload_speed_2G', 2)  # Mbps
        self.upload_speed_3G = kwarg.get('upload_speed_3G', 22)  # Mbps
        self.upload_speed_4G = kwarg.get('upload_speed_4G', 150)  # Mbps
        self.upload_speed_5G = kwarg.get('upload_speed_5G', 1000)  # Mbps

        self.fix_ADSL_1GO = kwarg.get('fix_ADSL_1GO', 29)  # Wh
        self.upload_speed_ADSL = kwarg.get('upload_speed_ADSL', 86)  # Mbps
        self.download_speed_ADSL = kwarg.get('download_speed_ADSL', 100)  # Mbps

        self.fix_fiber_1GO = kwarg.get('fix_fiber_1GO', 9.5)  # Wh
        self.upload_speed_fiber = kwarg.get('upload_speed_fiber', 600)  # Mbps
        self.download_speed_fiber = kwarg.get('upload_speed_fiber', 1000)  # Mbps

        self.fix_core_network_1GO = kwarg.get('fix_core_network', 7)  # Wh
        self.mobile_core_network_1GO = kwarg.get('mobile_core_network', 30)  # Wh

        self.network_infos_df = None
        self.network_df_reduced = None

        self.network_energy_consumption = None

    def create_simulated_network(self, state):
        """
        This method will create the numeric clone of the network architecture

        :param state: Instance of States class

        :return:  Dataframe and a CSV with all network and distance information between a device and the central server
                  at each timestamp.
        """

        if os.path.exists(self.network_path):
            self.network_infos_df = pd.read_csv(self.network_path)
            return

        distance_list = []

        if state.states_activated:
            for i in range(state.perma_states_df.shape[0]):
                distance = math.sqrt((state.perma_states_df['Position_X'][i] - state.server_position_x) ** 2 + (
                        state.perma_states_df['Position_Y'][i] - state.server_position_y) ** 2)
                distance_list.append(distance)

            network_infos_df = pd.DataFrame()
            network_infos_df['Guid'] = state.perma_states_df['Guid']
            network_infos_df['Timestamp'] = state.timestamp_df
            network_infos_df['Distance'] = distance_list
            network_infos_df['Network'] = state.perma_states_df['Network']

            self.network_infos_df = network_infos_df

            network_infos_df.to_csv(self.network_path, index=False)

        # TODO If States is disabled

        return

    def network_request(self, guid, timestamp):
        """
        Method which will allows to get the information on the network by requesting the network_output.csv file, with a
        particular guis and at a specific timestamp.

        :param guid: guid of the device we want
        :param timestamp: timestamp needed
        """
        with open(self.network_path, 'r', encoding='utf-8') as f:
            df = pd.read_csv(f)
            self.network_df_reduced = df.loc[(df['Timestamp'] == str(timestamp)) & (df['Guid'] == guid)].iloc[0]

    def network_energy_consumption_and_time_calculation(self, data_quantity, fix_network='fiber', mobile_network='4G'):
        """
        Function which will calculate values of energy consumption of the communication between central server and
        devices, and give the time of this communication

        :param data_quantity: number of parameters of the model
        :param fix_network: the access network of the device if it's a fix network
        :param mobile_network: the access network of the device if it's a fix network

        :return: list with energy consumption in Wh and upload and download times in seconds
        """

        if self.network_df_reduced['Network'] == "mobile":
            energy_consumption = data_quantity*(self.mobile_1GO+self.mobile_core_network_1GO)
            # TODO taking distance into account, and change the 4G and fiber default, but works for now

            if mobile_network == "2G":
                download_communication_time = data_quantity/self.download_speed_2G
                upload_communication_time = data_quantity/self.upload_speed_2G
            elif mobile_network == "3G":
                download_communication_time = data_quantity/self.download_speed_3G
                upload_communication_time = data_quantity/self.upload_speed_3G
            elif mobile_network == "5G":
                download_communication_time = data_quantity/self.download_speed_5G
                upload_communication_time = data_quantity/self.upload_speed_5G
            else:
                download_communication_time = data_quantity/self.download_speed_4G
                upload_communication_time = data_quantity/self.upload_speed_4G
        else:
            if fix_network == "fiber":
                energy_consumption = data_quantity*self.fix_ADSL_1GO + self.fix_core_network_1GO
                upload_communication_time = data_quantity/self.upload_speed_fiber
                download_communication_time = data_quantity/self.download_speed_fiber
            else:
                energy_consumption = data_quantity*self.fix_ADSL_1GO + self.fix_core_network_1GO
                upload_communication_time = data_quantity/self.upload_speed_ADSL
                download_communication_time = data_quantity/self.download_speed_ADSL

        return [energy_consumption, upload_communication_time, download_communication_time]
