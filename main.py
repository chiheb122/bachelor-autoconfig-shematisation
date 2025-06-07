from models.Router import Router
from topologie.converter.parser_config import parse_config_to_json
from topologie.draw.PktBuilder import PktBuilder
from topologie.draw.pkt_generator import generate_pkt
import json


# Étape 1 : Lire et parser la configuration texte d’un routeur (type show run)
parsed = parse_config_to_json("config/router1.txt")

print(parsed)
# Étape 2 : Créer l'objet Router
r1 = Router(macAdresse="00:11:22:33:44:55", hostname=parsed["hostname"])
r1.load_router()  # charge le template XML


# Étape 3 : Injecter dans le fichier .pkt de base
builder = PktBuilder(base_template_path="resources/xml/empty.xml", devices=[r1])
tree = builder.inject_devices()

# Étape 4 : Générer le fichier final
builder.generateXML(tree)

# Étape 5 : Générer le fichier final en pkt
builder.generatePKT("generated1.xml")









# Étape 2 : Vérification visuelle du JSON généré
print(json.dumps(parsed, indent=2))

# # Étape 3 : Préparation du format attendu par generate_pkt()
# config = {
#     "devices": [
#         {
#             "type": "router",
#             "hostname": parsed["hostname"],
#             "interfaces": parsed["interfaces"],
#             "position": (100, 200)  # position initiale (modifiable dynamiquement plus tard)
#         }
#     ]
# }

# # Étape 4 : Génération du fichier XML final (prêt à encoder en .pkt)
# generate_pkt(config, output_path="resources/xml/generated.xml")

print("✅ Fichier XML généré avec succès.")
