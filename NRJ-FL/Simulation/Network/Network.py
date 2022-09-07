import math
from ..States.States import *


class Network:
    """
    Classe mère de tous les Networks possible (accès cellulaire, accès fixe et coeur). Cette classe créé le double
    numérique du réseau, et fixe les valeurs de consommation énergétique par Go qui seront utilisées par la suite par
    Env pour qu'il puisse réaliser tous ses calculs.
    """

    def __init__(self, **kwarg):
        """
        Attributs de Network. Il y a les kwargs qui peuvent être des paramètres d'entrée et les attributs à valeur None
        au début qui prendront leurs valeurs après avoir été affecté par les méthodes de la classe.

        :param kwarg: - Les modes de connexion des devices, si c'est par 2G/3G/4G/5G, les différentes vitesses d'upload
                        et de download.
                      - Le chemin de stockage du fichier CSV contenant les résultats.
        """
        self.network_path = kwarg.get(
            'network_path',
            '/home/osboxes/PycharmProjects/clustered-fl/SimEnv/Simulation/Network/network_output.csv'
        )

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

    def create_simulated_network(self, state):
        """
        Méthode qui va créer le double numérique de l'architecture réseau physique existante sur la plateforme FL
        physique.

        :param state: instance de la classe States

        :return:  Dataframe avec un CSV avec toutes les informations des liaisons réseau entre tous les devices et le
                  serveur central en fonction de la distance entre ce
        """
        if os.path.exists(self.network_path):
            self.network_infos_df = pd.read_csv(self.network_path)
            return

        distance_list = []

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

        return

    def network_request(self, guid, timestamp):
        """
        Fonction qui va permettre de récupérer les informations sur le réseau qui se trouvent dans le csv retourné par
        la méthode create_simulated_network() sur le guid demandé et au moment du timestamp demandé

        :param guid: le guid de l'appareil qui nous intéresse
        :param timestamp: le timestamp qui nous intéresse

        :return: - les informations sur le réseau, la disponibilité... du device demandé, au timestamp voulu
        """
        with open(self.network_path, 'r', encoding='utf-8') as f:
            df = pd.read_csv(f)
            self.network_df_reduced = df.loc[(df['Timestamp'] == str(timestamp)) & (df['Guid'] == guid)].iloc[0]
        return

    def network_energy_consumption(self, data_quantity, **kwargs):
        """
        Fonction qui va calculer les valeurs de consommation énergétique des communications entre le device sélectionné
        et le serveur centrale
        :param data_quantity: quantité de donnée (en bits ou en octets à transférer)
        :param kwargs: les différents mode de connexion pour le mobile et le fix

        :return: la quantité d'énergie consommée par la communication demandée
        """
        # TODO penser à ajouter la dépendance avec la distance par la suite
        # FIXME pour l'instant, quand le network a pour valeur "fix" on considère qu'on est en fibre, et quand on est
        # en mobile, on considère qu'on est en 4G.

        data_quantity_unit = kwargs.get('data_quantity_unit', 'bit')
        if data_quantity_unit == "octet":
            data_quantity = data_quantity / 8

        fix_network = kwargs.get('fix_network', 'fiber')
        mobile_network = kwargs.get('mobile_network', '4G')

        if self.network_df_reduced['Network'] == "mobile":
            energy_consumption = data_quantity*(self.mobile_1GO+self.mobile_core_network_1GO)
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

        return energy_consumption, upload_communication_time, download_communication_time
