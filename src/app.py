# src/app.py
from src.topologie.packet_tracer.TopologyLoader import TopologyLoader
from src.topologie.packet_tracer.TopologyBuilder import TopologyBuilder
from src.topologie.packet_tracer.TopologyExecutor import TopologyExecutor


class TopologyGenerator:
    @staticmethod
    def run():
        # Tu peux ici demander dynamiquement à l'utilisateur le dossier :
        # folder = input("📁 Entrez le chemin du dossier de config : ").strip()
        folder = "/Users/chiba/Desktop/TB/configExtract/src/data/config/testt"
        parsed_devices, neighbors = TopologyLoader.load_config_from_folder(folder)
        devices = TopologyBuilder.create_devices(parsed_devices)
        links = TopologyBuilder.build_links(devices, neighbors)

        # Ajoute les liens à un builder si besoin
        TopologyExecutor.generate(devices,links)
