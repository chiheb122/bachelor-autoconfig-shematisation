from graphviz import Graph
from jinja2 import Environment, FileSystemLoader
import json
import os

IMG_DIR = os.path.abspath("src/resources/img")

class GraphvizRender:
    def __init__(self, devices, links, output_file="topologie", output_path=".", responsellm=None):
        self.devices = devices
        self.links = links
        self.output_file = output_file
        self.output_path = output_path
        self.responsellm = responsellm

    def draw_network(self):
        dot = Graph(comment="Topologie réseau", format='png')
        dot.attr(overlap='false')

        for dev in self.devices:
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


        for link in self.links:
            # Récupère l'IP et le masque pour chaque extrémité
            iface_a = self.get_interface_by_name(link.device_a.interfaces, link.iface_a)
            iface_b = self.get_interface_by_name(link.device_b.interfaces, link.iface_b)
            ip_a = f"{iface_a.ip}/{iface_a.subnet_mask}" if iface_a and getattr(iface_a, 'ip', None) else ""
            ip_b = f"{iface_b.ip}/{iface_b.subnet_mask}" if iface_b and getattr(iface_b, 'ip', None) else ""

            # Prépare le label avec les IPs
            label = f"{link.iface_a} ({ip_a})\n{link.iface_b} ({ip_b})"
            # Style du lien selon le type de câble
            style = 'dashed' if link.cable_type == 'eCrossOver' else 'solid'

            dot.edge(link.device_a.hostname, link.device_b.hostname, label=label, style=style)


        dot.render(f"{self.output_path}/{self.output_file}", cleanup=True, format='png')
        print(f"Diagramme généré : {self.output_path}/{self.output_file}.png")


    def get_interface_by_name(self, interfaces, name):
        # interfaces peut être un dict ou une liste
        if isinstance(interfaces, dict):
            return interfaces.get(name)
        else:
            for intf in interfaces:
                if intf.name.lower() == name.lower():
                    return intf
        return None

    def generate_html_report(self):
            # Récupère le chemin absolu du dossier contenant le script
            BASE_DIR = os.path.dirname(os.path.abspath(__file__))
            TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")

            env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
            template = env.get_template('template.html')
            output = template.render(devices=self.responsellm, output_file=self.output_file)

            # Sauvegarde le résultat
            with open(os.path.join(self.output_path, "network_report.html"), "w") as f:
                f.write(output)


