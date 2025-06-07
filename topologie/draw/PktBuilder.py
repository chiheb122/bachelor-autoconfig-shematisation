from models.Switch import Switch
from models.Device import Device
from models.Router import Router 
import xml.etree.ElementTree as ET
import sys
sys.path.append("lib/pka2xml_py")
import pka2core #type: ignore
from topologie.converter.pkt2xml import encrypt_xml_to_pkt  # Librairie standard pour manipuler du XML en Python


class PktBuilder:

    def __init__(self,base_template_path:str,devices:list[Device]): # type: ignore
        self.base_template:str = base_template_path
        self.devices:devices[Device] = devices # type: ignore

    # Fonction : load_base
    # But : Charger le fichier de base (2.xml), qui ne contient que la structure du fichier .pkt sans DEVICE
    def load_base(self):
        tree = ET.parse("resources/xml/empty.xml")
        root = tree.getroot()
        return tree, root  # On retourne à la fois l'arbre complet (pour l'enregistrement) et la racine (pour injection)


    def inject_devices(self):
        # Charger la structure de base du fichier pkt (sans appareils)
        tree, root = self.load_base()
        devices_node = root.find(".//DEVICES")
        if devices_node is None:
            raise ValueError("❌ Aucun bloc <DEVICES> trouvé dans la base XML")
        for device in self.devices:
            if isinstance(device, Router):
                # Ajouter le routeur modifié à la racine du document
                router_xml = device.parseXml()
                devices_node.append(router_xml)
            elif isinstance(device, Switch):
                # Ajouter le routeur modifié à la racine du document
                switch_xml = device.parseXml()
                devices_node.append(switch_xml)
            else:
                print(f"⚠️ Type d'appareil non pris en charge : {type(device)}")
     
        return tree  # Pour éventuellement sauvegarder ensuite via tree.write(...)
    

    def generateXML(self,tree, output_path="generated1.xml"):
        """
        Écrit l'arbre XML complet dans un fichier.
        """
        for elem in tree.getroot().iter():
            if isinstance(elem.text, dict):
                print(f"❌ ERREUR: dict trouvé dans .text pour <{elem.tag}> : {elem.text}")
        tree.write(output_path, encoding="utf-8", xml_declaration=True)
        print(f"✅ Fichier généré avec succès : {output_path}")

    def generatePKT(self, xml_path: str, output_path="generated.pkt"):
        try:
            pkt_bytes = encrypt_xml_to_pkt(xml_path)
            with open(output_path, "wb") as f:
                f.write(pkt_bytes)
            print(f"✅ Fichier .pkt généré avec succès : {output_path}")
        except Exception as e:
            print(f"❌ Erreur lors du chiffrement du fichier XML : {e}")


        