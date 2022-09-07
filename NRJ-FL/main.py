import pandas as pd
from Simulation.States import States
from Simulation.Network import Network
import time

pd.options.display.max_rows = False
pd.options.display.max_columns = False

start_time_1 = time.time()
states_object = States()
print("\n")
print(states_object.perma_states_df.head())
print("\n")
states_object.state_request(0, "0 days 00:00:00")
print(states_object.df_reduced.head())
print("\n")

# net = Network()
# net.create_simulated_network(states_object)
# print(net.network_infos_df.head())
# print("\n")
#
# stop_time_1 = time.time()
# print(stop_time_1 - start_time_1)
# print("\n")
#
# print("===============================================================================================================")
#
# start_time_2 = time.time()
# print("\n")
# print(states_object.perma_states_df.head())
# print("\n")
# print(net.network_infos_df.head())
# print("\n")
# stop_time_2 = time.time()
# print(stop_time_2 - start_time_2)
# print("\n")
# net.network_request(0, "0 days 00:00:00")
# print(net.network_df_reduced.head())
