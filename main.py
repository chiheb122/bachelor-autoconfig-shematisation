from models.factory.DeviceFactory import DeviceFactory
from topologie.converter.parser_config import parse_cdp_neighbors, parse_config_to_json
from topologie.draw.PktBuilder import PktBuilder
import json
from models.Link import Link
# Étape 1 : Lire et parser les configurations
parsed_router = parse_config_to_json("config/router1.txt")
parsed_switch = parse_config_to_json("config/switch.txt")

# print(parsed_router)
# print(parsed_router["name"])
# Étape 2 : Créer les objets via la factory
r1 = DeviceFactory.create_device(parsed_router["type"], parsed_router["mac"], parsed_router["name"], parsed_router["config"])
s1 = DeviceFactory.create_device(parsed_switch["type"], parsed_switch["mac"], parsed_switch["name"], parsed_switch["config"])
# 1. Ajout des interfaces
for intf in parsed_router["config"]["interfaces"]:
    r1.add_interface(intf)
for intf in parsed_switch["config"]["interfaces"]:
    s1.add_interface(intf)

# Charger les templates XML
r1.load_router()
s1.load_switch()

parsedcdp = parse_cdp_neighbors("config/cdpsw.txt")
print(parsedcdp)
# 2. Création des liens après que tous les mem_addr soient attribués

# links = []
# for entry in parsedcdp:
#     # On suppose que device_id est le voisin, donc dev_b
#     dev_b = r1 if entry["device_id"] == r1.hostname else s1
#     dev_a = s1 if dev_b is r1 else r1  # l'autre device
#     links.append(Link(dev_a, entry["local_interface"], dev_b, entry["port_id"]))

# # 3. Utilisation des liens
# for link in links:
#     print(link.to_xml())  # Ou ajoute au XML global


# # Étape 3 : Injecter dans le fichier .pkt de base
# builder = PktBuilder(base_template_path="resources/xml/empty.xml", devices=[r1, s1], links=links)
# tree = builder.inject_devices()

# # Étape 4 : Générer le fichier XML final
# builder.generateXML(tree)

# Étape 5 : Générer le fichier .pkt
builder.generatePKT("generated1.xml")

# # Vérification visuelle du JSON généré
# print(json.dumps(parsed_router, indent=2))
# print(json.dumps(parsed_switch, indent=2))

print("✅ Fichier XML généré avec succès.")
