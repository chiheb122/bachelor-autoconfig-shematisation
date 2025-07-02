# src/topologie/topology_loader.py

import os
from src.topologie.converter.parser_config import parse_config_to_json

class TopologyLoader:
    @staticmethod
    def load_config_from_folder(folder_path):
        parsed_devices = []

        # Tous les fichiers se terminant par "_config.txt"
        for filename in os.listdir(folder_path):
            if filename.endswith("_config.txt"):
                full_path = os.path.join(folder_path, filename)
                parsed = parse_config_to_json(full_path)
                parsed_devices.append(parsed)

        # Rassembler tous les neighbors de chaque device
        neighbors = []
        for dev in parsed_devices:
            neighbors.extend(dev["config"].get("neighbors", []))

        return parsed_devices, neighbors
