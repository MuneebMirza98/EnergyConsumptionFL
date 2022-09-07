import sys
import pandas as pd
import torch
import torch.nn as nn
import torchvision
import time
import logging
import os
from torchvision import transforms
from model.cifar10_CNN import ConvNet_cifar10
from model.FashionMNIST_CNN import FashionCNN
from model.MNIST_CNN import MNIST_CNN
from codecarbon import OfflineEmissionsTracker

logging.basicConfig(filename='local_experiment.log',
                    level=logging.INFO)


def Load_dataset_and_model(modelPATH, dataset):
    if dataset == "CIFAR-10":
        transform = transforms.Compose([transforms.ToTensor(),
                                        transforms.Normalize((0.5, 0.5, 0.5),
                                                             (0.5, 0.5, 0.5))
                                        ])

        train_dataset = torchvision.datasets.CIFAR10(root='./data',
                                                     train=True,
                                                     download=True,
                                                     transform=transform)

        test_dataset = torchvision.datasets.CIFAR10(root='./data',
                                                    train=False,
                                                    download=True,
                                                    transform=transform)

        # Load the model
        model = ConvNet_cifar10()
        model.load_state_dict(torch.load(modelPATH))
        model.eval()

        return model, train_dataset, test_dataset

    elif dataset == "FashionMNIST":
        transform = transforms.Compose([transforms.ToTensor(),
                                        transforms.Normalize((0.5,),
                                                             (0.5,), )
                                        ])

        train_dataset = torchvision.datasets.FashionMNIST(root='./data',
                                                          train=True,
                                                          download=True,
                                                          transform=transform)

        test_dataset = torchvision.datasets.FashionMNIST(root='./data',
                                                         train=False,
                                                         download=True,
                                                         transform=transform)

        # Load the model
        model = FashionCNN()
        model.load_state_dict(torch.load(modelPATH))
        model.eval()

        return model, train_dataset, test_dataset

    elif dataset == "MNIST":
        transform = transforms.Compose([transforms.ToTensor(),
                                        transforms.Normalize((0.5,),
                                                             (0.5,), )
                                        ])

        train_dataset = torchvision.datasets.MNIST(root='./data',
                                                   train=True,
                                                   download=True,
                                                   transform=transform)

        test_dataset = torchvision.datasets.MNIST(root='./data',
                                                  train=False,
                                                  download=True,
                                                  transform=transform)

        # Load the model
        model = MNIST_CNN()
        model.load_state_dict(torch.load(modelPATH))
        model.eval()

        return model, train_dataset, test_dataset


