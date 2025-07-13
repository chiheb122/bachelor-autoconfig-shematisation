# src/app.py
import json
from src.IA.llm.config_analyzer import ConfigAnalyzerAgent
from src.topologie.packet_tracer.TopologyLoader import TopologyLoader
from src.topologie.packet_tracer.TopologyBuilder import TopologyBuilder
from src.topologie.packet_tracer.TopologyExecutor import TopologyExecutor
from src.configs.save.save_configs_to_mongo import save_config_network,prepare_for_mongo
from src.IA.training.train_naive_bayes import ConfigClassifier
from src.IA.training.config_feature_parser import extract_features_from_configRaw

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
        # Modele local de regression logistique
        predictions = []
        evaluation = ConfigClassifier()
        for device in devices:
            # Extraire les features de la config
            features = extract_features_from_configRaw(device.config,True)
            # Prédire avec le modèle
            prediction = evaluation.predict(features)
            # Ajouter le nom de l'appareil
            predictions.append({
                "hostname": device.hostname,
                "prediction": prediction.get("prediction", "unknown"), 
            })
            # si il est mal configuré, on l'ajoute à l'instance
            if prediction.get("prediction") == "incomplete_config":
                device.notconfigured = True


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

        reponse_llm += TopologyGenerator.format_response(response)


        # Simuler que le routeur Rchiheb il est mal configuré
        # for device in devices:
        #     if device.hostname == "Rchiheb":
        #         device.notconfigured = True
        #         print(device)

        # Enregistrer les configs dans MongoDB
        # for device in parsed_devices:
        #     save_config_network(folder.split('/')[-1], prepare_for_mongo(device))

        # Exécuter la topologie
        TopologyExecutor.generate(devices, links, notes=reponse_llm)


    # Formatter la réponse pour l'afficher dans l'interface
    @staticmethod
    def format_response(response):
        formatted_response = ""
        showcase = [
            ("statut", "Statut de l'appareil", False),
            ("problemes", "Problèmes", True),
            ("recommandations", "Recommandations", True),
            ("commandes", "Commandes", True),
            ("networks", "Réseaux", True),
        ]
        for device in response:
            name = device.get("name", "Inconnu")
            formatted_response += f"\n\nAppareil : {name}\n"
            for key, label, is_list in showcase:
                value = device.get(key)
                if value:
                    formatted_response += f"{label} :\n"
                    if is_list and isinstance(value, list):
                        for item in value:
                            formatted_response += f"- {item}\n"
                    elif not is_list:
                        formatted_response += f"{value}\n"
        return formatted_response
