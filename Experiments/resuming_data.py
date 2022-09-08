import pandas as pd
import matplotlib.pyplot as plt
from MNIST_CNN import MNIST_CNN
from FashionMNIST_CNN import FashionCNN
import numpy as np

########################## Centralised case : Generation of resume_result_centralized.csv ##############################
############################# Method based on the output of the pytorch Kubernetes pod #################################


# mean_list = ['Training Time',
#              'Training Energy',
#              'Training Carbon',
#              'Accuracy',
#              'CPU Energy',
#              'GPU Energy',
#              'RAM Energy']
#
# csv_list = ['final_results_cifar10.csv',
#             'final_results_fashion_mnist.csv',
#             'final_results_fashion_mnist_cpu.csv',
#             'final_results_mnist.csv',
#             'final_results_mnist_cpu.csv']
#
# batch_size_list = [10, 32, 64, 128]
#
# df_final = pd.DataFrame()
#
# for csv in csv_list:
#     path = f"./Centralized/raw_results/{csv}"
#     df = pd.read_csv(path)
#     for batch_size in batch_size_list:
#         df_reduced = df.loc[(df['Batch Size'] == batch_size)]
#         for column in mean_list:
#             df_reduced[column] = df_reduced[column].mean()
#         df_final = pd.concat([df_final, df_reduced.head(1)], ignore_index=True, axis=0)
#
# df_final.to_csv('./Centralized/resume_result_centralized.csv', index=False, header=True)


########################## Federated case : Generation of computation_principal_base.csv ################################
################################### Method based on output of the FL platform ########################################


# df_fl_concat = pd.DataFrame()
# duration = 0
# for rounds in range(10):
#     df_temp = pd.read_csv(f'./Federated/experiment-1/nrj-{rounds+1}/worker.csv')
#     df_fl_concat = pd.concat([df_fl_concat, df_temp], ignore_index=True, axis=0)
#     for worker in range(10):
#         df_cc = pd.read_csv(f'./Federated/experiment-1/nrj-{rounds+1}/worker-{worker+1}.csv')
#         duration += df_cc['duration'][0]
# df_fl_concat['Training Time'] = duration
#
# print(df_fl_concat)
#
# df_final_fl = df_fl_concat
# df_final_fl['Training Energy'] = df_final_fl['Training Energy'].sum()
# df_final_fl['Training Carbon'] = df_final_fl['Training Carbon'].sum()
# print(df_final_fl)


############################################ PLOTTING PART ############################################################
##################################### energy_consumption(batch size) Centralized ######################################


# df_final = pd.read_csv('Centralized/resume_result_centralized.csv')
# df_for_plot = df_final.loc[(df_final['Device'] == 'cuda')]
# print(df_for_plot)
#
# df_mnist = df_for_plot.loc[(df_final['Dataset'] == 'MNIST')]
# print(df_mnist)
# df_cifar = df_for_plot.loc[(df_final['Dataset'] == 'CIFAR-10')]
# print(df_cifar)
# df_fashion = df_for_plot.loc[(df_final['Dataset'] == 'FashionMNIST')]
# df_fashion.drop([4, 5, 6, 7], inplace=True)
# print(df_fashion)
#
# plt.figure()
# plt.subplot(111)
# plt.plot(
#     df_mnist['Batch Size'],
#     df_mnist['Training Energy'],
#     'k',
#     label='MNIST'
# )
# plt.plot(
#     df_cifar['Batch Size'],
#     df_cifar['Training Energy'],
#     'b',
#     label='CIFAR-10'
# )
# plt.plot(
#     df_fashion['Batch Size'],
#     df_fashion['Training Energy'],
#     'r',
#     label='FashionMNIST'
# )
# plt.plot(
#     df_mnist['Batch Size'],
#     df_mnist['Training Energy'],
#     'ko'
# )
# plt.plot(
#     df_cifar['Batch Size'],
#     df_cifar['Training Energy'],
#     'bo'
# )
# plt.plot(
#     df_fashion['Batch Size'],
#     df_fashion['Training Energy'],
#     'ro'
# )
#
# plt.xlabel('Batch Size', fontweight='bold')
# plt.ylabel('Training energy (kWh)', fontweight='bold')
# plt.title('Training energy comparaison of batch sizes', fontweight='bold')
# plt.legend()
# plt.grid()
#
# plt.show()


################## CPU VS GPU energy consumption for MNIST and FashionMNIST Centralized case ##########################
############################### Method based on output of pytorch kubernetes pod ######################################


