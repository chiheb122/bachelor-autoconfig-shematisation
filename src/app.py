# src/app.py
from src.topologie.packet_tracer.TopologyLoader import TopologyLoader
from src.topologie.packet_tracer.TopologyBuilder import TopologyBuilder
from src.topologie.packet_tracer.TopologyExecutor import TopologyExecutor
from src.config.save.save_configs_to_mongo import save_config_network,prepare_for_mongo


class TopologyGenerator:
    @staticmethod
    def run():
        # Demander dynamiquement à l'utilisateur le dossier :
        folder = input("Entrez le chemin du dossier de config : ").strip()
        parsed_devices, neighbors = TopologyLoader.load_config_from_folder(folder)
        devices = TopologyBuilder.create_devices(parsed_devices)
        links = TopologyBuilder.build_links(devices, neighbors)
        # Enregistrer les configs dans MongoDB
        for device in parsed_devices:
            save_config_network(folder.split('/')[-1], prepare_for_mongo(device))

        # Exécuter la topologie
        TopologyExecutor.generate(devices, links)
