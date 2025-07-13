# src/app.py
import json
from src.IA.llm.config_analyzer import ConfigAnalyzerAgent
from src.topologie.packet_tracer.TopologyLoader import TopologyLoader
from src.topologie.packet_tracer.TopologyBuilder import TopologyBuilder
from src.topologie.packet_tracer.TopologyExecutor import TopologyExecutor
from src.configs.save.save_configs_to_mongo import save_config_network,prepare_for_mongo


class TopologyGenerator:
    @staticmethod
    def run():
        reponse_llm = "Résumé de l'analyse des configurations :\n\n"

        # Demander dynamiquement à l'utilisateur le dossier :
        folder = input("Entrez le chemin du dossier de configs : ").strip()
        folder = folder if folder else "/Users/chiba/Desktop/TB/configExtract/src/data/config/reseau12"
        parsed_devices, neighbors = TopologyLoader.load_config_from_folder(folder)
        devices = TopologyBuilder.create_devices(parsed_devices)
        links = TopologyBuilder.build_links(devices, neighbors)

        
        # # Appeler l'agent expert
        #agent = ConfigAnalyzerAgent()
        #configs = agent.returnConfigs(parsed_devices)
        #response = agent.analyze_configs(configs)
        # Afficher le résultat de l'analyse
        #print("\n Résultat de l'analyse expert réseau:\n")
        #print

        # lire le rapport txt
        fichier = "/Users/chiba/Desktop/TB/configExtract/src/IA/llm/rapport.txt"
        response = ""
        with open(fichier, "r", encoding="utf-8") as f:
            texte_complet = f.read()
            result_json = json.loads(texte_complet)
            response = result_json
            f.close()

        # Supposons que response est déjà une liste d'objets (après json.loads)
        for device in response:
            name = device.get("name", "Inconnu")
            problemes = device.get("problemes", [])
            recommandations = device.get("recommandations", [])
            commandes = device.get("commandes", [])
            reponse_llm += f"\n\n L'appareil {name} présente les problèmes suivants :"

            if problemes:
                reponse_llm += "\n  - Erreurs :"
                for p in problemes:
                    reponse_llm += f"\n    • {p}"
            if recommandations:
                reponse_llm += "\n  - Recommandations :"
                for r in recommandations:
                    reponse_llm += f"\n    • {r}"
            if commandes:
                reponse_llm += "\n  - Commandes correctives :"
                for c in commandes:
                    reponse_llm += f"\n    • {c}"




        # Simuler que le routeur Rchiheb il est mal configuré
        # for device in devices:
        #     if device.hostname == "Rchiheb":
        #         device.notconfigured = True
        #         print(device)

        # Enregistrer les configs dans MongoDB
        for device in parsed_devices:
            save_config_network(folder.split('/')[-1], prepare_for_mongo(device))

        # Exécuter la topologie
        TopologyExecutor.generate(devices, links, notes=reponse_llm)
