from graphviz import Graph
from src.topologie.TopologyLoader import TopologyLoader
from src.topologie.TopologyBuilder import TopologyBuilder
import os

IMG_DIR = os.path.abspath("src/resources/img")

def draw_network(devices, links, output_file="topologie", output_path="."):
    dot = Graph(comment="Topologie réseau", format='png')
    dot.attr(overlap='false')

    for dev in devices:
        img = ""  # Valeur par défaut si le type n'est pas reconnu

        # Définir l'image selon le type
        if dev.__class__.__name__ == "Router":
            img = os.path.join(IMG_DIR, "Router.png")
        elif dev.__class__.__name__ == "Switch":
            img = os.path.join(IMG_DIR, "Switch.png")
        else:
            img = ""

        # Définir la couleur selon l'état de config
        if getattr(dev, "notconfigured", False):
            color = 'red'
        elif dev.__class__.__name__ == "Router":
            color = 'lightblue'
        elif dev.__class__.__name__ == "Switch":
            color = 'lightgreen'
        else:
            color = 'grey'

        shape = 'ellipse' if dev.__class__.__name__ == "Router" else 'box'
        # Ajoute un label avec le statut si dispo
        label = dev.hostname
        if hasattr(dev, "statut"):
            label += f"\n(complet)"
        dot.node(dev.hostname, label='', shape=shape, style='filled', fillcolor=color, image=img, imagescale='true', width='0.7', height='0.3',xlabel=label)


    for link in links:
        # Récupère l'IP et le masque pour chaque extrémité
        iface_a = get_interface_by_name(link.device_a.interfaces, link.iface_a)
        iface_b = get_interface_by_name(link.device_b.interfaces, link.iface_b)
        ip_a = f"{iface_a.ip}/{iface_a.subnet_mask}" if iface_a and getattr(iface_a, 'ip', None) else ""
        ip_b = f"{iface_b.ip}/{iface_b.subnet_mask}" if iface_b and getattr(iface_b, 'ip', None) else ""

        # Prépare le label avec les IPs
        label = f"{link.iface_a} ({ip_a})\n{link.iface_b} ({ip_b})"
        # Style du lien selon le type de câble
        style = 'dashed' if link.cable_type == 'eCrossOver' else 'solid'

        dot.edge(link.device_a.hostname, link.device_b.hostname, label=label, style=style)


    dot.render(f"{output_path}/{output_file}", cleanup=True, format='png')
    output_file = f"{output_path}/{output_file}"
    # Affiche le message de succès
    print(f"Diagramme généré : {output_file}.png")


def get_interface_by_name(interfaces, name):
    # interfaces peut être un dict ou une liste
    if isinstance(interfaces, dict):
        return interfaces.get(name)
    else:
        for intf in interfaces:
            if intf.name.lower() == name.lower():
                return intf
    return None


main = __name__ == "__main__"

if main:
    # Exemple d'utilisation
            # Demander dynamiquement à l'utilisateur le dossier :
    folder = input("Entrez le chemin du dossier de configs : ").strip()
    folder = folder if folder else "/Users/chiba/Desktop/TB/configExtract/src/data/config/reseau12"
    parsed_devices, neighbors = TopologyLoader.load_config_from_folder(folder)
    devices = TopologyBuilder.create_devices(parsed_devices)
    links = TopologyBuilder.build_links(devices, neighbors)

    
    draw_network(devices, links, output_file="topologie_reseau")
else:
    print("Module importé, pas d'exécution directe.")