# Training and energy consumption measure
def Experiment(
        dataset,
        modelPATH,
        measurePowerSecs,
        batchSizes,
        nbrEpoch,
        learningRate,
        optimizer,
        loss,
        emission_output_directory,
        emission_output_file
):
    device = torch.device('cpu')
    logging.info(f'Num GPUs available: {torch.cuda.device_count()}')
    logging.info(f'Num CPUs available: {os.cpu_count()}')
    logging.info(f'Will use device {device}')

    model, trainDataset, testDataset = Load_dataset_and_model(modelPATH, dataset)
    model = model.to(device)

    trainLoader = torch.utils.data.DataLoader(trainDataset,
                                              batch_size=batchSizes,
                                              shuffle=True)

    testLoader = torch.utils.data.DataLoader(testDataset,
                                             batch_size=batchSizes,
                                             shuffle=False)

    if loss == "CrossEntropyLoss":
        criterion = nn.CrossEntropyLoss()

    if optimizer == "SGD":
        optimizer = torch.optim.SGD(model.parameters(), lr=learningRate)
    elif optimizer == "Adam":
        optimizer = torch.optim.Adam(model.parameters, lr=learningRate)

    nbrStepsTotal = len(trainLoader)

    tracker = OfflineEmissionsTracker(
        country_iso_code="FRA",
        measure_power_secs=measurePowerSecs,
        output_dir=emission_output_directory,
        output_file=emission_output_file
    )

    tracker.start()
    startTime = time.time()

    logging.info(f'Experiment for dataset {dataset}, with the model saved her "{modelPATH}"')
    logging.info(f'learning rate = {learningRate}')
    print(f'Experiment for dataset {dataset}, with the model saved her "{modelPATH}"')
    print(f'learning rate = {learningRate}')

    for epoch in range(nbrEpoch):
        logging.info(f'=================================== EPOCH {epoch + 1} =========================================')
        print(f'=================================== EPOCH {epoch + 1} =========================================')
        for i, (images, labels) in enumerate(trainLoader):

            images = images.to(device)
            labels = labels.to(device)

            # Forward pass
            outputs = model(images)
            loss = criterion(outputs, labels)

            # Backward and optimize
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            if (i + 1) % 1000 == 0:
                logging.info(f'Epoch [{epoch + 1}/{nbrEpoch}], Step [{i + 1}/{nbrStepsTotal}], Loss: {loss.item():.4f}')
                print(f'Epoch [{epoch + 1}/{nbrEpoch}], Step [{i + 1}/{nbrStepsTotal}], Loss: {loss.item():.4f}')

    # torch.save(model.state_dict(), './model/mnist_cnn_experiment.pth')

    endTime = time.time()
    emissions = tracker.stop()
    trainingCarbon = emissions
    trainingEnergy = tracker._total_energy.kWh
    trainingTime = endTime - startTime

    logging.info('===================================Training Finished ===============================================')
    logging.info(f'                     Training total time = {trainingTime}  seconds ')
    logging.info(f'                     Training Energy = {trainingEnergy}  kWh ')
    logging.info(f'                     Training Carbon Emissions = {trainingCarbon}  CO2eq')
    print('===================================Training Finished ===============================================')
    print(f'                     Training total time = {trainingTime}  seconds ')
    print(f'                     Training Energy = {trainingEnergy}  kWh ')
    print(f'                     Training Carbon Emissions = {trainingCarbon}  CO2eq')

    with torch.no_grad():
        nbrCorrect, nbrSamples = 0, 0
        for images, labels in testLoader:
            images = images.to(device)
            labels = labels.to(device)
            outputs = model(images)

            _, predicted = torch.max(outputs, 1)
            nbrSamples += labels.size(0)
            nbrCorrect += (predicted == labels).sum().item()

        acc = 100 * nbrCorrect / nbrSamples
        logging.info(f'                             Accuracy of the network : {acc}%                                  ')
        print(f'                             Accuracy of the network : {acc}%                                  ')

    code_carbon_file = emission_output_directory + "/" + emission_output_file

    output_dict = {
        "Dataset": dataset,
        "Batch Size": batchSizes,
        "Device": device,
        "Nbr Epoch": nbrEpoch,
        "Training Time": trainingTime,
        "Training Energy": trainingEnergy,
        "Training Carbon": trainingCarbon,
        "Accuracy": acc,
    }
    return output_dict, code_carbon_file


############################################# Execution de la fonction #################################################

if __name__ == "__main__":

    results, code_carbon_output_path = Experiment(dataset='MNIST',
                                                  measurePowerSecs=9999999,
                                                  batchSizes=10,
                                                  modelPATH='./model/mnist_cnn_experiment.pth',
                                                  nbrEpoch=100,
                                                  learningRate=0.001,
                                                  optimizer="SGD",
                                                  loss='CrossEntropyLoss',
                                                  emission_output_directory='./energy',
                                                  emission_output_file='emissions_mnist_cpu.csv'
                                                  )

    final_result_PATH = "./final_results_mnist_cpu.csv"

    df = pd.DataFrame.from_dict([results])
    code_carbon_results_df = pd.read_csv(code_carbon_output_path)
    df["CPU Energy"] = code_carbon_results_df["cpu_energy"][len(code_carbon_results_df.index) - 1]
    df["GPU Energy"] = code_carbon_results_df["gpu_energy"][len(code_carbon_results_df.index) - 1]
    df["RAM Energy"] = code_carbon_results_df["ram_energy"][len(code_carbon_results_df.index) - 1]

    if os.path.exists(final_result_PATH):
        df0 = pd.read_csv(final_result_PATH)
        df = pd.concat([df0, df], axis=0)

    df.to_csv(final_result_PATH, index=False, header=True)
