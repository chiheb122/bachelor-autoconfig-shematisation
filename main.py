from topologie.converter.parser_config import parse_config_to_json
from topologie.draw.pkt_generator import generate_pkt
import json

# Étape 1 : Lire et parser la configuration texte d’un routeur (type show run)
parsed = parse_config_to_json("config/router1.txt")

# Étape 2 : Vérification visuelle du JSON généré
print(json.dumps(parsed, indent=2))

# Étape 3 : Préparation du format attendu par generate_pkt()
config = {
    "devices": [
        {
            "type": "router",
            "hostname": parsed["hostname"],
            "interfaces": parsed["interfaces"],
            "position": (100, 200)  # position initiale (modifiable dynamiquement plus tard)
        }
    ]
}

# Étape 4 : Génération du fichier XML final (prêt à encoder en .pkt)
generate_pkt(config, output_path="resources/xml/generated.xml")

print("✅ Fichier XML généré avec succès.")
