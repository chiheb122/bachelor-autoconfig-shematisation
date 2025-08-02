# src/app.py
import json
import platform
from pathlib import Path
from src.IA.llm.config_analyzer import ConfigAnalyzerAgent
from src.topologie.TopologyLoader import TopologyLoader
from src.topologie.TopologyBuilder import TopologyBuilder
from src.topologie.TopologyExecutor import TopologyExecutor
from src.configs.save.save_configs_to_mongo import save_config_network,prepare_for_mongo
from src.IA.training.train_naive_bayes import ConfigClassifier
from src.IA.training.config_feature_parser import extract_features_from_configRaw
from src.configs.extract.pytermi import main
from colorama import Fore, init
from src.topologie.graphviz.draw_network import GraphvizRender

init(autoreset=True)

class TopologyGenerator:
    @staticmethod
    def run(packet_tracer=False):
        reponse_llm = "Résumé de l'analyse des configurations :\n\n"

        # Demander dynamiquement à l'utilisateur le dossier :
        folder = input("Entrez le chemin du dossier de configs : ").strip()
        folder = Path(folder).resolve()

        if not folder.exists():
            print("!! Le dossier spécifié n'existe pas.")
            return
        # folder = folder if folder else "/Users/chiba/Desktop/TB/configExtract/src/data/config/reseau12"
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
            prediction = evaluation.predict(features, plot=False)
            # Ajouter le nom de l'appareil
            predictions.append({
                "hostname": device.hostname,
                "prediction": prediction.get("prediction", "unknown"), 
            })
            # si il est mal configuré, on l'ajoute à l'instance
            if prediction.get("prediction") == "incomplete_config":
                device.notconfigured = True

        # Appeler l'agent expert du modèle LLM avec les prédictions faites en local
        # agent = ConfigAnalyzerAgent()
        # configs = agent.returnConfigs(parsed_devices)
        # response = agent.analyze_configs(configs, predictions)
        # # Afficher le résultat de l'analyse
        # print("\n Résultat de l'analyse expert réseau:\n")
        # print(response)

        # lire le rapport txt
        fichier = "src/IA/llm/rapport.txt"
        response = ""
        with open(fichier, "r", encoding="utf-8") as f:
            texte_complet = f.read()
            result_json = json.loads(texte_complet)
            response = result_json
            f.close()

        reponse_llm += TopologyGenerator.format_response(response)


        # Enregistrer les configs dans MongoDB
        # for device in parsed_devices:
        #     save_config_network(folder.split('/')[-1], prepare_for_mongo(device))

        # Exécuter la topologie
        nom_folder = folder.name
        output_file = f"{nom_folder}"
        if packet_tracer:
            TopologyGenerator.packet_tracer(devices, links, reponse_llm, output_path=folder, output_file=output_file)
        else:
            TopologyGenerator.graphviz(devices, links, output_file=output_file, output_path=folder, responsellm=response)




    @staticmethod
    def packet_tracer(devices, links, reponse_IA, output_path=".", output_file="topologie_packet_tracer"):
        # Logique pour générer la topologie avec Packet Tracer
        TopologyExecutor.generate(devices, links, notes=reponse_IA, output_path=output_path, output_file=output_file)

    @staticmethod
    def graphviz(devices, links, output_file="topologie_graphviz", output_path=".", responsellm=None):
        # Logique pour générer la topologie avec Graphviz
        drawnetwork = GraphvizRender(devices, links, output_file=output_file, output_path=output_path, responsellm=responsellm)
        drawnetwork.draw_network()
        # Générer le rapport HTML
        drawnetwork.generate_html_report()

    # Formatter la réponse pour l'afficher dans l'interface
    @staticmethod
    def format_response(response):
        # Nettoyer les balises Markdown éventuelles
        if isinstance(response, str):
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            response = json.loads(response)
        
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

def main_menu():
    is_windows = platform.system() == "Windows"
    
    while True:
        # Préparer le texte pour l'option Packet Tracer
        packet_tracer_option = f"{Fore.LIGHTBLACK_EX}2. Générer la topologie Packet Tracer (non disponible sur Windows)" if is_windows else f"{Fore.BLUE}2. Générer la topologie Packet Tracer"
        
        menu = f"""
\033[1m\033[94m
===============================================================
             Haute École de Gestion de Genève (HEG)
       Travail de Bachelor – Année académique 2024-2025
===============================================================

Projet : Schématisation visuelle des configurations réseau  
         et détection intelligente des erreurs par l'IA

Auteur : Chiheb BIDANI (@chiheb122)

\033[91m\nNotice : Assurez-vous que les fichiers de config se terminent par _config.txt et les neighbors avec _neighbors.txt\033[0m

\n{Fore.BLUE}Menu principal :\n{Fore.BLUE}
1. Extraire les configurations\n{packet_tracer_option}\n{Fore.BLUE}3. Générer la topologie Graphviz\n{Fore.BLUE}0. Quitter\n"""
        
        print(menu)
        
        choix = input("Votre choix : ").strip()
        if choix == "1":
            # Extraction configs (à adapter selon ta logique)
            try:
                response = input("Avez-vous des configurations à extraire ? (oui/non)")
                while response.lower() == "oui":
                    main()  # Relance l'extraction de configuration si l'utilisateur le souhaite
                    response = input("Avez-vous d'autres configurations à extraire ? (oui/non)")
                    # Si l'utilisateur ne souhaite pas extraire d'autres configurations, on termine le programme
                    print("Extraction de la configuration terminée.")
            except Exception as e:
                print(f"Une erreur s'est produite lors de l'extraction de la configuration : {e}")
                # Après l'extraction, génère la 
                print("Pour générer la topologie, veuillez choisir l'option 2 ou 3 au menu principal.")
                main_menu()

        elif choix == "2":
            if is_windows:
                print(f"{Fore.RED} Cette option n'est pas disponible sur Windows.")
                print(f"{Fore.YELLOW} Utilisez l'option 3 (Graphviz) comme alternative.")
            else:
                print("Génération de la topologie Packet Tracer...")
                TopologyGenerator.run(packet_tracer=True)
                break  # Sortir de la boucle après la génération
        elif choix == "3":
            print("Génération de la topologie Graphviz...")
            TopologyGenerator.run(packet_tracer=False)
        elif choix == "0":
            print("Au revoir !")
            break
        else:
            print("Choix invalide.")

if __name__ == "__main__":
    main_menu()
