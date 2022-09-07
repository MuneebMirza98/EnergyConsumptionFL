import json
from datetime import datetime
import pandas as pd
import os
import random
from .Timer import Timer


class States:
    """
    Créé le double numérique des devices, dans les états (charge, vérouillage, modèle du device, puissance du device...)
    et donne les informations sur les devices demandées à Env.
    """

    def __init__(self, **kwarg):

        self.server_position_x = kwarg.get('server_position_x', -5)  # Mbps
        self.server_position_y = kwarg.get('server_position_y', 10)  # Mbps
        self.output_path = kwarg.get(
            'output_path',
            '/home/osboxes/PycharmProjects/clustered-fl/SimEnv/Simulation/States/states_output.csv'
        )

        self.guid_list = None
        self.timestamp_df = None
        self.position_list_x = None
        self.position_list_y = None

        self.perma_states_df = self.create_states_CSV()
        self.df_reduced = None

    def create_states_CSV(self):
        """
        Méthode qui créé un CSV contenant tous les états de 1000 devices sur 4 jours, en utilisant des données raw
        issues d'un fichier JSON

        :return: un CSV avec toutes les informations sur les états des devices ainsi que le dataframe correspondant
        """

        if os.path.exists(self.output_path):
            perma_states_df = pd.read_csv(self.output_path)
            self.guid_list = perma_states_df['Guid']
            self.position_list_x = perma_states_df['Position_X']
            self.position_list_y = perma_states_df['Position_Y']
            self.timestamp_df = perma_states_df['Timestamp']
            return perma_states_df

        perma_states_df = pd.DataFrame()
        success_list = []
        guid_list = []
        model_list = []
        timestamp_list = []
        message_list = []
        network_list = []
        charging_list = []
        available_list = []
        position_list_x = []
        position_list_y = []

        PATH = '/home/osboxes/PycharmProjects/SimEnv/Simulation/States/state_traces.json'
        with open(PATH, 'r', encoding='utf-8') as f:
            d = json.load(f)

        for i in list(d.keys()):

            uid = list(d.keys())[int(i)]
            timer = Timer(ubt=d[str(uid)], google=True)
            message = timer.ubt['messages'].split("\n")
            current_network_state = "mobile"
            current_charging_state = "Not in charge"
            current_device_position_x = random.randint(0, 100)  # FIXME ce sera à rajouter pour compléter les positions
            current_device_position_y = random.randint(0, 100)
            reference_timestamp = datetime.strptime(message[0].strip().split("\t")[0].strip(), '%Y-%m-%d %H:%M:%S')

            for mes in message:

                current_timestamp = datetime.strptime(mes.strip().split("\t")[0].strip(), '%Y-%m-%d %H:%M:%S')
                relatif_timestamp = current_timestamp - reference_timestamp
                timestamp_list.append(relatif_timestamp)

                message_str = mes.strip().split("\t")[1].strip()

                if message_str == "wifi":
                    current_network_state = "fix"
                elif message_str == "4G" or message_str == "3G" or message_str == "2G":
                    current_network_state = "mobile"
                elif message_str == "0.0%":
                    current_network_state = "disconnected"
                network_list.append(current_network_state)

                if message_str == "battery_charged_on":
                    current_charging_state = "In charge"
                elif message_str == "battery_charged_off":
                    current_charging_state = "Not in charge"
                charging_list.append(current_charging_state)

                if current_network_state == "fix" and current_charging_state == "In charge":
                    available_list.append('Available')
                else:
                    available_list.append('Not available')

                success_list.append(timer.isSuccess)
                guid_list.append(timer.guid)
                model_list.append(timer.model)
                message_list.append(message_str)
                position_list_x.append(current_device_position_x)
                position_list_y.append(current_device_position_y)

        perma_states_df['Guid'] = guid_list
        perma_states_df['Model'] = model_list
        perma_states_df['Success'] = success_list
        perma_states_df['Timestamp'] = timestamp_list
        perma_states_df['Message'] = message_list
        perma_states_df['Network'] = network_list
        perma_states_df['Charging'] = charging_list
        perma_states_df['Position_X'] = position_list_x
        perma_states_df['Position_Y'] = position_list_y
        perma_states_df['Availability'] = available_list

        self.guid_list = guid_list
        self.position_list_x = position_list_x
        self.position_list_y = position_list_y
        self.timestamp_df = perma_states_df['Timestamp']

        perma_states_df.to_csv(self.output_path, index=False)

        return perma_states_df

    def state_request(self, guid, timestamp):
        """
        Fonction qui va permettre de récupérer l'état du device qui se trouvent dans le csv retourné par la méthode
        create_state_CSV() à partir de son guid et du timestamp voulu.

        :param guid: le guid de l'appareil qui nous intéresse
        :param timestamp: le timestamp qui nous intéresse

        :return: - les informations sur le réseau, la disponibilité... du device demandé, au timestamp voulu
        """
        with open(self.output_path, 'r', encoding='utf-8') as f:
            df = pd.read_csv(f)
            self.df_reduced = df.loc[(df['Timestamp'] == str(timestamp)) & (df['Guid'] == guid)].iloc[0]
        return

    def simulated_state(self, **kwargs):
        """
        Fonction qui va permettre d'ajouter les états simulés des devices qui auront été sélectionnés pour les
        différents rounds d'expériences d'apprentissage fédéré.

        :param kwargs:

        :return:
        """
