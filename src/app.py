# src/app.py
import json
from src.IA.llm.config_analyzer import ConfigAnalyzerAgent
from src.topologie.packet_tracer.TopologyLoader import TopologyLoader
from src.topologie.packet_tracer.TopologyBuilder import TopologyBuilder
from src.topologie.packet_tracer.TopologyExecutor import TopologyExecutor
from src.config.save.save_configs_to_mongo import save_config_network,prepare_for_mongo


class TopologyGenerator:
    @staticmethod
    def run():
        # Demander dynamiquement à l'utilisateur le dossier :
        folder = input("Entrez le chemin du dossier de config : ").strip()
        folder = folder if folder else "/Users/chiba/Desktop/TB/configExtract/src/data/config/reseau12"
        parsed_devices, neighbors = TopologyLoader.load_config_from_folder(folder)
        # # Appeler l'agent expert
        agent = ConfigAnalyzerAgent()
        response = agent.analyze_configs(parsed_devices)
        # Afficher le résultat de l'analyse
        print("\n Résultat de l'analyse expert réseau:\n")
        print(response)
        # response = "### Anomalies détectées : #### Router Rchiheb **Interface GigabitEthernet0/0 (box internet) :**"


        # devices = TopologyBuilder.create_devices(parsed_devices)
        # Simuler que le routeur Rchiheb il est mal configuré
        # for device in devices:
        #     if device.hostname == "Rchiheb":
        #         device.notconfigured = True
        #         print(device)
        # links = TopologyBuilder.build_links(devices, neighbors)
        # Enregistrer les configs dans MongoDB
        # for device in parsed_devices:
        #     save_config_network(folder.split('/')[-1], prepare_for_mongo(device))

        # Exécuter la topologie
        # TopologyExecutor.generate(devices, links, notes=response)
