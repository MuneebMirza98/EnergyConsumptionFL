import pandas as pd


class Computation:
    """
    Determine the energy consumption of the total training of a federated learning algorithm
    """

    def __init__(self):  # FIXME arguments potentiels manquants à ajouter

        self.df_results = None

    def training_energy_consumption(self):
        """
        Méthode qui va calculer la consommation énergétique des entraînements et ainsi alimenter les CSV, pour les cas
        centralisés et fédérés # FIXME pour l'instant il n'y a que le cas centralisé
        """

        df_raw = pd.read_csv('/Tests/emissions/emissions.csv')
        # df_raw.head(-1)
        results = dict()

        interesting_columns = [
            'os',
            'python_version',
            'cpu_count',
            'cpu_model',
            'gpu_count',
            'gpu_model',
            'emissions',
        ]

        for keys in interesting_columns:
            results[keys] = df_raw[keys][0]

        # results['Model'] = model
        # results['Dataset'] = dataset
        results['Mean_training_duration'] = df_raw['duration'].mean()
        results['Mean_training_energy_consumption'] = df_raw['energy_consumed'].mean()
        results['Variance_training_energy_consumption'] = df_raw['energy_consumed'].var()
        df_dict = pd.DataFrame([results])

        if self.df_results is None:
            self.df_results = df_dict
            return
        self.df_results = pd.concat([self.df_results, df_dict])
        return

    def RequestCSV(self):
        """
        Méthode qui va aller requêter dans le CSV (ou la BDD) les informations de l'entraînement demandé

        :param CSV: CSV possédant les résultats des expériences réalisées
        :type CSV: CSV file
        :return: consommation énergétique exacte
        """

        pass
