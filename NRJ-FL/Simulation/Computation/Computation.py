import pandas as pd


class Computation:
    """
    Determine the energy consumption of the total training of a federated learning algorithm
    """

    def __init__(self):  # FIXME arguments potentiels manquants à ajouter

        self.df_results = None

    def training_energy_consumption(self, config_list):
        """
        Calculate the energy consumption of training

        :param config_list: list with, name of dataset, size of dataset, size of model, batch_size, number of workers,
                            nbr of rounds, hardware, CPU_count and CPU freq

        :return: energy consumption of the training or print "not this information in my database, please make
                 experiment and feed it".
        """
        data_df = pd.read_csv('./computation_principal_base.csv')
        for i in data_df.index:
            if data_df['Dataset'][i] == config_list[0] and data_df['Batch Size'][i] == config_list[3] and data_df['CPU count'] == config_list[8] and data_df['CPU freq'] == config_list[9] and config_list[6] == 'CPU':
                return data_df['Training Energy'][i]
            # elif data_df['Dataset'][i] == config_list[0] and data_df['Batch Size'][i] == config_list[3] and
            # config_list[6] == 'GPU': print('not this information in my database, please make experiment and feed
            # it') return
            else:
                print('not this information in my database, please make experiment and feed it')
                return
