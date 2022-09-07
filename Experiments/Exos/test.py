from codecarbon import OfflineEmissionsTracker
import logging
import math

logging.basicConfig(filename='emissions.log',
                    level=logging.INFO)


a = 5
b = 20
energy_list = []
carbon_list = []


for i in range(500):
    tracker = OfflineEmissionsTracker(country_iso_code="FRA")

    tracker.start()
    c = a
    emissions = tracker.stop()
    energy = tracker._total_energy.kWh

    energy_list.append(energy)
    carbon_list.append(emissions)

mean_energy = sum(energy_list)/100

print("=======================================================")
print("\n")
print(energy_list)
print("\n")
print(len(energy_list))
print("\n")
print("=======================================================")
print("\n")
print(carbon_list)
print("\n")
print(len(carbon_list))
print("\n")
print(f"l'énergie moyenne par assignement est de {mean_energy} kWh")
logging.info(f"l'énergie moyenne par assignement est de {mean_energy} kWh")





