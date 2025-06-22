from src.models.factory.DeviceFactory import DeviceFactory
from src.topologie.converter.parser_config import parse_cdp_neighbors, parse_config_to_json,read_config_file
from src.topologie.draw.PktBuilder import PktBuilder
import re
from src.models.Link import Link

# Étape 1 : Lire et parser les configurations
parsed_router = parse_config_to_json("src/data/config/R0.txt")
parsed_switch = parse_config_to_json("src/data/config/switch.txt")

# Charge le fichier brut
lines = read_config_file("src/data/config/R1.txt")
lines2 = read_config_file("src/data/config/R0.txt")


print(parsed_router)
# Étape 2 : Créer les objets via la factory
r1 = DeviceFactory.create_device(parsed_router["type"], parsed_router["mac"], parsed_router["name"], parsed_router["raw"])
s1 = DeviceFactory.create_device(parsed_switch["type"], parsed_switch["mac"], parsed_switch["name"], parsed_switch["raw"])
# 1. Ajout des interfaces
for intf in parsed_router["config"]["interfaces"].values():
    r1.add_interface(intf)
for intf in parsed_switch["config"]["interfaces"].values():
    s1.add_interface(intf)

# Charger les templates XML
r1.load_router()
s1.load_switch()

parsedcdp = parse_cdp_neighbors("src/data/config/cdpsw.txt")
print(parsedcdp)
# 2. Création des liens après que tous les mem_addr soient attribués


def is_vlan_subinterface(interface: str) -> bool:
    """
    Retourne True si l'interface est une sous-interface de type VLAN.
    Ex : GigabitEthernet0/1.10 → True ; FastEthernet0/0 → False
    """
    return bool(re.search(r'/\d+\.\d+$', interface))
seen = set()
links = []

for entry in parsedcdp:
    port = entry["port_id"]

    if is_vlan_subinterface(port):
        continue

    dev_b = r1 if entry["device_id"] == r1.hostname else s1
    dev_a = s1 if dev_b is r1 else r1

    # Clé unique représentant le lien
    key = tuple(sorted([
        (dev_a.hostname, entry["local_interface"]),
        (dev_b.hostname, entry["port_id"])
    ]))

    if key in seen:
        continue
    seen.add(key)

    links.append(Link(dev_a, entry["local_interface"], dev_b, entry["port_id"]))

print(links)
# # 3. Utilisation des liens
# for link in links:
#     print(link.to_xml())  # Ou ajoute au XML global


# # Étape 3 : Injecter dans le fichier .pkt de base
builder = PktBuilder(base_template_path="src/resources/xml/empty.xml", devices=[r1, s1], links=links)
tree = builder.inject_devices()

# Étape 4 : Générer le fichier XML final
builder.generateXML(tree)

# Étape 5 : Générer le fichier .pkt
builder.generatePKT("src/resources/generated/generated1.xml")

# # Vérification visuelle du JSON généré
# print(json.dumps(parsed_router, indent=2))
# print(json.dumps(parsed_switch, indent=2))

print("✅ Fichier XML généré avec succès.")
