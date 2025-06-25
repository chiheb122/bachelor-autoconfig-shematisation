from src.models.factory.DeviceFactory import DeviceFactory
from src.topologie.converter.parser_config import parse_cdp_neighbors, parse_config_to_json
from src.topologie.packet_tracer.draw.PktBuilder import PktBuilder
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

all_neighbors = []
all_neighbors.extend(parse_cdp_neighbors("src/data/config/testt/router_neighbors.txt"))
all_neighbors.extend(parse_cdp_neighbors("src/data/config/testt/switch_neighbors.txt"))

# Dictionnaire des objets Device
devices_by_hostname = {
    r1.hostname: r1,
    s1.hostname: s1,
    # Ajouter d’autres appareils ici si besoin
}

seen = set()
links = []

for entry in all_neighbors:
    local_host = entry["device_id"]
    local_intf = entry["local_interface"]
    remote_intf = entry["port_id"]

    # Ignorer les sous-interfaces
    if is_vlan_subinterface(local_intf) or is_vlan_subinterface(remote_intf):
        continue

    dev_a = devices_by_hostname.get(local_host)
    dev_b = None

    # Chercher l’appareil voisin (celui qui a l’interface "remote_intf")
    for d in devices_by_hostname.values():
        if hasattr(d.config, "interfaces") and remote_intf in d.config.interfaces:
            dev_b = d
            break

    if not dev_a or not dev_b:
        print(f"⚠️ Appareils introuvables pour {local_host} -> {remote_intf}")
        continue

    # Clé unique de lien (ordre trié pour éviter les doublons)
    key = tuple(sorted([
        (dev_a.hostname, local_intf),
        (dev_b.hostname, remote_intf)
    ]))

    if key in seen:
        continue

    seen.add(key)
    links.append(Link(dev_a, local_intf, dev_b, remote_intf))


# # Étape 3 : Injecter dans le fichier .pkt de base
builder = PktBuilder(base_template_path="src/resources/xml/empty.xml", devices=[s1,r1])
tree = builder.inject_devices()

# Étape 4 : Générer le fichier XML final
builder.generateXML(tree)

# Étape 5 : Générer le fichier .pkt
builder.generatePKT("src/resources/generated/generated1.xml")


print("✅ Fichier XML généré avec succès.")
