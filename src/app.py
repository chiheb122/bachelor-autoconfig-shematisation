# src/app.py
import json
from src.IA.llm.config_analyzer import ConfigAnalyzerAgent
from src.topologie.packet_tracer.TopologyLoader import TopologyLoader
#from src.topologie.packet_tracer.TopologyBuilder import TopologyBuilder
from src.topologie.packet_tracer.TopologyExecutor import TopologyExecutor
from src.config.save.save_configs_to_mongo import save_config_network,prepare_for_mongo


class TopologyGenerator:
    @staticmethod
    def run():
        # Demander dynamiquement à l'utilisateur le dossier :
        folder = input("Entrez le chemin du dossier de configs : ").strip()
        folder = folder if folder else "D:/HEG/sem6/TB/Tb_code/bachelor-autoconfig-shematisation/src/data/configs/packet"
        parsed_devices, neighbors = TopologyLoader.load_config_from_folder(folder)
        # # Appeler l'agent expert
        #agent = ConfigAnalyzerAgent()
        #configs = agent.returnConfigs(parsed_devices)
        #response = agent.analyze_configs(configs)
        # Afficher le résultat de l'analyse
        #print("\n Résultat de l'analyse expert réseau:\n")
        #print

        # lire le rapport txt
        fichier = "D:/HEG/sem6/TB/Tb_code/bachelor-autoconfig-shematisation/src/IA/llm/rapport.txt"
        response = ""
        with open(fichier, "r", encoding="utf-8") as f:
            texte_complet = f.read()
            result_json = json.loads(texte_complet)
            print(result_json)
            response = result_json
            print(response)
            f.close()





        #devices = TopologyBuilder.create_devices(parsed_devices)
        # Simuler que le routeur Rchiheb il est mal configuré
        #for device in devices:
        #     if device.hostname == "Rchiheb":
        #         device.notconfigured = True
        #         print(device)
        #links = TopologyBuilder.build_links(devices, neighbors)
        # Enregistrer les configs dans MongoDB
         #for device in parsed_devices:
         #    save_config_network(folder.split('/')[-1], prepare_for_mongo(device))

        # Exécuter la topologie
        #TopologyExecutor.generate(devices, links, notes=response)
