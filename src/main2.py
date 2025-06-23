from src.models.factory.DeviceFactory import DeviceFactory
from src.topologie.converter.parser_config import parse_cdp_neighbors, parse_config_to_json,read_config_file
from src.topologie.draw.PktBuilder import PktBuilder
import re
from src.models.Link import Link

# Étape 1 : Lire et parser les configurations
parsed_switch = parse_config_to_json("src/data/config/testt/switch_config.txt")
parsed_router = parse_config_to_json("src/data/config/testt/router_config.txt")


# Étape 2 : Créer les objets via la factory
s1 = DeviceFactory.create_device(parsed_switch["type"], parsed_switch["mac"], parsed_switch["name"], parsed_switch["raw"])
r1 = DeviceFactory.create_device(parsed_router["type"], parsed_router["mac"], parsed_router["name"], parsed_router["raw"])


# 1. Ajout des interfaces
for intf in parsed_switch["config"]["interfaces"].values():
    s1.add_interface(intf)
for intf in parsed_router["config"]["interfaces"].values():
    r1.add_interface(intf)

# Charger les templates XML
s1.load_switch()
r1.load_router()

# 2. Création des liens après que tous les mem_addr soient attribués


def is_vlan_subinterface(interface: str) -> bool:
    """
    Retourne True si l'interface est une sous-interface de type VLAN.
    Ex : GigabitEthernet0/1.10 → True ; FastEthernet0/0 → False
    """
    return bool(re.search(r'/\d+\.\d+$', interface))


# # Étape 3 : Injecter dans le fichier .pkt de base
builder = PktBuilder(base_template_path="src/resources/xml/empty.xml", devices=[s1,r1])
tree = builder.inject_devices()

# Étape 4 : Générer le fichier XML final
builder.generateXML(tree)

# Étape 5 : Générer le fichier .pkt
builder.generatePKT("src/resources/generated/generated1.xml")


print("✅ Fichier XML généré avec succès.")
