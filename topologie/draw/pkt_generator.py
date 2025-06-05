import xml.etree.ElementTree as ET  # Librairie standard pour manipuler du XML en Python
import copy  # Permet de dupliquer un objet (deepcopy pour dupliquer entièrement un arbre XML)

# ─────────────────────────────────────────────────────────────────────
# Fonction : load_router
# But : Charger le modèle de routeur (fichier XML contenant un seul <DEVICE>)
def load_router():
    root = ET.parse("resources/xml/router.xml").getroot()
    print(root.tag)
    return root


# Fonction : load_switch
# But : Charger le modèle de switch (similaire à load_router)
def load_switch():
    return ET.parse("resources/xml/switch.xml").getroot().find("DEVICE")


# Fonction : load_base
# But : Charger le fichier de base (2.xml), qui ne contient que la structure du fichier .pkt sans DEVICE
def load_base():
    tree = ET.parse("resources/xml/2.xml")
    root = tree.getroot()
    return tree, root  # On retourne à la fois l'arbre complet (pour l'enregistrement) et la racine (pour injection)


# ─────────────────────────────────────────────────────────────────────
# Fonction : inject_router
# But : Injecter un nouveau routeur dans la base XML à partir du modèle
# Arguments :
#   - root : racine de l'arbre XML de base
#   - router_template : le modèle de routeur chargé depuis router.xml
#   - hostname : nom à donner au routeur
#   - ip_conf : liste de dictionnaires avec adresse IP, masque et statut pour chaque interface
#   - coords : position X, Y à placer dans le workspace graphique
def inject_router(root, router_template, hostname, ip_conf, coords):
    router = copy.deepcopy(router_template)  # On duplique le modèle pour pouvoir le modifier

    # Modifier le nom du routeur
    router.find(".//NAME").text = hostname

    # Injecter les informations d’interface
    # for i, iface in enumerate(ip_conf):
    #     port = router.findall(".//PORT")[i]  # On suppose que l’ordre des ports dans le XML correspond à l’ordre dans ip_conf
    #     port.find("IP").text = iface["ip"]
    #     #port.find("SUBNET").text = iface["mask"]
    #     port.find("POWER").text = "true" if iface["status"] == "up" else "false"

    devices_node = root.find(".//DEVICES")
    if devices_node is None:
        raise ValueError("❌ Aucun bloc <DEVICES> trouvé dans la base XML")
    # Ajouter le routeur modifié à la racine du document
    devices_node.append(router)




# ─────────────────────────────────────────────────────────────────────
# Fonction : generate_pkt
# But : Fonction principale orchestrant la génération du XML final prêt à être converti en .pkt
# Argument :
#   - config : dictionnaire contenant la configuration du réseau (nom, interfaces, position, etc.)
#   - output_path : nom du fichier XML de sortie (par défaut "generated.xml")
def generate_pkt(config, output_path="generated.xml"):
    # Charger la structure de base du fichier pkt (sans appareils)
    tree, root = load_base()

    # Parcourir les appareils définis dans la configuration
    for device in config["devices"]:
        if device["type"] == "router":
            inject_router(
                root,
                load_router(),  # charger modèle de routeur
                hostname=device["hostname"],
                ip_conf=device["interfaces"],
                coords=device.get("position", (100, 100))  # position par défaut si non spécifiée
            )
        # TODO : Ajouter "elif device['type'] == 'switch'" ici pour gérer les switches
    print("[DEBUG] type(tree):", type(tree))
    print("[DEBUG] type(output_path):", type(output_path))
    print("[DEBUG] output_path value:", output_path)

    # Écrire le fichier XML final prêt à être converti avec pka2xml
    tree.write(output_path, encoding="utf-8", xml_declaration=True)