# df_final = pd.read_csv('Centralized/resume_result_centralized.csv')
# df_mnist_cuda = df_final.loc[(df_final['Dataset'] == 'MNIST') & (df_final['Device'] == "cuda")]
# print(df_mnist_cuda)
# df_mnist_cpu = df_final.loc[(df_final['Dataset'] == 'MNIST') & (df_final['Device'] == "cpu")]
# print(df_mnist_cpu)
# df_fashion_mnist_cuda = df_final.loc[(df_final['Dataset'] == 'FashionMNIST') & (df_final['Device'] == "cuda")]
# print(df_fashion_mnist_cuda)
# df_fashion_mnist_cpu = df_final.loc[(df_final['Dataset'] == 'FashionMNIST') & (df_final['Device'] == "cpu")]
# print(df_fashion_mnist_cpu)
#
# plt.figure()
# plt.subplot(111)
# plt.plot(
#     df_mnist_cpu['Batch Size'],
#     df_mnist_cpu['Training Energy'],
#     'r',
#     label='MNIST CPU'
# )
# plt.plot(
#     df_mnist_cuda['Batch Size'],
#     df_mnist_cuda['Training Energy'],
#     'r',
#     label='MNIST GPU',
#     linewidth=4
# )
# plt.plot(
#     df_mnist_cpu['Batch Size'],
#     df_mnist_cpu['Training Energy'],
#     'ro'
# )
# plt.plot(
#     df_mnist_cuda['Batch Size'],
#     df_mnist_cuda['Training Energy'],
#     'ro'
# )
# plt.plot(
#     df_fashion_mnist_cpu['Batch Size'],
#     df_fashion_mnist_cpu['Training Energy'],
#     'b',
#     label='FashionMNIST CPU'
# )
# plt.plot(
#     df_fashion_mnist_cuda['Batch Size'],
#     df_fashion_mnist_cuda['Training Energy'],
#     'b',
#     label='FashionMNIST GPU',
#     linewidth=4
# )
# plt.plot(
#     df_fashion_mnist_cpu['Batch Size'],
#     df_fashion_mnist_cpu['Training Energy'],
#     'bo'
# )
# plt.plot(
#     df_fashion_mnist_cuda['Batch Size'],
#     df_fashion_mnist_cuda['Training Energy'],
#     'bo'
# )
#
# plt.xlabel('Batch Size', fontweight='bold')
# plt.ylabel('Training energy (kWh)', fontweight='bold')
# plt.title('Training energy comparaison between CPU & GPU', fontweight='bold')
# plt.legend()
# plt.grid()
#
# plt.show()


############################## Compare energy consumption between fl and centralized ###################################


df_c = pd.read_csv('./Centralized/results_centralized/resume_result_centralized.csv')
df_mnist_cuda = df_c.loc[(df_c['Dataset'] == 'FashionMNIST') & (df_c['Device'] == "cuda")]
uploading_dataset_consumption = (0.011 * 9.5)/1000  # MNIST size in Go x 1Go communication cost in fiber
df_mnist_cuda['Training Energy'] = df_mnist_cuda['Training Energy']*30 + uploading_dataset_consumption
print(df_mnist_cuda[['Training Energy', 'Batch Size']])

df_mnist_cpu = df_c.loc[(df_c['Dataset'] == 'FashionMNIST') & (df_c['Device'] == "cpu")]
uploading_dataset_consumption = (0.011 * 9.5)/1000  # MNIST size in Go x 1Go communication cost in fiber
df_mnist_cpu['Training Energy'] = df_mnist_cpu['Training Energy']*30 + uploading_dataset_consumption
print(df_mnist_cpu[['Training Energy', 'Batch Size']])


model = MNIST_CNN()
mods = list(model.modules())
for i in range(1, len(mods)):
    m = mods[i]
    p = list(m.parameters())
    sizes = []
    for j in range(len(p)):
        sizes.append(np.array(p[j].size()))

total_bits = 0
for i in range(len(sizes)):
    s = sizes[i]
    bits = np.prod(np.array(s))*32
    total_bits += bits
print(f'HEEEEEEEEEERRRRRRRRRREEEEEEEEEEEEEEEE : {total_bits}')

communication_energy = (19*0.000063*495)/1000
df_final_fl = pd.read_csv('./Federated/resume_result_federated.csv')
df_mnist_fl = df_final_fl.loc[(df_final_fl['Dataset'] == 'FashionMNIST')]
df_mnist_fl['Training Energy'] = df_mnist_fl['Training Energy'] + communication_energy
print(df_mnist_fl[['Training Energy', 'Batch Size']])

plt.figure()
plt.subplot(111)

plt.plot(
    df_mnist_fl['Batch Size'],
    df_mnist_fl['Training Energy'],
    'r',
    label='FashionMNIST FL'
)
plt.plot(
    df_mnist_fl['Batch Size'],
    df_mnist_fl['Training Energy'],
    'ro'
)

plt.plot(
    df_mnist_cuda['Batch Size'],
    df_mnist_cuda['Training Energy'],
    'b',
    label='FashionMNIST GPU Centralized'
)
plt.plot(
    df_mnist_cuda['Batch Size'],
    df_mnist_cuda['Training Energy'],
    'bo'
)

plt.plot(
    df_mnist_cpu['Batch Size'],
    df_mnist_cpu['Training Energy'],
    'k',
    label='FashionMNIST CPU centralized'
)
plt.plot(
    df_mnist_cpu['Batch Size'],
    df_mnist_cpu['Training Energy'],
    'ko',
)

plt.xlabel('Batch Size', fontweight='bold')
plt.ylabel('Training energy (kWh)', fontweight='bold')
plt.title('Training energy comparaison between FL and centralized (with CPU & GPU) with FashionMNIST dataset', fontweight='bold')
plt.legend()
plt.grid()

plt.show()
