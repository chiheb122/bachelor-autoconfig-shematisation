# src/app.py
from src.topologie.packet_tracer.TopologyLoader import TopologyLoader
from src.topologie.packet_tracer.TopologyBuilder import TopologyBuilder
from src.topologie.packet_tracer.TopologyExecutor import TopologyExecutor


class TopologyGenerator:
    @staticmethod
    def run():
        # Demander dynamiquement à l'utilisateur le dossier :
        folder = input("Entrez le chemin du dossier de config : ").strip()
        parsed_devices, neighbors = TopologyLoader.load_config_from_folder(folder)
        devices = TopologyBuilder.create_devices(parsed_devices)
        links = TopologyBuilder.build_links(devices, neighbors)

        # Exécuter la topologie
        TopologyExecutor.generate(devices,links)
